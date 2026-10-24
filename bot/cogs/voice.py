import logging

import discord
from discord import app_commands
from discord.ext import commands

from bot.utils.embeds import error_embed, info_embed, success_embed


logger = logging.getLogger(__name__)


class VoicePanel(discord.ui.View):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=300)
        self.bot = bot

    async def _reply(
        self, interaction: discord.Interaction, title: str, description: str
    ) -> None:
        await interaction.response.send_message(
            embed=info_embed(title, description, self.bot),
            ephemeral=True,
        )

    @discord.ui.button(
        label="Join my voice",
        style=discord.ButtonStyle.primary,
        emoji="🔊",
    )
    async def join_voice(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        guild = interaction.guild
        member = interaction.user
        voice_state = member.voice if isinstance(member, discord.Member) else None
        channel = voice_state.channel if voice_state else None
        if guild is None or channel is None:
            await interaction.response.send_message(
                embed=error_embed(
                    "Join a voice channel first",
                    "Connect to a voice channel, then press this button.",
                    self.bot,
                ),
                ephemeral=True,
            )
            return

        bot_member = guild.me
        if bot_member is None or not channel.permissions_for(bot_member).connect:
            await interaction.response.send_message(
                embed=error_embed(
                    "Voice permission missing",
                    "I need permission to connect to that voice channel.",
                    self.bot,
                ),
                ephemeral=True,
            )
            return

        voice_client = guild.voice_client
        try:
            if voice_client and voice_client.is_connected():
                if voice_client.channel == channel:
                    await self._reply(
                        interaction,
                        "Already connected",
                        f"I'm already in **{channel.name}**.",
                    )
                    return
                if not member.guild_permissions.manage_channels:
                    await interaction.response.send_message(
                        embed=error_embed(
                            "Already in another channel",
                            "A server manager must move me from my current "
                            "voice channel.",
                            self.bot,
                        ),
                        ephemeral=True,
                    )
                    return
                await voice_client.move_to(channel)
            else:
                await channel.connect(self_deaf=True)
        except discord.Forbidden:
            logger.warning("Discord denied voice connection to channel %s", channel.id)
            await interaction.response.send_message(
                embed=error_embed(
                    "Could not connect",
                    "Discord denied access to that voice channel.",
                    self.bot,
                ),
                ephemeral=True,
            )
            return
        except (discord.ClientException, discord.HTTPException):
            logger.exception("Failed to connect to voice channel %s", channel.id)
            await interaction.response.send_message(
                embed=error_embed(
                    "Could not connect",
                    "The voice connection failed. Please try again.",
                    self.bot,
                ),
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            embed=success_embed(
                "Connected",
                f"I joined **{channel.name}**. This bot currently joins voice "
                "only; it does not play audio.",
                self.bot,
            ),
            ephemeral=True,
        )

    @discord.ui.button(
        label="Leave voice",
        style=discord.ButtonStyle.secondary,
        emoji="🔇",
    )
    async def leave_voice(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        guild = interaction.guild
        if guild is None or guild.voice_client is None:
            await interaction.response.send_message(
                embed=error_embed(
                    "Not connected",
                    "I'm not connected to a voice channel in this server.",
                    self.bot,
                ),
                ephemeral=True,
            )
            return

        member = interaction.user
        member_channel = (
            member.voice.channel
            if isinstance(member, discord.Member) and member.voice
            else None
        )
        voice_client = guild.voice_client
        if (
            member_channel != voice_client.channel
            and not (
                isinstance(member, discord.Member)
                and member.guild_permissions.manage_channels
            )
        ):
            await interaction.response.send_message(
                embed=error_embed(
                    "Action denied",
                    "Join my voice channel or ask a server manager to disconnect me.",
                    self.bot,
                ),
                ephemeral=True,
            )
            return

        try:
            await voice_client.disconnect(force=True)
        except discord.HTTPException:
            logger.exception("Failed to disconnect from voice in guild %s", guild.id)
            await interaction.response.send_message(
                embed=error_embed(
                    "Could not disconnect",
                    "The voice disconnect failed. Please try again.",
                    self.bot,
                ),
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            embed=success_embed("Disconnected", "I left the voice channel.", self.bot),
            ephemeral=True,
        )


class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="voice", description="Open voice connection controls")
    @app_commands.guild_only()
    async def voice(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            embed=info_embed(
                "Voice Controls",
                "Use the buttons to join your voice channel or disconnect. "
                "The bot joins silently and does not play audio.",
                self.bot,
            ),
            view=VoicePanel(self.bot),
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Voice(bot))
