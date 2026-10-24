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
            "ScooVice Command Center",
            "Chat with me by mentioning me or sending a direct message. "
            "Choose a command below to get started.",
            self.bot,
        )
        embed.add_field(
            name="🤖 AI & Voice",
            value=(
                "Mention me with a message — Chat with AI\n"
                "`/clear_chat` — Clear your conversation\n"
                "`/settings` — Configure AI (server managers)\n"
                "`/voice` — Open voice controls"
            ),
            inline=False,
        )
        embed.add_field(
            name="🛡️ Moderation",
            value=(
                "`/kick` · `/ban` · `/tempban` · `/unban`\n"
                "`/mute` · `/unmute`"
            ),
            inline=False,
        )
        embed.add_field(
            name="✨ Utilities",
            value="`/ping` — Check latency\n`/help` — Show this guide",
            inline=False,
        )
        await interaction.response.defer()
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Core(bot))
