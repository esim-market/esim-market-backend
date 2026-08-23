from collections.abc import Mapping


class HistoryRepositoryMixin:
    """Optional, domain-neutral stream history helper."""

    async def append_history_message(self, session_id: str, category: str, data: Mapping[str, object]):
        return await self.append_stream_item(f"messages:{category}:{session_id}", dict(data))
