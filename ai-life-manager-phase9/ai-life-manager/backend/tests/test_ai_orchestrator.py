"""
Tests for the AI orchestrator.

The Anthropic client is faked with plain duck-typed objects matching
the shape the orchestrator actually reads (`response.stop_reason`,
`block.type`/`.text`/`.name`/`.input`/`.id`) — no real API key or
network call needed, while tool execution itself runs for real
through the in-process MCP server, so the tool-call loop is genuinely
exercised end-to-end.
"""

import pytest
from fastmcp import Client

from app.mcp.server import mcp
from app.services.ai_orchestrator import MAX_TOOL_ROUNDS, AIOrchestrator
from app.services.fallback_intent import match_intent
from app.services.tool_bridge import get_anthropic_tools

import app.mcp.prompts  # noqa: F401,E402
import app.mcp.resources  # noqa: F401,E402
import app.mcp.tools  # noqa: F401,E402


class FakeBlock:
    def __init__(self, type, **kwargs):
        self.type = type
        for key, value in kwargs.items():
            setattr(self, key, value)


class FakeResponse:
    def __init__(self, stop_reason, content):
        self.stop_reason = stop_reason
        self.content = content


class FakeMessagesAPI:
    def __init__(self, responses):
        self._responses = list(responses)
        self._index = 0

    async def create(self, **kwargs):
        response = self._responses[self._index]
        self._index += 1
        return response


class FakeAnthropicClient:
    def __init__(self, responses):
        self.messages = FakeMessagesAPI(responses)


# ---------- Tool schema bridge ----------


@pytest.mark.asyncio
async def test_get_anthropic_tools_includes_expected_tools():
    async with Client(mcp) as client:
        tools = await get_anthropic_tools(client)
    names = {t["name"] for t in tools}
    assert "add_expense" in names
    assert "ping" in names

    ping_tool = next(t for t in tools if t["name"] == "ping")
    assert ping_tool["input_schema"]["type"] == "object"
    assert "description" in ping_tool


# ---------- Fallback intent matcher (unit-level, no orchestrator) ----------


def test_match_intent_add_expense():
    intent = match_intent("I spent 250 on food")
    assert intent == {"tool": "add_expense", "arguments": {"amount": 250.0, "category": "Food"}}


def test_match_intent_weekly_summary():
    intent = match_intent("how much did I spend this week?")
    assert intent["tool"] == "compare_weekly_expenses"


def test_match_intent_overdue_reminders():
    intent = match_intent("what are my overdue reminders")
    assert intent["tool"] == "list_reminders"
    assert intent["arguments"] == {"when": "overdue"}


def test_match_intent_no_match():
    assert match_intent("tell me a joke about penguins") is None


# ---------- Full orchestrator: LLM tool-call loop (faked model, real tool execution) ----------


@pytest.mark.asyncio
async def test_orchestrator_executes_tool_and_returns_final_text(test_user_id):
    responses = [
        FakeResponse("tool_use", [FakeBlock("tool_use", id="call_1", name="ping", input={})]),
        FakeResponse("end_turn", [FakeBlock("text", text="All systems are online!")]),
    ]
    orchestrator = AIOrchestrator(anthropic_client=FakeAnthropicClient(responses))

    result = await orchestrator.handle_message(user_id=test_user_id, message="ping the server")

    assert result["used_fallback"] is False
    assert result["tools_called"] == ["ping"]
    assert result["response"] == "All systems are online!"


@pytest.mark.asyncio
async def test_orchestrator_executes_real_add_expense_tool(test_user_id):
    responses = [
        FakeResponse(
            "tool_use",
            [
                FakeBlock(
                    "tool_use",
                    id="call_1",
                    name="add_expense",
                    input={"user_id": test_user_id, "amount": 250, "category": "Food"},
                )
            ],
        ),
        FakeResponse("end_turn", [FakeBlock("text", text="Added ₹250 under Food.")]),
    ]
    orchestrator = AIOrchestrator(anthropic_client=FakeAnthropicClient(responses))

    result = await orchestrator.handle_message(user_id=test_user_id, message="I spent 250 on food")

    assert result["tools_called"] == ["add_expense"]
    assert "250" in result["response"]

    # Confirm the expense was actually written via the real MCP tool, not mocked.
    async with Client(mcp) as client:
        check = await client.call_tool("get_expenses", {"user_id": test_user_id, "category": "Food"})
        assert check.data["count"] >= 1


@pytest.mark.asyncio
async def test_orchestrator_falls_back_when_tool_loop_never_terminates(test_user_id):
    # Every round returns tool_use, never end_turn — should exceed
    # MAX_TOOL_ROUNDS, raise internally, and fall back gracefully
    # rather than hanging or crashing.
    responses = [
        FakeResponse("tool_use", [FakeBlock("tool_use", id=f"call_{i}", name="ping", input={})])
        for i in range(MAX_TOOL_ROUNDS + 2)
    ]
    orchestrator = AIOrchestrator(anthropic_client=FakeAnthropicClient(responses))

    result = await orchestrator.handle_message(user_id=test_user_id, message="gibberish that matches no fallback pattern")

    assert result["used_fallback"] is True
    assert result["tools_called"] == []


# ---------- Fallback path (no Anthropic client configured at all) ----------


@pytest.mark.asyncio
async def test_handle_message_falls_back_without_api_key(test_user_id):
    # No injected client, and ANTHROPIC_API_KEY is unset in the test
    # environment — _build_anthropic_client() should raise, triggering fallback.
    orchestrator = AIOrchestrator()
    result = await orchestrator.handle_message(user_id=test_user_id, message="I spent 100 on transportation")

    assert result["used_fallback"] is True
    assert result["tools_called"] == ["add_expense"]
    assert "Transportation" in result["response"]


@pytest.mark.asyncio
async def test_handle_message_fallback_unmatched_message(test_user_id):
    orchestrator = AIOrchestrator()
    result = await orchestrator.handle_message(user_id=test_user_id, message="what's the meaning of life")

    assert result["used_fallback"] is True
    assert result["tools_called"] == []
    assert "trouble reaching" in result["response"]
