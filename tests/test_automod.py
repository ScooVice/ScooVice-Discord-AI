import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from bot.cogs.automod import AutoMod


def make_message(content: str, user_id: int = 42):
    author = SimpleNamespace(
        bot=False,
        id=user_id,
        mention=f"<@{user_id}>",
        guild_permissions=SimpleNamespace(manage_messages=False),
    )
    channel = SimpleNamespace(id=7, send=AsyncMock())
    message = SimpleNamespace(
        author=author,
        guild=SimpleNamespace(id=5),
        channel=channel,
        content=content,
        id=user_id * 100,
        delete=AsyncMock(),
    )
    return message


class AutoModTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.automod = AutoMod(
            SimpleNamespace(command_prefix="!", user=None)
        )

    async def test_banned_words_match_whole_words(self):
        self.automod.banned_words = ("test",)
        message = make_message("This is a contest.")

        await self.automod.on_message(message)

        message.delete.assert_not_awaited()
        message.channel.send.assert_not_awaited()

    async def test_spam_rule_removes_the_sixth_message(self):
        messages = [make_message("hello") for _ in range(6)]

        for message in messages:
            await self.automod.on_message(message)

        for message in messages[:5]:
            message.delete.assert_not_awaited()
        messages[5].delete.assert_awaited_once()
        messages[5].channel.send.assert_awaited_once()

    async def test_link_filter_is_disabled_by_default(self):
        self.assertFalse(self.automod.block_links)
        message = make_message("Here is a link: https://example.com")

        await self.automod.on_message(message)

        message.delete.assert_not_awaited()

    async def test_prefix_commands_are_not_counted_as_spam(self):
        messages = [make_message("!help") for _ in range(6)]

        for message in messages:
            await self.automod.on_message(message)

        self.assertEqual(self.automod.user_messages, {})
        for message in messages:
            message.delete.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
