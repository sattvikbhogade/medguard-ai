import os
from dotenv import load_dotenv

# Loads variables from .env into the environment
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROK_API_KEY = os.getenv("GROK_API_KEY")

if not (GEMINI_API_KEY or OPENROUTER_API_KEY or GROK_API_KEY):
    raise ValueError(
        "No AI provider API key found. Set GEMINI_API_KEY, OPENROUTER_API_KEY, or GROK_API_KEY in .env."
    )