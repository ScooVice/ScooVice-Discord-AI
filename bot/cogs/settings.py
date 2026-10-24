from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from bot.config import (
    GROQ_HISTORY_TURNS,
    GROQ_MAX_COMPLETION_TOKENS,
    GROQ_REASONING_EFFORT,
)
from bot.utils.ai_settings_store import AISettings, AISettingsStore
from bot.utils.embeds import error_embed, info_embed


REASONING_OPTIONS = ("low", "medium", "high")
TOKEN_OPTIONS = (256, 512, 1024, 2048)
HISTORY_OPTIONS = (2, 5, 10)


class AISettingsView(discord.ui.View):
    def __init__(self, store: AISettingsStore, guild_id: int, bot: commands.Bot):
        super().__init__(timeout=300)
        self.store = store
        self.guild_id = guild_id
        self.bot = bot
        self._build_components()

    def _build_components(self) -> None:
        settings = self.store.get(self.guild_id)
        self.clear_items()
        self.add_item(
            _SettingSelect(
                self,
                setting="reasoning_effort",
                placeholder="Reasoning: " + settings.reasoning_effort,
                values=REASONING_OPTIONS,
                current=str(settings.reasoning_effort),
                descriptions={
                    "low": "Faster replies; uses less reasoning",
                    "medium": "Balanced speed and reasoning",
                    "high": "More reasoning; can take longer",
                },
            )
        )
        self.add_item(
            _SettingSelect(
                self,
                setting="max_completion_tokens",
                placeholder=f"Reply limit: {settings.max_completion_tokens}",
                values=TOKEN_OPTIONS,
                current=str(settings.max_completion_tokens),
                descriptions={
                    str(value): f"At most {value} generated tokens"
                    for value in TOKEN_OPTIONS
                },
            )
        )
        self.add_item(
            _SettingSelect(
                self,
                setting="history_turns",
                placeholder=f"Context: {settings.history_turns} turns",
                values=HISTORY_OPTIONS,
                current=str(settings.history_turns),
                descriptions={
                    str(value): f"Keep the latest {value} conversation turns"
                    for value in HISTORY_OPTIONS
                },
            )
        )
        self.add_item(_ResetSettingsButton())

    def panel_embed(self) -> discord.Embed:
        settings = self.store.get(self.guild_id)
        embed = info_embed(
            "AI Settings",
            (
                f"**Reasoning:** `{settings.reasoning_effort}`\n"
                f"**Maximum reply tokens:** `{settings.max_completion_tokens}`\n"
                f"**Conversation context:** `{settings.history_turns}` turns\n\n"
                "Choose a setting below. Lower reasoning and shorter context "
                "usually respond faster and use fewer tokens. Groq rate limits "
                "still apply."
            ),
            self.bot,
        )
        embed.set_footer(text="Only server managers can change these settings")
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if (
            interaction.guild_id == self.guild_id
            and isinstance(interaction.user, discord.Member)
            and interaction.user.guild_permissions.manage_guild
        ):
            return True

        await interaction.response.send_message(
            embed=error_embed(
                "Settings unavailable",
                "Only server managers can use this settings panel.",
                self.bot,
            ),
            ephemeral=True,
        )
        return False


class _SettingSelect(discord.ui.Select):
    def __init__(
        self,
        view: AISettingsView,
        setting: str,
        placeholder: str,
        values: tuple[str, ...] | tuple[int, ...],
        current: str,
        descriptions: dict[str, str],
    ) -> None:
        self.settings_view = view
        self.setting = setting
        if setting == "reasoning_effort":
            labels = {str(value): str(value).title() for value in values}
        elif setting == "max_completion_tokens":
            labels = {str(value): f"{value} tokens" for value in values}
        else:
            labels = {str(value): f"{value} turns" for value in values}
        options = [
            discord.SelectOption(
                label=labels[str(value)],
                value=str(value),
                description=descriptions[str(value)],
                default=str(value) == current,
            )
            for value in values
        ]
        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        selected: str | int = self.values[0]
        if self.setting != "reasoning_effort":
            selected = int(selected)
        self.settings_view.store.update(
            self.settings_view.guild_id,
            self.setting,
            selected,
        )
        self.settings_view._build_components()
        await interaction.response.edit_message(
            embed=self.settings_view.panel_embed(),
            view=self.settings_view,
        )


class _ResetSettingsButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(
            label="Reset defaults",
            style=discord.ButtonStyle.secondary,
            row=3,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        view = self.view
        if not isinstance(view, AISettingsView):
            return
        view.store.reset(view.guild_id)
        view._build_components()
        await interaction.response.edit_message(
            embed=view.panel_embed(),
            view=view,
        )


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        defaults = AISettings(
            reasoning_effort=GROQ_REASONING_EFFORT,
            max_completion_tokens=GROQ_MAX_COMPLETION_TOKENS,
            history_turns=GROQ_HISTORY_TURNS,
        )
        database_path = (
            Path(__file__).resolve().parents[2] / "data" / "ai-settings.sqlite3"
        )
        self.store = AISettingsStore(database_path, defaults)

    @app_commands.command(name="settings", description="Configure AI chat settings")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def settings(self, interaction: discord.Interaction) -> None:
        guild_id = interaction.guild_id
        if guild_id is None:
            await interaction.response.send_message(
                embed=error_embed(
                    "Server only",
                    "AI settings can only be changed in a server.",
                    self.bot,
                ),
                ephemeral=True,
            )
            return

        view = AISettingsView(self.store, guild_id, self.bot)
        await interaction.response.send_message(
            embed=view.panel_embed(),
            view=view,
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Settings(bot))
