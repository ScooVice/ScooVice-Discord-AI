import asyncio
import logging
import discord
from discord import app_commands
from discord.ext import commands
import httpx
from groq import APIError, AsyncGroq
from bot.config import GROQ_API_KEY, GROQ_MODEL
from bot.utils.embeds import info_embed, error_embed


logger = logging.getLogger(__name__)


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        http_client = httpx.AsyncClient(trust_env=False)
        self.client = AsyncGroq(api_key=GROQ_API_KEY, http_client=http_client)
        self.conversations = {}
        self.conversation_locks = {}

    async def cog_unload(self):
        await self.client.close()

    def _conversation_key(self, interaction: discord.Interaction) -> tuple:
        return (interaction.guild_id, interaction.user.id)

    def _get_lock(self, key: tuple) -> asyncio.Lock:
        if key not in self.conversation_locks:
            self.conversation_locks[key] = asyncio.Lock()
        return self.conversation_locks[key]

    @app_commands.command(name="chat", description="Chat with AI assistant")
    async def chat(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(thinking=True)
        key = self._conversation_key(interaction)
        lock = self._get_lock(key)

        async with lock:
            conversation = self.conversations.setdefault(key, [])
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

            embed = info_embed("ScooVice AI", ai_response, self.bot)
            embed.set_footer(text=f"Chat with {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="clear_chat", description="Clear your chat history with AI")
    async def clear_chat(self, interaction: discord.Interaction):
        key = self._conversation_key(interaction)
        async with self._get_lock(key):
            self.conversations.pop(key, None)
        await interaction.response.send_message(embed=info_embed("Chat Cleared", "Your conversation history has been cleared.", self.bot), ephemeral=True)


async def setup(bot):
    await bot.add_cog(AI(bot))