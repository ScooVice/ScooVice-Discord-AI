# Clear proxy environment variables to prevent Groq client issues
import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

import discord
from discord import app_commands
from discord.ext import commands
import httpx
from groq import Groq
from bot.config import GROQ_API_KEY
from bot.utils.embeds import info_embed, error_embed


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Create httpx client without trusting environment proxies
        http_client = httpx.Client(trust_env=False)
        self.client = Groq(api_key=GROQ_API_KEY, http_client=http_client)
        self.conversations = {}  # user_id: list of messages

    def get_conversation(self, user_id):
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        return self.conversations[user_id]

    def add_message(self, user_id, role, content):
        conv = self.get_conversation(user_id)
        conv.append({"role": role, "content": content})
        # Keep only last 20 messages to avoid token limits
        if len(conv) > 20:
            conv.pop(0)

    @app_commands.command(name="chat", description="Chat with AI assistant")
    async def chat(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()

        try:
            # Add user message to conversation
            self.add_message(interaction.user.id, "user", message)

            # Get conversation history
            conversation = self.get_conversation(interaction.user.id)

            # Create system prompt
            system_prompt = {
                "role": "system",
                "content": "You are ScooVice AI, a helpful and friendly Discord bot assistant. Keep responses concise and engaging. You have access to various Discord features and can help with moderation and general chat."
            }

            messages = [system_prompt] + conversation

            # Get response from Groq
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content

            # Add AI response to conversation
            self.add_message(interaction.user.id, "assistant", ai_response)

            # Send response
            embed = info_embed("ScooVice AI", ai_response, self.bot)
            embed.set_footer(text=f"Chat with {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(embed=error_embed("AI Error", f"Failed to get AI response: {str(e)}", self.bot), ephemeral=True)

    @app_commands.command(name="clear_chat", description="Clear your chat history with AI")
    async def clear_chat(self, interaction: discord.Interaction):
        self.conversations.pop(interaction.user.id, None)
        await interaction.response.send_message(embed=info_embed("Chat Cleared", "Your conversation history has been cleared.", self.bot), ephemeral=True)


async def setup(bot):
    await bot.add_cog(AI(bot))