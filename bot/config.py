import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL") or "openai/gpt-oss-20b"


def _get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be set to true or false")


AUTOMOD_BANNED_WORDS = tuple(
    word.strip().casefold()
    for word in os.getenv("AUTOMOD_BANNED_WORDS", "").split(",")
    if word.strip()
)
AUTOMOD_BLOCK_LINKS = _get_bool_env("AUTOMOD_BLOCK_LINKS", False)
AUTOMOD_BLOCK_EXCESSIVE_CAPS = _get_bool_env(
    "AUTOMOD_BLOCK_EXCESSIVE_CAPS", False
)

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found in .env")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in .env")
