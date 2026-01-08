import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from bot.config import DISCORD_TOKEN


class ScooViceBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.load_extension("bot.cogs.admin")
        await self.load_extension("bot.cogs.core")
        await self.load_extension("bot.cogs.automod")
        await self.load_extension("bot.cogs.logs")
        await self.load_extension("bot.cogs.ai")

        await self.tree.sync()

        print("✅ Slash commands synced")

    async def on_ready(self):
        print(f"🚀 Logged in as {self.user}")
        print(f"🆔 Bot ID: {self.user.id}")
        print(f"🌐 Servers: {len(self.guilds)}")

        # Set professional presence
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, name="/help | ScooVice's AI ChatBot"
            ),
            status=discord.Status.online,
        )


async def on_app_command_error(
    interaction: discord.Interaction, error: discord.app_commands.AppCommandError
):
    from bot.utils.embeds import error_embed

    if isinstance(error, discord.app_commands.MissingPermissions):
        missing = ", ".join(error.missing_permissions)
        embed = error_embed(
            "Missing Permissions", f"You need: {missing}", interaction.client
        )
    elif isinstance(error, discord.app_commands.BotMissingPermissions):
        missing = ", ".join(error.missing_permissions)
        embed = error_embed(
            "Bot Missing Permissions", f"I need: {missing}", interaction.client
        )
    elif isinstance(error, discord.app_commands.CheckFailure):
        embed = error_embed(
            "Check Failed",
            "You don't have permission to use this command.",
            interaction.client,
        )
    else:
        embed = error_embed(
            "Error", f"An error occurred: {str(error)}", interaction.client
        )

    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        pass  # In case of further errors
