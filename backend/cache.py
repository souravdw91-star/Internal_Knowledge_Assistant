"""
cache.py

Redis response cache.
"""

import json
import redis

from backend.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
    CACHE_ENABLED,
    CACHE_TTL,
)

from backend.utils import (
    LOGGER,
    generate_hash,
)


class RedisCache:

    def __init__(self):

        self.enabled = CACHE_ENABLED

        if not self.enabled:

            self.client = None

            LOGGER.info("Redis cache disabled.")

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

            LOGGER.info("Redis cache connected.")

        except Exception as e:

            LOGGER.exception(e)

            self.client = None

    # -----------------------------------------------------
    # Cache Key
    # -----------------------------------------------------

    @staticmethod
    def build_key(question: str) -> str:

        return f"rag_cache:{generate_hash(question)}"

    # -----------------------------------------------------
    # Get
    # -----------------------------------------------------

    def get(self, question: str):

        if self.client is None:

            return None

        try:

            key = self.build_key(question)

            value = self.client.get(key)

            if value is None:

                return None

            LOGGER.info("Cache hit.")

            return json.loads(value)

        except Exception as e:

            LOGGER.exception(e)

            return None

    # -----------------------------------------------------
    # Set
    # -----------------------------------------------------

    def set(
        self,
        question: str,
        response: dict,
    ):

        if self.client is None:

            return

        try:

            key = self.build_key(question)

            self.client.setex(
                key,
                CACHE_TTL,
                json.dumps(response),
            )

            LOGGER.info("Response cached.")

        except Exception as e:

            LOGGER.exception(e)

    # -----------------------------------------------------
    # Exists
    # -----------------------------------------------------

    def exists(
        self,
        question: str,
    ) -> bool:

        if self.client is None:

            return False

        try:

            key = self.build_key(question)

            return bool(self.client.exists(key))

        except Exception:

            return False

    # -----------------------------------------------------
    # Delete
    # -----------------------------------------------------

    def delete(
        self,
        question: str,
    ):

        if self.client is None:

            return

        try:

            key = self.build_key(question)

            self.client.delete(key)

        except Exception as e:

            LOGGER.exception(e)

    # -----------------------------------------------------
    # Clear All
    # -----------------------------------------------------

    def clear(self):

        if self.client is None:

            return

        try:

            pattern = "rag_cache:*"

            keys = self.client.keys(pattern)

            if keys:

                self.client.delete(*keys)

            LOGGER.info("Cache cleared.")

        except Exception as e:

            LOGGER.exception(e)

    # -----------------------------------------------------
    # TTL
    # -----------------------------------------------------

    def ttl(
        self,
        question: str,
    ):

        if self.client is None:

            return -1

        try:

            key = self.build_key(question)

            return self.client.ttl(key)

        except Exception:

            return -1

    # -----------------------------------------------------
    # Stats
    # -----------------------------------------------------

    def stats(self):

        if self.client is None:

            return {
                "enabled": False
            }

        try:

            info = self.client.info()

            return {

                "enabled": True,

                "connected_clients": info.get(
                    "connected_clients"
                ),

                "used_memory": info.get(
                    "used_memory_human"
                ),

                "total_keys": len(
                    self.client.keys("rag_cache:*")
                ),

            }

        except Exception:

            return {
                "enabled": False
            }


# Singleton

redis_cache = RedisCache()