from datetime import datetime, timezone

import discord
from discord.ext import commands


_COLORS = {
    "success": 0x2ECC71,
    "error": 0xED4245,
    "warning": 0xF1C40F,
    "info": 0x5865F2,
}
_ICONS = {
    "success": "✅",
    "error": "⛔",
    "warning": "⚠️",
    "info": "✨",
}


def _create_embed(
    kind: str,
    title: str,
    description: str,
    bot: commands.Bot | None = None,
) -> discord.Embed:
    embed = discord.Embed(
        title=f"{_ICONS[kind]}  {title}",
        description=description,
        color=_COLORS[kind],
        timestamp=datetime.now(timezone.utc),
    )
    user = bot.user if bot else None
    if user:
        avatar_url = user.display_avatar.url
        embed.set_author(
            name=f"{user.name}  •  Discord Assistant",
            icon_url=avatar_url,
        )
        embed.set_footer(
            text=f"ScooVice  •  {datetime.now(timezone.utc).year}",
            icon_url=avatar_url,
        )
    else:
        embed.set_footer(text="ScooVice  •  Discord Assistant")
    return embed


def success_embed(
    title: str, description: str, bot: commands.Bot | None = None
) -> discord.Embed:
    return _create_embed("success", title, description, bot)


def error_embed(
    title: str, description: str, bot: commands.Bot | None = None
) -> discord.Embed:
    return _create_embed("error", title, description, bot)


def warning_embed(
    title: str, description: str, bot: commands.Bot | None = None
) -> discord.Embed:
    return _create_embed("warning", title, description, bot)


def info_embed(
    title: str, description: str, bot: commands.Bot | None = None
) -> discord.Embed:
    return _create_embed("info", title, description, bot)
