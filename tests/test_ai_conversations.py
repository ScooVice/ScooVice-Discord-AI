import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

os.environ.setdefault("DISCORD_TOKEN", "test-token")
os.environ.setdefault("GROQ_API_KEY", "test-key")

from bot.cogs.ai import AI
from bot.config import GROQ_MODEL


def make_interaction(user_id: int, guild_id: int):
    user = SimpleNamespace(id=user_id, display_name=f"user-{user_id}")
    return SimpleNamespace(
        guild_id=guild_id,
        user=user,
        response=SimpleNamespace(defer=AsyncMock()),
        followup=SimpleNamespace(send=AsyncMock()),
    )


class AIConversationTests(unittest.IsolatedAsyncioTestCase):
    def test_long_responses_are_split_within_embed_limits(self):
        response = "word " * 2_000
        chunks = AI._response_chunks(response)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 4_000 for chunk in chunks))
        self.assertEqual("".join(chunks), response)

    async def test_chat_uses_configured_model_and_isolates_server_history(self):
        bot = SimpleNamespace(
            user=SimpleNamespace(
                name="ScooVice",
                display_avatar=SimpleNamespace(
                    url="https://example.invalid/avatar.png"
                ),
            )
        )
        cog = AI(bot)
        await cog.client.close()

        response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Hello!"))]
        )
        create_completion = AsyncMock(return_value=response)
        cog.client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=create_completion)
            )
        )

        first_server = make_interaction(user_id=5, guild_id=10)
        second_server = make_interaction(user_id=5, guild_id=20)
        await AI.chat.callback(cog, first_server, "first")
        await AI.chat.callback(cog, second_server, "second")

        self.assertEqual(create_completion.await_count, 2)
        self.assertEqual(create_completion.await_args_list[0].kwargs["model"], GROQ_MODEL)
        self.assertEqual(
            [message["content"] for message in create_completion.await_args_list[1].kwargs["messages"][1:]],
            ["second"],
        )
        self.assertIn((10, 5), cog.conversations)
        self.assertIn((20, 5), cog.conversations)


if __name__ == "__main__":
    unittest.main()
