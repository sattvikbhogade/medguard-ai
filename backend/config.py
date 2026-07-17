import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from the project root, one level up from backend/,
# regardless of what directory uvicorn is launched from.
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROK_API_KEY = os.getenv("GROK_API_KEY")

if not (GEMINI_API_KEY or OPENROUTER_API_KEY or GROK_API_KEY):
    raise ValueError(
        "No AI provider API key found. Set GEMINI_API_KEY, OPENROUTER_API_KEY, or GROK_API_KEY in .env."
    )