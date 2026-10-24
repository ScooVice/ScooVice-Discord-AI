import logging
import sys

import discord
from discord import app_commands
from discord.ext import commands

from bot.config import DISCORD_TOKEN
from bot.utils.embeds import error_embed
from bot.utils.voice_support import voice_stack_ready


logger = logging.getLogger(__name__)


def print_startup_banner(bot: commands.Bot, command_count: int) -> None:
    use_color = sys.stdout.isatty()
    accent = "\033[96m" if use_color else ""
    green = "\033[92m" if use_color else ""
    red = "\033[91m" if use_color else ""
    dim = "\033[90m" if use_color else ""
    reset = "\033[0m" if use_color else ""
    voice_ready = voice_stack_ready()
    voice_status = (
        f"{green}Ready · DAVE + PyNaCl{reset}"
        if voice_ready
        else f"{red}Missing voice packages{reset}"
    )
    name = bot.user.name if bot.user else "ScooVice Discord AI"
    guild_count = len(bot.guilds)

    print()
    print(f"{accent}╭──────────────────────────────────────────────────╮{reset}")
    print(f"{accent}│{reset}  ✨ {name}")
    print(f"{accent}├──────────────────────────────────────────────────┤{reset}")
    print(f"{accent}│{reset}  ✅ Status       Online")
    print(f"{accent}│{reset}  🌐 Servers      {guild_count}")
    print(f"{accent}│{reset}  ⚡ Commands     {command_count} synced")
    print(f"{accent}│{reset}  🔊 Voice        {voice_status}")
    print(
        f"{accent}╰──────────────────────────────────────────────────╯{reset}"
    )
    print(f"{dim}  Press Ctrl+C to stop the bot.{reset}")
    print()


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
        "bot.cogs.settings",
        "bot.cogs.voice",
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
        self.synced_command_count = len(synced_commands)

    async def on_ready(self) -> None:
        if self.user is None:
            logger.error("Discord connected without a bot user")
            return

        if not getattr(self, "_startup_banner_shown", False):
            print_startup_banner(
                self,
                getattr(self, "synced_command_count", len(self.tree.get_commands())),
            )
            self._startup_banner_shown = True
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
        level=logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    bot = ScooViceBot()
    bot.run(DISCORD_TOKEN, log_handler=None)
