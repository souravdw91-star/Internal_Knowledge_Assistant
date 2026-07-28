from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")

LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

REDIS_HOST = os.getenv("REDIS_HOST")

REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

REDIS_DB = int(os.getenv("REDIS_DB", 0))