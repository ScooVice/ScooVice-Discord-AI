import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands, tasks

from bot.utils.embeds import success_embed, error_embed, warning_embed
from bot.utils.tempban_store import TempBanStore


logger = logging.getLogger(__name__)


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        database_path = Path(__file__).resolve().parents[2] / "data" / "tempbans.sqlite3"
        self.tempban_store = TempBanStore(database_path)

    async def cog_load(self):
        self.expired_tempban_check.start()

    async def cog_unload(self):
        self.expired_tempban_check.cancel()

    @tasks.loop(seconds=30)
    async def expired_tempban_check(self):
        now = int(datetime.now(timezone.utc).timestamp())
        for guild_id, user_id in self.tempban_store.expired(now):
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                continue

            try:
                await guild.unban(
                    discord.Object(id=user_id),
                    reason="Temporary ban expired",
                )
            except discord.NotFound:
                self.tempban_store.remove(guild_id, user_id)
            except discord.HTTPException:
                logger.exception(
                    "Failed to expire temporary ban for user %s in guild %s",
                    user_id,
                    guild_id,
                )
            else:
                self.tempban_store.remove(guild_id, user_id)

    @expired_tempban_check.before_loop
    async def before_expired_tempban_check(self):
        await self.bot.wait_until_ready()

    def _target_error(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> Optional[str]:
        guild = interaction.guild
        bot_user = self.bot.user
        if guild is None or bot_user is None or guild.me is None:
            return "This command can only be used in a server."
        if member.id == interaction.user.id:
            return "You cannot target yourself."
        if member.id == bot_user.id or member.top_role >= guild.me.top_role:
            return "I cannot moderate a member with an equal or higher role."
        if (
            interaction.user.id != guild.owner_id
            and member.top_role >= interaction.user.top_role
        ):
            return "You cannot moderate a member with an equal or higher role."
        return None

    async def _send_target_error(
        self, interaction: discord.Interaction, message: str
    ) -> None:
        await interaction.followup.send(
            embed=error_embed("Action denied", message, self.bot),
            ephemeral=True,
        )

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    @app_commands.guild_only()
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "No reason provided",
    ):
        await interaction.response.defer()

        target_error = self._target_error(interaction, member)
        if target_error:
            await self._send_target_error(interaction, target_error)
            return

        await member.kick(reason=reason)

        await interaction.followup.send(
            embed=success_embed(
                "Member kicked", f"**User:** {member}\n**Reason:** {reason}", self.bot
            )
        )

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "No reason provided",
    ):
        await interaction.response.defer()

        target_error = self._target_error(interaction, member)
        if target_error:
            await self._send_target_error(interaction, target_error)
            return

        guild = interaction.guild
        if guild is None:
            return
        await guild.ban(member, reason=reason)
        self.tempban_store.remove(guild.id, member.id)

        await interaction.followup.send(
            embed=success_embed(
                "Member banned", f"**User:** {member}\n**Reason:** {reason}", self.bot
            )
        )

    @app_commands.command(name="unban", description="Unban a user by ID")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: int,
        reason: Optional[str] = "No reason provided",
    ):
        await interaction.response.defer()

        guild = interaction.guild
        if guild is None:
            return
        user = discord.Object(id=user_id)
        await guild.unban(user, reason=reason)
        self.tempban_store.remove(guild.id, user.id)

        await interaction.followup.send(
            embed=success_embed(
                "User unbanned",
                f"**User ID:** {user_id}\n**Reason:** {reason}",
                self.bot,
            )
        )

    @app_commands.command(name="tempban", description="Temporarily ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def tempban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        days: app_commands.Range[int, 1, 36500],
        reason: Optional[str] = "No reason provided",
    ):
        await interaction.response.defer()

        guild = interaction.guild
        if guild is None:
            await interaction.followup.send(
                embed=error_embed(
                    "Server only",
                    "Temporary bans can only be used in a server.",
                    self.bot,
                ),
                ephemeral=True,
            )
            return

        target_error = self._target_error(interaction, member)
        if target_error:
            await self._send_target_error(interaction, target_error)
            return

        expires_at = int((datetime.now(timezone.utc) + timedelta(days=days)).timestamp())
        self.tempban_store.schedule(guild.id, member.id, expires_at)
        try:
            await member.ban(reason=reason, delete_message_seconds=0)
        except discord.HTTPException:
            self.tempban_store.remove(guild.id, member.id)
            raise

        await interaction.followup.send(
            embed=success_embed(
                "Member temporarily banned",
                f"**User:** {member}\n**Duration:** {days} days\n**Reason:** {reason}",
                self.bot,
            )
        )

    # =========================
    # MUTE (TIMEOUT)
    @app_commands.command(name="mute", description="Timeout a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    @app_commands.guild_only()
    async def mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: app_commands.Range[int, 1, 40320],
        reason: Optional[str] = "No reason provided",
    ):
        await interaction.response.defer()

        target_error = self._target_error(interaction, member)
        if target_error:
            await self._send_target_error(interaction, target_error)
            return

        duration = timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)

        await interaction.followup.send(
            embed=warning_embed(
                "Member muted",
                f"**User:** {member}\n**Duration:** {minutes} minutes\n**Reason:** {reason}",
                self.bot,
            )
        )

    @app_commands.command(name="unmute", description="Remove timeout from a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    @app_commands.guild_only()
    async def unmute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "No reason provided",
    ):
        await interaction.response.defer()

        target_error = self._target_error(interaction, member)
        if target_error:
            await self._send_target_error(interaction, target_error)
            return

        await member.timeout(None, reason=reason)

        await interaction.followup.send(
            embed=success_embed(
                "Member unmuted", f"**User:** {member}\n**Reason:** {reason}", self.bot
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
