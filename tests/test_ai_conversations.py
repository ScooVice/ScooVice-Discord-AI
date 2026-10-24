import os
import tempfile
import unittest
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

os.environ.setdefault("DISCORD_TOKEN", "test-token")
os.environ.setdefault("GROQ_API_KEY", "test-key")

from bot.cogs.ai import AI
from bot.config import GROQ_MODEL
from bot.utils.ai_settings_store import AISettings, AISettingsStore


@asynccontextmanager
async def fake_typing():
    yield


def make_bot():
    return SimpleNamespace(
        user=SimpleNamespace(
            id=123,
            name="ScooVice",
            display_avatar=SimpleNamespace(
                url="https://example.invalid/avatar.png"
            ),
        )
    )


def make_message(bot, user_id: int, guild_id: int):
    user = SimpleNamespace(
        id=user_id,
        bot=False,
        display_name=f"user-{user_id}",
    )
    guild = SimpleNamespace(id=guild_id)
    channel = SimpleNamespace(
        typing=fake_typing,
        send=AsyncMock(),
    )
    return SimpleNamespace(
        author=user,
        guild=guild,
        channel=channel,
        mentions=[bot.user],
        content=f"<@{bot.user.id}> hello",
        reply=AsyncMock(),
    )


class AIConversationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.defaults = AISettings("low", 512, 5)
        self.store = AISettingsStore(
            Path(self.temp_directory.name) / "settings.sqlite3",
            self.defaults,
        )

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_long_responses_are_split_without_loss(self):
        response = "word " * 2_000
        chunks = AI._response_chunks(response)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 4_000 for chunk in chunks))
        self.assertEqual("".join(chunks), response)

    async def test_mentions_use_configured_effort_tokens_and_isolate_servers(self):
        bot = make_bot()
        cog = AI(bot, settings_store=self.store)
        await cog.client.close()

        usage = SimpleNamespace(
            prompt_tokens=37,
            completion_tokens=18,
            completion_tokens_details=SimpleNamespace(reasoning_tokens=6),
        )
        response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Hello!"))],
            usage=usage,
        )
        create_completion = AsyncMock(return_value=response)
        cog.client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=create_completion)
            )
        )

        self.store.update(10, "reasoning_effort", "low")
        self.store.update(10, "max_completion_tokens", 256)
        first_server = make_message(bot, user_id=5, guild_id=10)
        second_server = make_message(bot, user_id=5, guild_id=20)
        await cog.on_message(first_server)
        await cog.on_message(second_server)

        first_request = create_completion.await_args_list[0].kwargs
        self.assertEqual(first_request["model"], GROQ_MODEL)
        self.assertEqual(first_request["reasoning_effort"], "low")
        self.assertEqual(first_request["max_completion_tokens"], 256)
        self.assertEqual(
            [
                item["content"]
                for item in create_completion.await_args_list[1].kwargs["messages"][1:]
            ],
            ["hello"],
        )
        first_server.reply.assert_awaited_once()
        first_embed = first_server.reply.await_args.kwargs["embed"]
        self.assertIn("Input 37", first_embed.footer.text)
        self.assertIn("Reasoning 6", first_embed.footer.text)

    async def test_unmentioned_server_message_is_ignored(self):
        bot = make_bot()
        cog = AI(bot, settings_store=self.store)
        await cog.client.close()
        message = make_message(bot, user_id=5, guild_id=10)
        message.mentions = []

        await cog.on_message(message)

        message.reply.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
