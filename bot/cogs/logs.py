import logging

import discord
from discord.ext import commands

from bot.utils.embeds import info_embed


logger = logging.getLogger(__name__)


class Logs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _log_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        channel = discord.utils.get(guild.text_channels, name="mod-logs")
        return channel

    async def _send_log(self, channel: discord.TextChannel, embed: discord.Embed) -> None:
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning("Missing permission to send moderation logs to %s", channel.id)
        except discord.HTTPException:
            logger.exception("Could not send moderation log to channel %s", channel.id)

    @commands.Cog.listener()
    async def on_member_ban(
        self, guild: discord.Guild, user: discord.User
    ) -> None:
        channel = self._log_channel(guild)
        if channel:
            await self._send_log(
                channel,
                info_embed(
                    "Member Banned",
                    f"**User:** {user}\n**ID:** {user.id}",
                    self.bot,
                ),
            )

    @commands.Cog.listener()
    async def on_member_unban(
        self, guild: discord.Guild, user: discord.User
    ) -> None:
        channel = self._log_channel(guild)
        if channel:
            await self._send_log(
                channel,
                info_embed(
                    "Member Unbanned",
                    f"**User:** {user}\n**ID:** {user.id}",
                    self.bot,
                ),
            )

    @commands.Cog.listener()
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        if before.timed_out_until == after.timed_out_until:
            return

        channel = self._log_channel(after.guild)
        if channel is None:
            return

        if after.timed_out_until:
            embed = info_embed(
                "Member Timed Out",
                f"**User:** {after}\n**Until:** {after.timed_out_until}",
                self.bot,
            )
        else:
            embed = info_embed("Timeout Removed", f"**User:** {after}", self.bot)
        await self._send_log(channel, embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Logs(bot))
