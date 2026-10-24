import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands

from bot.utils.embeds import error_embed, info_embed, success_embed
from bot.utils.voice_support import voice_stack_ready


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

    async def _finish(
        self, interaction: discord.Interaction, embed: discord.Embed
    ) -> None:
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

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

        if not voice_stack_ready():
            await interaction.response.send_message(
                embed=error_embed(
                    "Voice support isn't ready",
                    "Install the current dependencies with "
                    "`python -m pip install -r requirements.txt`, then restart "
                    "the bot.",
                    self.bot,
                ),
                ephemeral=True,
            )
            return

        bot_member = guild.me
        if bot_member is None:
            await interaction.response.send_message(
                embed=error_embed(
                    "Voice unavailable",
                    "I couldn't find my server member profile. Try again shortly.",
                    self.bot,
                ),
                ephemeral=True,
            )
            return

        permissions = channel.permissions_for(bot_member)
        if not permissions.view_channel or not permissions.connect:
            await interaction.response.send_message(
                embed=error_embed(
                    "Voice permission missing",
                    "I need **View Channel** and **Connect** permissions in that "
                    "voice channel.",
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
            await interaction.response.defer(ephemeral=True, thinking=True)
            if voice_client and voice_client.is_connected():
                await voice_client.move_to(channel)
            else:
                if voice_client is not None:
                    await voice_client.disconnect(force=True)
                await channel.connect(
                    timeout=30.0,
                    reconnect=True,
                    self_deaf=True,
                )
        except asyncio.TimeoutError:
            logger.warning("Voice connection timed out for channel %s", channel.id)
            await self._finish(
                interaction,
                error_embed(
                    "Voice connection timed out",
                    "Discord didn't finish the voice handshake. Check the bot's "
                    "voice permissions and update its dependencies with "
                    "`python -m pip install -r requirements.txt`, then restart it.",
                    self.bot,
                ),
            )
            return
        except discord.Forbidden:
            logger.warning("Discord denied voice connection to channel %s", channel.id)
            await self._finish(
                interaction,
                error_embed(
                    "Could not connect",
                    "Discord denied access to that voice channel.",
                    self.bot,
                ),
            )
            return
        except (discord.ClientException, discord.HTTPException, OSError):
            logger.exception("Failed to connect to voice channel %s", channel.id)
            await self._finish(
                interaction,
                error_embed(
                    "Could not connect",
                    "The voice connection failed. Confirm the bot has the required "
                    "voice permissions, update the bot dependencies, and try again.",
                    self.bot,
                ),
            )
            return

        await self._finish(
            interaction,
            success_embed(
                "Connected",
                f"I joined **{channel.name}**. This bot currently joins voice "
                "only; it does not play audio.",
                self.bot,
            ),
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

        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            await voice_client.disconnect(force=True)
        except discord.HTTPException:
            logger.exception("Failed to disconnect from voice in guild %s", guild.id)
            await self._finish(
                interaction,
                error_embed(
                    "Could not disconnect",
                    "The voice disconnect failed. Please try again.",
                    self.bot,
                ),
            )
            return

        await self._finish(
            interaction,
            success_embed("Disconnected", "I left the voice channel.", self.bot),
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
