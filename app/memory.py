from collections import defaultdict
from typing import List, Dict
import time
from app.config import settings


class ConversationMemory:
    """
    Manages in-memory chat history per WhatsApp contact.
    """

    def __init__(self, max_messages: int = 12, ttl_seconds: int = 3600 * 6):
        self.max_messages = max_messages
        self.ttl_seconds = ttl_seconds
        # dict of chatId -> {"last_active": timestamp, "messages": [{"role": "user"|"assistant", "content": "..."}]}
        self._history: Dict[str, Dict] = defaultdict(lambda: {"last_active": time.time(), "messages": []})

    def get_messages(self, chat_id: str) -> List[Dict[str, str]]:
        self._cleanup_if_expired(chat_id)
        return list(self._history[chat_id]["messages"])

    def add_user_message(self, chat_id: str, content: str):
        self._cleanup_if_expired(chat_id)
        self._history[chat_id]["last_active"] = time.time()
        self._history[chat_id]["messages"].append({"role": "user", "content": content})
        self._truncate(chat_id)

    def add_assistant_message(self, chat_id: str, content: str):
        self._history[chat_id]["last_active"] = time.time()
        self._history[chat_id]["messages"].append({"role": "assistant", "content": content})
        self._truncate(chat_id)

    def clear(self, chat_id: str):
        if chat_id in self._history:
            del self._history[chat_id]

    def _truncate(self, chat_id: str):
        msgs = self._history[chat_id]["messages"]
        if len(msgs) > self.max_messages:
            self._history[chat_id]["messages"] = msgs[-self.max_messages:]

    def _cleanup_if_expired(self, chat_id: str):
        if chat_id in self._history:
            last_active = self._history[chat_id].get("last_active", 0)
            if time.time() - last_active > self.ttl_seconds:
                del self._history[chat_id]


memory = ConversationMemory(max_messages=settings.MAX_HISTORY_MESSAGES)
