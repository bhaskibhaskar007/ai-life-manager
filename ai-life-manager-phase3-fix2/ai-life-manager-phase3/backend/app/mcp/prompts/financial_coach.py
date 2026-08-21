"""
MCP prompts — reusable instruction templates any MCP host can fetch,
not just Python string constants baked into our own AI layer. This is
what keeps "how should the assistant phrase a financial insight"
portable to other MCP hosts (Claude Desktop, etc.), per the spec's
requirement to demonstrate MCP prompts as a first-class concept.
"""

from app.mcp.server import mcp


@mcp.prompt
def financial_coach_prompt(spending_change_percent: float, top_category: str) -> str:
    """
    Prompt template for turning raw analytics numbers into a
    plain-language financial insight. Called with real numbers from
    `generate_financial_insight` (Phase 6) — never fabricated ones.
    """
    direction = "increased" if spending_change_percent >= 0 else "decreased"
    return (
        f"The user's spending has {direction} by {abs(spending_change_percent):.1f}% "
        f"compared with the previous week, with '{top_category}' as the largest "
        "contributing category. Explain this to the user in one or two friendly, "
        "plain-language sentences. State it as informational observation, not "
        "financial advice. Do not invent numbers beyond what was given."
    )
