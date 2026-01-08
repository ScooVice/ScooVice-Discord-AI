import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from typing import Optional

from bot.utils.embeds import success_embed, error_embed, warning_embed


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "No reason provided",
    ):
        await interaction.response.defer()

        if member == interaction.user:
            await interaction.followup.send(
                embed=error_embed(
                    "Action denied", "You cannot kick yourself.", self.bot
                ),
                ephemeral=True,
            )
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.followup.send(
                embed=error_embed(
                    "Hierarchy error", "I cannot kick this member.", self.bot
                ),
                ephemeral=True,
            )
            return

        await member.kick(reason=reason)

        await interaction.followup.send(
            embed=success_embed(
                "Member kicked", f"**User:** {member}\n**Reason:** {reason}", self.bot
            )
        )

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "No reason provided",
    ):
        await interaction.response.defer()

        if member == interaction.user:
            await interaction.followup.send(
                embed=error_embed(
                    "Action denied", "You cannot ban yourself.", self.bot
                ),
                ephemeral=True,
            )
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.followup.send(
                embed=error_embed(
                    "Hierarchy error", "I cannot ban this member.", self.bot
                ),
                ephemeral=True,
            )
            return

        await interaction.guild.ban(member, reason=reason)

        await interaction.followup.send(
            embed=success_embed(
                "Member banned", f"**User:** {member}\n**Reason:** {reason}", self.bot
            )
        )

    @app_commands.command(name="unban", description="Unban a user by ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str,
        reason: Optional[str] = "No reason provided",
    ):
        await interaction.response.defer()

        user = await self.bot.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=reason)

        await interaction.followup.send(
            embed=success_embed(
                "User unbanned", f"**User:** {user}\n**Reason:** {reason}", self.bot
            )
        )

    @app_commands.command(name="tempban", description="Temporarily ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def tempban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        days: int,
        reason: Optional[str] = "No reason provided",
    ):
        await interaction.response.defer()

        if member == interaction.user:
            await interaction.followup.send(
                embed=error_embed(
                    "Action denied", "You cannot ban yourself.", self.bot
                ),
                ephemeral=True,
            )
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.followup.send(
                embed=error_embed(
                    "Hierarchy error", "I cannot ban this member.", self.bot
                ),
                ephemeral=True,
            )
            return

        duration = timedelta(days=days)
        await member.ban(reason=reason, delete_message_days=0)

        # Schedule unban
        import asyncio

        async def unban_after():
            await asyncio.sleep(duration.total_seconds())
            await interaction.guild.unban(member)

        self.bot.loop.create_task(unban_after())

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
    async def mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: int,
        reason: Optional[str] = "No reason provided",
    ):
        await interaction.response.defer()

        if member == interaction.user:
            await interaction.followup.send(
                embed=error_embed(
                    "Action denied", "You cannot mute yourself.", self.bot
                ),
                ephemeral=True,
            )
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.followup.send(
                embed=error_embed(
                    "Hierarchy error", "I cannot mute this member.", self.bot
                ),
                ephemeral=True,
            )
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
    async def unmute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "No reason provided",
    ):
        await interaction.response.defer()

        await member.timeout(None)

        await interaction.followup.send(
            embed=success_embed(
                "Member unmuted", f"**User:** {member}\n**Reason:** {reason}", self.bot
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
