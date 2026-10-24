import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL") or "openai/gpt-oss-20b"
GROQ_REASONING_EFFORT = os.getenv("GROQ_REASONING_EFFORT", "low").strip().lower()


def _get_int_env(name: str, default: int, allowed_values: set[int]) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if value not in allowed_values:
        allowed = ", ".join(str(item) for item in sorted(allowed_values))
        raise RuntimeError(f"{name} must be one of: {allowed}")
    return value


if GROQ_REASONING_EFFORT not in {"low", "medium", "high"}:
    raise RuntimeError("GROQ_REASONING_EFFORT must be low, medium, or high")

GROQ_MAX_COMPLETION_TOKENS = _get_int_env(
    "GROQ_MAX_COMPLETION_TOKENS", 512, {256, 512, 1024, 2048}
)
GROQ_HISTORY_TURNS = _get_int_env("GROQ_HISTORY_TURNS", 5, {2, 5, 10})


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
