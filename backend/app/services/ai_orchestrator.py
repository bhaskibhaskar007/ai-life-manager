"""
AI orchestrator: routes a user's natural-language message through
the AI agent (with MCP tools available) and returns the final response.

This is the ONLY place an LLM's tool_use requests get executed — and
even here, execution goes through the exact same MCP `Client.call_tool`
path as everywhere else, so the "LLM never writes to the database
directly" rule holds: the LLM can only ask for a named, schema-validated
tool to run; it never gets a raw DB connection or arbitrary code
execution.
"""

import json
from datetime import date
from typing import Any

from fastmcp import Client

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.mcp.server import mcp
from app.services.fallback_intent import match_intent
from app.services.memory_service import MemoryService
from app.services.tool_bridge import get_anthropic_tools

settings = get_settings()

MAX_TOOL_ROUNDS = 6

SYSTEM_PROMPT_TEMPLATE = """You are AI Life Manager — an intelligent, context-aware personal AI assistant.
You help users seamlessly manage their daily productivity, personal expenses, budgets, reminders, schedule planning, and weather-aware routines.

Today's date is {today}.
The current user's id is {user_id}. Always pass this exact value as the `user_id` argument for every tool call. Never ask the user for their user id, and never invent a different one.

User context & preferences:
{user_context}

Available capabilities via MCP tools:
1. Expenses: Record, list, update, delete, summarize, and categorize transactions.
2. Analytics: Compare weekly spending, analyze trends, compute percentage changes, and detect anomalies.
3. Reminders: Schedule, list (today/tomorrow/overdue/upcoming), update, complete, and delete reminders.
4. Budgets: Monitor monthly and category budgets, calculate remaining limits, and check for overspending risks.
5. Day Planner: Generate an organized, time-blocked daily schedule based on active reminders, weather forecasts, and daily budget limits.
6. Weather: Fetch live conditions and multi-day forecasts for weather-aware planning (e.g. rain/umbrella alerts).
7. Memory: Store and retrieve non-sensitive user preferences and context.

Rules:
- Resolve relative dates ("tomorrow", "next Monday", "6 PM") to ISO YYYY-MM-DD and HH:MM before tool execution.
- All database modifications MUST happen via standard MCP tool calls. Never invent or hallucinate data.
- When presenting financial observations or spending trends, make it clear that they are informational summaries based on recorded data, not financial advice.
- Keep responses concise, helpful, friendly, and structured."""


class AIOrchestrator:
    def __init__(self, anthropic_client: Any | None = None):
        self._injected_anthropic = anthropic_client

    def _build_anthropic_client(self) -> Any:
        if self._injected_anthropic is not None:
            return self._injected_anthropic
        if not settings.anthropic_api_key:
            raise RuntimeError("Anthropic API key is not configured.")
        try:
            from anthropic import AsyncAnthropic
            return AsyncAnthropic(api_key=settings.anthropic_api_key)
        except ImportError:
            raise RuntimeError("Anthropic client library is not installed.")

    async def handle_message(
        self, *, user_id: int, message: str, conversation_history: list[dict] | None = None
    ) -> dict:
        try:
            return await self._handle_with_llm(user_id=user_id, message=message, conversation_history=conversation_history)
        except Exception:
            # LLM unreachable, unconfigured, or timed out — fall back to deterministic matching
            return await self._handle_with_fallback(user_id=user_id, message=message)

    async def _handle_with_llm(
        self, *, user_id: int, message: str, conversation_history: list[dict] | None
    ) -> dict:
        anthropic_client = self._build_anthropic_client()

        # Retrieve user context & preferences
        user_context_str = "No specific preferences recorded yet."
        try:
            async with AsyncSessionLocal() as session:
                mem_svc = MemoryService(session)
                prefs = await mem_svc.list_user_preferences(user_id=user_id)
                if prefs:
                    user_context_str = ", ".join(f"{p['key']}={p['value']}" for p in prefs)
        except Exception:
            pass

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            today=date.today().isoformat(),
            user_id=user_id,
            user_context=user_context_str,
        )

        async with Client(mcp) as mcp_client:
            anthropic_tools = await get_anthropic_tools(mcp_client)
            messages: list[dict[str, Any]] = list(conversation_history or [])
            messages.append({"role": "user", "content": message})

            tools_called: list[str] = []

            for _ in range(MAX_TOOL_ROUNDS):
                response = await anthropic_client.messages.create(
                    model=settings.anthropic_model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=messages,
                    tools=anthropic_tools,
                )

                if response.stop_reason != "tool_use":
                    final_text = "".join(
                        block.text for block in response.content if getattr(block, "type", None) == "text"
                    )
                    # Persist conversation context asynchronously
                    try:
                        async with AsyncSessionLocal() as session:
                            mem_svc = MemoryService(session)
                            await mem_svc.save_user_context(
                                user_id=user_id,
                                summary=f"User: {message[:100]} | Assistant: {final_text[:100]}",
                            )
                    except Exception:
                        pass

                    return {"response": final_text, "used_fallback": False, "tools_called": tools_called}

                messages.append({"role": "assistant", "content": response.content})
                tool_result_blocks = []
                for block in response.content:
                    if getattr(block, "type", None) == "tool_use":
                        tools_called.append(block.name)
                        tool_result = await mcp_client.call_tool(block.name, block.input)
                        tool_result_blocks.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(tool_result.data, default=str),
                            }
                        )
                messages.append({"role": "user", "content": tool_result_blocks})

            raise RuntimeError("Too many tool-call rounds without a final response.")

    async def _handle_with_fallback(self, *, user_id: int, message: str) -> dict:
        intent = match_intent(message)
        if intent is None:
            return {
                "response": (
                    "I am ready to help! You can say things like:\n"
                    "• 'I spent ₹250 on food today'\n"
                    "• 'How much did I spend this week?'\n"
                    "• 'Compare my spending with last week'\n"
                    "• 'Which category am I spending the most on?'\n"
                    "• 'Plan my day'\n"
                    "• 'Remind me to submit assignment tomorrow at 6 PM'\n"
                    "• 'Do I need an umbrella today?'"
                ),
                "used_fallback": True,
                "tools_called": [],
            }

        async with Client(mcp) as mcp_client:
            arguments = {"user_id": user_id, **intent["arguments"]}
            result = await mcp_client.call_tool(intent["tool"], arguments)

        return {
            "response": _summarize_fallback_result(intent["tool"], result.data),
            "used_fallback": True,
            "tools_called": [intent["tool"]],
        }


def _summarize_fallback_result(tool_name: str, data: dict) -> str:
    if not data.get("success", True):
        return f"Unable to complete request: {data.get('error', 'an unexpected error occurred')}."

    if tool_name == "add_expense":
        exp = data.get("expense", {})
        return f"Successfully added expense of ₹{exp.get('amount')} under category '{exp.get('category')}'. Description: {exp.get('description', 'N/A')}."

    if tool_name == "compare_weekly_expenses":
        curr = data.get("current_week", {}).get("total", 0)
        prev = data.get("previous_week", {}).get("total", 0)
        pct = data.get("change_percent")
        trend_msg = f" ({pct:+.1f}% change)" if pct is not None else ""
        return f"This week: ₹{curr} | Previous week: ₹{prev}{trend_msg}."

    if tool_name == "get_category_breakdown":
        top = data.get("top_category", "None")
        cats = data.get("categories", [])
        cat_summary = ", ".join(f"{c['category']}: ₹{c['total']}" for c in cats[:3])
        return f"Top spending category: {top}. Breakdown: {cat_summary or 'No expenses recorded'}."

    if tool_name == "generate_financial_insight":
        return data.get("insight_text", "Financial analysis updated.")

    if tool_name == "calculate_remaining_budget":
        spent = data.get("spent", 0)
        rem = data.get("remaining", 0)
        pct = data.get("percentage_used", 0)
        status = data.get("status", "on_track")
        return f"Budget status: {status.upper()}. Spent ₹{spent} ({pct}%), remaining: ₹{rem}."

    if tool_name == "create_reminder":
        rem = data.get("reminder", data)
        return f"Reminder set: '{rem.get('title')}' due on {rem.get('due_date')} at {rem.get('due_time') or 'all day'}."

    if tool_name == "list_reminders":
        count = data.get("count", len(data.get("reminders", [])))
        rems = data.get("reminders", [])
        if not count:
            return "No pending reminders found. You are all caught up!"
        items = "; ".join(f"• {r.get('title')} ({r.get('due_date')})" for r in rems[:3])
        return f"You have {count} reminder(s): {items}."

    if tool_name == "get_current_weather":
        w = data.get("weather", {})
        rain = " Rain is expected — carry an umbrella!" if w.get("rain_expected") else " No rain expected."
        return f"Current weather in {w.get('location', 'your area')}: {w.get('temperature_celsius')}°C, {w.get('conditions')}.{rain}"

    if tool_name == "plan_day":
        p = data.get("plan", {})
        count = p.get("reminders_count", 0)
        blocks = p.get("schedule_blocks", [])
        notes = p.get("notes", "")
        summary_blocks = " | ".join(f"{b['period']}: {len(b['items'])} item(s)" for b in blocks)
        return f"Day Plan for {p.get('date')}: {count} scheduled reminder(s). {summary_blocks}. {notes}"

    return "Request completed successfully."
