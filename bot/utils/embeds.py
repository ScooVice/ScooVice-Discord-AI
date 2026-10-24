from datetime import datetime, timezone
from typing import Optional

import discord
from discord.ext import commands


_COLORS = {
    "success": 0x57F287,
    "error": 0xED4245,
    "warning": 0xFEE75C,
    "info": 0x3498DB,
}


def _create_embed(
    kind: str,
    title: str,
    description: str,
    bot: Optional[commands.Bot] = None,
) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=_COLORS[kind],
        timestamp=datetime.now(timezone.utc),
    )
    user = bot.user if bot else None
    if user:
        avatar_url = user.display_avatar.url
        embed.set_author(name=user.name, icon_url=avatar_url)
        embed.set_thumbnail(url=avatar_url)
        embed.set_footer(
            text=f"ScooVice-Discord-AI • {datetime.now(timezone.utc).year}",
            icon_url=avatar_url,
        )
    else:
        embed.set_footer(text="ScooVice-Discord-AI")
    return embed


def success_embed(
    title: str, description: str, bot: Optional[commands.Bot] = None
) -> discord.Embed:
    return _create_embed("success", title, description, bot)


def error_embed(
    title: str, description: str, bot: Optional[commands.Bot] = None
) -> discord.Embed:
    return _create_embed("error", title, description, bot)


def warning_embed(
    title: str, description: str, bot: Optional[commands.Bot] = None
) -> discord.Embed:
    return _create_embed("warning", title, description, bot)


def info_embed(
    title: str, description: str, bot: Optional[commands.Bot] = None
) -> discord.Embed:
    return _create_embed("info", title, description, bot)
