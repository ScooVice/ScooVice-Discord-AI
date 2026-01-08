import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found in .env")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in .env")
