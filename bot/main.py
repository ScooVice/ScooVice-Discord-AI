import logging

import discord
from discord import app_commands
from discord.ext import commands

from bot.config import DISCORD_TOKEN
from bot.utils.embeds import error_embed


logger = logging.getLogger(__name__)


class ScooViceCommandTree(app_commands.CommandTree):
    async def on_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        original = getattr(error, "original", error)
        if isinstance(error, app_commands.MissingPermissions):
            message = f"You need: {', '.join(error.missing_permissions)}"
        elif isinstance(error, app_commands.BotMissingPermissions):
            message = f"I need: {', '.join(error.missing_permissions)}"
        elif isinstance(error, app_commands.CheckFailure):
            message = "You don't have permission to use this command."
        else:
            message = "An unexpected error occurred. Please try again later."
            logger.error(
                "Slash command failed: %s",
                error,
                exc_info=(type(original), original, original.__traceback__),
            )

        try:
            embed = error_embed("Command Error", message, self.client)
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.HTTPException:
            logger.exception("Could not send slash-command error response")


class ScooViceBot(commands.Bot):
    extensions = (
        "bot.cogs.admin",
        "bot.cogs.core",
        "bot.cogs.automod",
        "bot.cogs.logs",
        "bot.cogs.ai",
    )

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            tree_cls=ScooViceCommandTree,
        )

    async def setup_hook(self) -> None:
        for extension in self.extensions:
            await self.load_extension(extension)
            logger.info("Loaded extension %s", extension)

        synced_commands = await self.tree.sync()
        logger.info("Synced %s slash commands", len(synced_commands))

    async def on_ready(self) -> None:
        if self.user is None:
            logger.error("Discord connected without a bot user")
            return

        logger.info(
            "Logged in as %s (ID %s) in %s servers",
            self.user,
            self.user.id,
            len(self.guilds),
        )
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/help | ScooVice's AI ChatBot",
            ),
            status=discord.Status.online,
        )

    async def close(self) -> None:
        logger.info("Shutting down bot")
        await super().close()


def run_bot() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    bot = ScooViceBot()
    bot.run(DISCORD_TOKEN, log_handler=None)
