import asyncio
import logging
import re
from collections import OrderedDict
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import discord
import httpx
from discord import app_commands
from discord.ext import commands
from groq import APIError, AsyncGroq

from bot.config import (
    GROQ_API_KEY,
    GROQ_HISTORY_TURNS,
    GROQ_MAX_COMPLETION_TOKENS,
    GROQ_MODEL,
    GROQ_REASONING_EFFORT,
)
from bot.utils.ai_settings_store import AISettings, AISettingsStore
from bot.utils.embeds import error_embed, info_embed


logger = logging.getLogger(__name__)
ConversationKey = tuple[int | None, int]
MAX_CONVERSATIONS = 5_000
MAX_EMBED_DESCRIPTION = 4_000
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are ScooVice AI, a helpful and friendly Discord bot assistant. "
        "Keep responses concise and engaging. You can help with Discord-related "
        "questions and general chat."
    ),
}


class ClearChatView(discord.ui.View):
    def __init__(self, cog: "AI", key: ConversationKey, owner_id: int) -> None:
        super().__init__(timeout=900)
        self.cog = cog
        self.key = key
        self.owner_id = owner_id

    @discord.ui.button(
        label="Clear my chat",
        style=discord.ButtonStyle.secondary,
        emoji="🧹",
    )
    async def clear_chat_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                embed=error_embed(
                    "This button is not for you",
                    "Only the person who started this conversation can clear it.",
                    self.cog.bot,
                ),
                ephemeral=True,
            )
            return

        async with self.cog._conversation_lock(self.key):
            self.cog.conversations.pop(self.key, None)
        button.disabled = True
        await interaction.response.send_message(
            embed=info_embed(
                "Chat cleared",
                "Your conversation history has been deleted.",
                self.cog.bot,
            ),
            ephemeral=True,
        )
        if interaction.message:
            await interaction.message.edit(view=self)


class AI(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
        settings_store: AISettingsStore | None = None,
    ) -> None:
        self.bot = bot
        http_client = httpx.AsyncClient(trust_env=False)
        self.client = AsyncGroq(api_key=GROQ_API_KEY, http_client=http_client)
        self.conversations: OrderedDict[
            ConversationKey, list[dict[str, str]]
        ] = OrderedDict()
        self.conversation_locks: dict[
            ConversationKey, tuple[asyncio.Lock, int]
        ] = {}
        defaults = AISettings(
            reasoning_effort=GROQ_REASONING_EFFORT,
            max_completion_tokens=GROQ_MAX_COMPLETION_TOKENS,
            history_turns=GROQ_HISTORY_TURNS,
        )
        self.settings_store = settings_store or AISettingsStore(
            Path(__file__).resolve().parents[2]
            / "data"
            / "ai-settings.sqlite3",
            defaults,
        )

    async def cog_unload(self) -> None:
        await self.client.close()

    @staticmethod
    def _conversation_key(guild_id: int | None, user_id: int) -> ConversationKey:
        return (guild_id, user_id)

    @asynccontextmanager
    async def _conversation_lock(
        self, key: ConversationKey
    ) -> AsyncGenerator[None, None]:
        entry = self.conversation_locks.get(key)
        lock, references = entry if entry else (asyncio.Lock(), 0)
        self.conversation_locks[key] = (lock, references + 1)
        try:
            async with lock:
                yield
        finally:
            _, references = self.conversation_locks[key]
            if references == 1:
                del self.conversation_locks[key]
            else:
                self.conversation_locks[key] = (lock, references - 1)

    @staticmethod
    def _response_chunks(response: str) -> list[str]:
        chunks = []
        while len(response) > MAX_EMBED_DESCRIPTION:
            split_at = response.rfind("\n", 0, MAX_EMBED_DESCRIPTION)
            if split_at < MAX_EMBED_DESCRIPTION // 2:
                split_at = response.rfind(" ", 0, MAX_EMBED_DESCRIPTION)
            if split_at < MAX_EMBED_DESCRIPTION // 2:
                split_at = MAX_EMBED_DESCRIPTION
            else:
                split_at += 1
            chunks.append(response[:split_at])
            response = response[split_at:]
        chunks.append(response)
        return chunks

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        bot_user = self.bot.user
        if bot_user is None or (not is_dm and bot_user not in message.mentions):
            return

        prompt = message.content
        if not is_dm:
            prompt = re.sub(rf"<@!?{bot_user.id}>", "", prompt)
        prompt = prompt.strip()
        if not prompt:
            await message.reply(
                embed=info_embed(
                    "Ask me something",
                    "Mention me followed by a question, or send me a direct message.",
                    self.bot,
                ),
                mention_author=False,
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        guild_id = message.guild.id if message.guild else None
        key = self._conversation_key(guild_id, message.author.id)
        settings = self.settings_store.get(guild_id) if guild_id else self.settings_store.defaults

        async with message.channel.typing():
            response, usage = await self._generate_response(key, prompt, settings)

        if response is None:
            await message.reply(
                embed=error_embed(
                    "AI unavailable",
                    "I couldn't get a response from the AI service. Please try again.",
                    self.bot,
                ),
                mention_author=False,
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        chunks = self._response_chunks(response)
        for index, chunk in enumerate(chunks):
            embed = info_embed("ScooVice AI", chunk, self.bot)
            if index == 0:
                embed.set_footer(text=f"Reply to {message.author.display_name}")
            if index == len(chunks) - 1 and usage:
                completion_details = getattr(usage, "completion_tokens_details", None)
                reasoning_tokens = getattr(completion_details, "reasoning_tokens", 0)
                usage_text = (
                    f"Input {usage.prompt_tokens} · Output {usage.completion_tokens}"
                )
                if reasoning_tokens:
                    usage_text += f" · Reasoning {reasoning_tokens}"
                embed.set_footer(text=usage_text)

            allowed_mentions = discord.AllowedMentions.none()
            if index == 0:
                await message.reply(
                    embed=embed,
                    view=ClearChatView(self, key, message.author.id),
                    mention_author=False,
                    allowed_mentions=allowed_mentions,
                )
            else:
                await message.channel.send(
                    embed=embed,
                    allowed_mentions=allowed_mentions,
                )

    async def _generate_response(
        self,
        key: ConversationKey,
        prompt: str,
        settings: AISettings,
    ) -> tuple[str | None, object | None]:
        async with self._conversation_lock(key):
            conversation = self.conversations.setdefault(key, [])
            self.conversations.move_to_end(key)
            max_history_messages = settings.history_turns * 2
            if len(conversation) > max_history_messages:
                del conversation[:-max_history_messages]
            conversation.append({"role": "user", "content": prompt})

            try:
                response = await self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[SYSTEM_PROMPT, *conversation],
                    max_completion_tokens=settings.max_completion_tokens,
                    reasoning_effort=settings.reasoning_effort,
                )
            except APIError:
                conversation.pop()
                if not conversation:
                    self.conversations.pop(key, None)
                logger.exception("Groq request failed for user %s", key[1])
                return None, None

            answer = response.choices[0].message.content
            if not answer:
                conversation.pop()
                if not conversation:
                    self.conversations.pop(key, None)
                logger.warning("Groq returned an empty answer for user %s", key[1])
                return None, response.usage

            conversation.append({"role": "assistant", "content": answer})
            while len(self.conversations) > MAX_CONVERSATIONS:
                self.conversations.popitem(last=False)
            return answer, response.usage

    @app_commands.command(name="clear_chat", description="Clear your AI conversation")
    async def clear_chat(self, interaction: discord.Interaction) -> None:
        key = self._conversation_key(
            interaction.guild_id,
            interaction.user.id,
        )
        async with self._conversation_lock(key):
            self.conversations.pop(key, None)
        await interaction.response.send_message(
            embed=info_embed(
                "Chat cleared",
                "Your conversation history has been deleted.",
                self.bot,
            ),
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AI(bot))
