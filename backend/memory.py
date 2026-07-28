"""
memory.py

Redis-backed conversation memory.
"""

import json
import redis
from typing import List, Dict

from backend.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
    MEMORY_ENABLED,
    MEMORY_WINDOW,
)

from backend.utils import LOGGER


class RedisMemory:

    def __init__(self):

        self.enabled = MEMORY_ENABLED

        if not self.enabled:

            self.client = None

            LOGGER.info("Conversation memory disabled.")

            return

        try:

            self.client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD or None,
                decode_responses=True,
            )

            self.client.ping()

            LOGGER.info("Redis memory connected.")

        except Exception as e:

            LOGGER.exception(e)

            self.client = None

    # ---------------------------------------------------------
    # Session Key
    # ---------------------------------------------------------

    @staticmethod
    def session_key(session_id: str) -> str:

        return f"chat_memory:{session_id}"

    # ---------------------------------------------------------
    # Add Message
    # ---------------------------------------------------------

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ):

        if self.client is None:
            return

        try:

            key = self.session_key(session_id)

            message = json.dumps(
                {
                    "role": role,
                    "content": content,
                }
            )

            self.client.rpush(key, message)

            length = self.client.llen(key)

            if length > MEMORY_WINDOW * 2:

                self.client.ltrim(
                    key,
                    length - (MEMORY_WINDOW * 2),
                    -1,
                )

        except Exception as e:

            LOGGER.exception(e)

    # ---------------------------------------------------------
    # Get History
    # ---------------------------------------------------------

    def get_history(
        self,
        session_id: str,
    ) -> List[Dict]:

        if self.client is None:
            return []

        try:

            key = self.session_key(session_id)

            history = self.client.lrange(
                key,
                0,
                -1,
            )

            return [
                json.loads(item)
                for item in history
            ]

        except Exception as e:

            LOGGER.exception(e)

            return []

    # ---------------------------------------------------------
    # Formatted History
    # ---------------------------------------------------------

    def formatted_history(
        self,
        session_id: str,
    ) -> str:

        history = self.get_history(session_id)

        if not history:
            return ""

        lines = []

        for item in history:

            role = item["role"].capitalize()

            lines.append(
                f"{role}: {item['content']}"
            )

        return "\n".join(lines)

    # ---------------------------------------------------------
    # Last Message
    # ---------------------------------------------------------

    def last_message(
        self,
        session_id: str,
    ):

        history = self.get_history(session_id)

        if not history:
            return None

        return history[-1]

    # ---------------------------------------------------------
    # Clear Session
    # ---------------------------------------------------------

    def clear_session(
        self,
        session_id: str,
    ):

        if self.client is None:
            return

        try:

            self.client.delete(
                self.session_key(session_id)
            )

        except Exception as e:

            LOGGER.exception(e)

    # ---------------------------------------------------------
    # Session Exists
    # ---------------------------------------------------------

    def exists(
        self,
        session_id: str,
    ) -> bool:

        if self.client is None:
            return False

        return bool(
            self.client.exists(
                self.session_key(session_id)
            )
        )

    # ---------------------------------------------------------
    # Number of Messages
    # ---------------------------------------------------------

    def message_count(
        self,
        session_id: str,
    ) -> int:

        if self.client is None:
            return 0

        try:

            return self.client.llen(
                self.session_key(session_id)
            )

        except Exception:

            return 0

    # ---------------------------------------------------------
    # Active Sessions
    # ---------------------------------------------------------

    def active_sessions(self):

        if self.client is None:
            return []

        try:

            keys = self.client.keys(
                "chat_memory:*"
            )

            return [
                key.replace(
                    "chat_memory:",
                    "",
                )
                for key in keys
            ]

        except Exception:

            return []

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def stats(self):

        if self.client is None:

            return {
                "enabled": False
            }

        return {

            "enabled": True,

            "sessions": len(
                self.active_sessions()
            ),

            "window_size": MEMORY_WINDOW,

        }


# Singleton

redis_memory = RedisMemory()