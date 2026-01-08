import discord
from datetime import datetime
from typing import Optional
from discord.ext import commands


def success_embed(
    title: str, description: str, bot: Optional[commands.Bot] = None
) -> discord.Embed:
    """Create a success embed (green)"""
    embed = discord.Embed(title=title, description=description, color=0x57F287)
    if bot:
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(
            text=f"ScooVice-Discord-AI • {datetime.now().year}",
            icon_url=bot.user.avatar.url,
        )
    else:
        embed.set_footer(text="ScooVice-Discord-AI")
    embed.timestamp = datetime.now()
    return embed


def error_embed(
    title: str, description: str, bot: Optional[commands.Bot] = None
) -> discord.Embed:
    """Create an error embed (red)"""
    embed = discord.Embed(title=title, description=description, color=0xED4245)
    if bot:
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(
            text=f"ScooVice-Discord-AI • {datetime.now().year}",
            icon_url=bot.user.avatar.url,
        )
    else:
        embed.set_footer(text="ScooVice-Discord-AI")
    embed.timestamp = datetime.now()
    return embed


def warning_embed(
    title: str, description: str, bot: Optional[commands.Bot] = None
) -> discord.Embed:
    """Create a warning embed (yellow)"""
    embed = discord.Embed(title=title, description=description, color=0xFEE75C)
    if bot:
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(
            text=f"ScooVice-Discord-AI • {datetime.now().year}",
            icon_url=bot.user.avatar.url,
        )
    else:
        embed.set_footer(text="ScooVice-Discord-AI")
    embed.timestamp = datetime.now()
    return embed


def info_embed(
    title: str, description: str, bot: Optional[commands.Bot] = None
) -> discord.Embed:
    """Create an info embed (blue)"""
    embed = discord.Embed(title=title, description=description, color=0x3498DB)
    if bot:
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(
            text=f"ScooVice-Discord-AI • {datetime.now().year}",
            icon_url=bot.user.avatar.url,
        )
    else:
        embed.set_footer(text="ScooVice-Discord-AI")
    embed.timestamp = datetime.now()
    return embed
