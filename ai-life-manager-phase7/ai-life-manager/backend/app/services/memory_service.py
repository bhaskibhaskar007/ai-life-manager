"""
Memory service layer: user preferences + conversation context.

The preference allow-list is the actual enforcement mechanism behind
"never store passwords or sensitive credentials" — `save_user_preference`
rejects any key not on this list outright, so there's no path for the
LLM to accidentally (or deliberately, via a crafted prompt) persist a
password, token, or other credential through this tool.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.context import ConversationContext
from app.models.preference import UserPreference
from app.repositories import context_repository, preference_repository

# Each entry: key -> short human-readable description (used in error
# messages so an invalid key request tells the caller what IS allowed).
ALLOWED_PREFERENCE_KEYS: dict[str, str] = {
    "currency": "preferred currency code, e.g. INR, USD",
    "reminder_style": "how reminders should be phrased, e.g. 'brief' or 'detailed'",
    "common_categories": "comma-separated list of frequently used expense categories",
    "dashboard_layout": "preferred dashboard widget arrangement",
    "voice_response_enabled": "whether spoken responses are preferred, 'true' or 'false'",
    "notification_style": "how the user prefers to be notified, e.g. 'email', 'push', 'none'",
    "timezone": "IANA timezone name, e.g. 'Asia/Kolkata'",
    "language": "preferred language code, e.g. 'en'",
}

MAX_CONTEXT_SUMMARY_LENGTH = 1000


def _serialize_preference(pref: UserPreference) -> dict:
    return {"key": pref.key, "value": pref.value, "updated_at": pref.updated_at.isoformat()}


def _serialize_context(ctx: ConversationContext) -> dict:
    return {"id": ctx.id, "summary": ctx.summary, "created_at": ctx.created_at.isoformat()}


class MemoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_user_preference(self, *, user_id: int, key: str, value: str) -> dict:
        normalized_key = key.strip().lower()
        if normalized_key not in ALLOWED_PREFERENCE_KEYS:
            valid = ", ".join(ALLOWED_PREFERENCE_KEYS)
            raise ValueError(f"'{key}' is not a supported preference. Supported keys: {valid}")
        if not value or not str(value).strip():
            raise ValueError("Preference value cannot be empty.")
        if len(str(value)) > 500:
            raise ValueError("Preference value is too long (500 characters max).")

        pref = await preference_repository.upsert_preference(self.session, user_id, normalized_key, str(value).strip())
        return _serialize_preference(pref)

    async def get_user_preference(self, *, user_id: int, key: str) -> dict:
        pref = await preference_repository.get_preference(self.session, user_id, key.strip().lower())
        if pref is None:
            return {"found": False, "key": key, "value": None}
        return {"found": True, **_serialize_preference(pref)}

    async def list_user_preferences(self, *, user_id: int) -> list[dict]:
        prefs = await preference_repository.list_preferences(self.session, user_id)
        return [_serialize_preference(p) for p in prefs]

    async def save_user_context(self, *, user_id: int, summary: str) -> dict:
        if not summary or not summary.strip():
            raise ValueError("Context summary cannot be empty.")
        if len(summary) > MAX_CONTEXT_SUMMARY_LENGTH:
            raise ValueError(f"Context summary is too long ({MAX_CONTEXT_SUMMARY_LENGTH} characters max).")

        context = await context_repository.create_context(self.session, user_id, summary.strip())
        return _serialize_context(context)

    async def retrieve_relevant_context(self, *, user_id: int, query: str | None = None, limit: int = 5) -> list[dict]:
        if limit < 1 or limit > 20:
            raise ValueError("limit must be between 1 and 20.")

        if query and query.strip():
            results = await context_repository.search_context(self.session, user_id, query.strip(), limit)
        else:
            results = await context_repository.list_recent_context(self.session, user_id, limit)
        return [_serialize_context(c) for c in results]
