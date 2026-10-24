import re
import time
from collections import OrderedDict, deque

import discord
from discord.ext import commands

from bot.config import (
    AUTOMOD_BANNED_WORDS,
    AUTOMOD_BLOCK_EXCESSIVE_CAPS,
    AUTOMOD_BLOCK_LINKS,
)
from bot.utils.embeds import warning_embed


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banned_words = AUTOMOD_BANNED_WORDS
        self.block_links = AUTOMOD_BLOCK_LINKS
        self.block_excessive_caps = AUTOMOD_BLOCK_EXCESSIVE_CAPS
        self.spam_threshold = 5
        self.spam_window = 10
        self.user_messages = OrderedDict()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author.bot:
            return
        if isinstance(message.author, discord.Member) and (
            message.author.guild_permissions.manage_messages
        ):
            return
        if isinstance(self.bot.command_prefix, str) and message.content.startswith(
            self.bot.command_prefix
        ):
            return

        content = message.content
        folded_content = content.casefold()
        if any(
            re.search(rf"(?<!\w){re.escape(word)}(?!\w)", folded_content)
            for word in self.banned_words
        ):
            await self._delete_and_warn(message, "Banned Word Detected")
            return

        if self.block_excessive_caps:
            letters = [character for character in content if character.isalpha()]
            if len(letters) > 5 and sum(c.isupper() for c in letters) / len(letters) > 0.7:
                await self._delete_and_warn(message, "Excessive Caps")
                return

        if self.block_links and re.search(r"(?:https?://|www\.)\S+", content, re.IGNORECASE):
            await self._delete_and_warn(message, "Links Not Allowed")
            return

        key = (message.guild.id, message.author.id)
        now = time.monotonic()
        timestamps = self.user_messages.pop(key, deque())
        while timestamps and now - timestamps[0] >= self.spam_window:
            timestamps.popleft()
        timestamps.append(now)
        self.user_messages[key] = timestamps
        if len(self.user_messages) > 10_000:
            self.user_messages.popitem(last=False)

        if len(timestamps) > self.spam_threshold:
            self.user_messages.pop(key, None)
            await self._delete_and_warn(message, "Spam Detected")

    async def _delete_and_warn(self, message, reason: str):
        await message.delete()
        embed = warning_embed(
            reason,
            f"{message.author.mention}, your message was removed by AutoMod.",
            self.bot,
        )
        await message.channel.send(embed=embed, delete_after=10)


async def setup(bot):
    await bot.add_cog(AutoMod(bot))
