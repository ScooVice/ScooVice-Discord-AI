import discord
from discord import app_commands
from discord.ext import commands
from bot.utils.embeds import info_embed


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(
            f"Pong! 🏓 `{round(self.bot.latency * 1000)}ms`"
        )

    @app_commands.command(name="help", description="Show available commands")
    async def help(self, interaction: discord.Interaction):
        embed = info_embed(
            "ScooVice AI ChatBot Help",
            "**Moderation Commands:**\n"
            "/kick - Kick a member\n"
            "/ban - Ban a member\n"
            "/tempban - Temporarily ban a member\n"
            "/unban - Unban a user\n"
            "/mute - Timeout a member\n"
            "/unmute - Remove timeout\n"
            "**AI Commands:**\n"
            "/chat <message> - Chat with AI\n"
            "/clear_chat - Clear chat history\n\n"
            "**Other Commands:**\n"
            "/ping - Check bot latency\n"
            "/help - Show this help",
            self.bot,
        )
        await interaction.response.defer()
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Core(bot))
