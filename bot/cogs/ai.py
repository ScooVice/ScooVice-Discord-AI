import asyncio
import logging
from collections import OrderedDict
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import discord
from discord import app_commands
from discord.ext import commands
import httpx
from groq import APIError, AsyncGroq
from bot.config import GROQ_API_KEY, GROQ_MODEL
from bot.utils.embeds import info_embed, error_embed


logger = logging.getLogger(__name__)
ConversationKey = tuple[int | None, int]
MAX_CONVERSATIONS = 5_000
MAX_EMBED_DESCRIPTION = 4_000


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        http_client = httpx.AsyncClient(trust_env=False)
        self.client = AsyncGroq(api_key=GROQ_API_KEY, http_client=http_client)
        self.conversations: OrderedDict[ConversationKey, list[dict[str, str]]] = (
            OrderedDict()
        )
        self.conversation_locks: dict[
            ConversationKey, tuple[asyncio.Lock, int]
        ] = {}

    async def cog_unload(self):
        await self.client.close()

    def _conversation_key(
        self, interaction: discord.Interaction
    ) -> ConversationKey:
        return (interaction.guild_id, interaction.user.id)

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

    @app_commands.command(name="chat", description="Chat with AI assistant")
    async def chat(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(thinking=True)
        key = self._conversation_key(interaction)
        async with self._conversation_lock(key):
            conversation = self.conversations.setdefault(key, [])
            self.conversations.move_to_end(key)
            conversation.append({"role": "user", "content": message})

            system_prompt = {
                "role": "system",
                "content": (
                    "You are ScooVice AI, a helpful and friendly Discord bot "
                    "assistant. Keep responses concise and engaging. You can help "
                    "with Discord-related questions and general chat."
                ),
            }

            try:
                response = await self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[system_prompt, *conversation],
                    max_completion_tokens=500,
                    temperature=0.7,
                )
            except APIError:
                conversation.pop()
                if not conversation:
                    self.conversations.pop(key, None)
                logger.exception("Groq request failed for user %s", interaction.user.id)
                await interaction.followup.send(
                    embed=error_embed(
                        "AI Error",
                        "The AI service could not respond. Please try again later.",
                        self.bot,
                    ),
                    ephemeral=True,
                )
                return

            ai_response = response.choices[0].message.content
            if not ai_response:
                conversation.pop()
                if not conversation:
                    self.conversations.pop(key, None)
                logger.error(
                    "Groq returned an empty response for user %s",
                    interaction.user.id,
                )
                await interaction.followup.send(
                    embed=error_embed(
                        "AI Error",
                        "The AI service returned an empty response. Please try again.",
                        self.bot,
                    ),
                    ephemeral=True,
                )
                return

            conversation.append({"role": "assistant", "content": ai_response})
            if len(conversation) > 20:
                del conversation[:2]
            while len(self.conversations) > MAX_CONVERSATIONS:
                self.conversations.popitem(last=False)

            for chunk in self._response_chunks(ai_response):
                embed = info_embed("ScooVice AI", chunk, self.bot)
                embed.set_footer(text=f"Chat with {interaction.user.display_name}")
                await interaction.followup.send(embed=embed)

    @app_commands.command(name="clear_chat", description="Clear your chat history with AI")
    async def clear_chat(self, interaction: discord.Interaction):
        key = self._conversation_key(interaction)
        async with self._conversation_lock(key):
            self.conversations.pop(key, None)
        await interaction.response.send_message(embed=info_embed("Chat Cleared", "Your conversation history has been cleared.", self.bot), ephemeral=True)


async def setup(bot):
    await bot.add_cog(AI(bot))