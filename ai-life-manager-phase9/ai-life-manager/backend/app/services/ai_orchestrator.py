"""
AI orchestrator: routes a user's natural-language message through
Claude (with MCP tools available) and returns the final response.

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

from anthropic import AsyncAnthropic
from fastmcp import Client

from app.config import get_settings
from app.mcp.server import mcp
from app.services.fallback_intent import match_intent
from app.services.tool_bridge import get_anthropic_tools

settings = get_settings()

MAX_TOOL_ROUNDS = 6

SYSTEM_PROMPT_TEMPLATE = """You are the AI Life Manager assistant — a personal assistant for expenses, budgets, reminders, and daily planning.

Today's date is {today}.
The current user's id is {user_id}. Always pass this exact value as the `user_id` argument for every tool call. Never ask the user for their user id, and never invent a different one.

Resolve relative dates and times ("tomorrow", "next Friday", "6pm") into explicit values yourself before calling a tool, using today's date above as the reference point — tools only accept explicit YYYY-MM-DD dates and HH:MM (24-hour) times.

If a tool result contains "success": false, explain the error to the user in plain language rather than retrying the same call blindly.

When presenting financial insights or spending analysis, be clear that these are informational observations based on the user's own recorded data, not financial advice.

Keep responses concise, warm, and conversational — you're a helpful assistant, not a report generator."""


class AIOrchestrator:
    def __init__(self, anthropic_client: AsyncAnthropic | None = None):
        # Injectable for testing — lets tests supply a fake client that
        # never makes a real network call, instead of needing a real
        # ANTHROPIC_API_KEY to exercise the tool-calling loop.
        self._injected_anthropic = anthropic_client

    def _build_anthropic_client(self) -> AsyncAnthropic:
        if self._injected_anthropic is not None:
            return self._injected_anthropic
        if not settings.anthropic_api_key:
            raise RuntimeError("Anthropic API key is not configured.")
        return AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def handle_message(
        self, *, user_id: int, message: str, conversation_history: list[dict] | None = None
    ) -> dict:
        try:
            return await self._handle_with_llm(user_id=user_id, message=message, conversation_history=conversation_history)
        except Exception:
            # Anthropic API unreachable, unconfigured, rate-limited, or the
            # tool loop ran too long — fall back to deterministic matching
            # rather than surfacing a raw error to the user.
            return await self._handle_with_fallback(user_id=user_id, message=message)

    async def _handle_with_llm(
        self, *, user_id: int, message: str, conversation_history: list[dict] | None
    ) -> dict:
        anthropic_client = self._build_anthropic_client()
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(today=date.today().isoformat(), user_id=user_id)

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
                    "I'm having trouble reaching the AI assistant right now, so I can only handle a "
                    "few simple requests directly — try something like 'I spent 250 on food' or "
                    "'how much did I spend this week'."
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
        return f"I couldn't do that: {data.get('error', 'an unknown error occurred')}."

    if tool_name == "add_expense":
        expense = data["expense"]
        return f"Added {expense['amount']} under {expense['category']}."
    if tool_name == "compare_weekly_expenses":
        return (
            f"This week: {data['current_week']['total']}. "
            f"Last week: {data['previous_week']['total']}."
        )
    if tool_name == "list_reminders":
        count = data.get("count", 0)
        return f"You have {count} overdue reminder(s)." if count else "No overdue reminders — nice work!"
    return "Done."
