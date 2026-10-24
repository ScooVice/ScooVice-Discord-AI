import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from bot.cogs.core import Core


class CoreHelpTests(unittest.IsolatedAsyncioTestCase):
    async def test_help_shows_current_ai_voice_and_moderation_controls(self):
        interaction = SimpleNamespace(
            response=SimpleNamespace(defer=AsyncMock()),
            followup=SimpleNamespace(send=AsyncMock()),
        )
        cog = Core(SimpleNamespace(user=None))

        await Core.help.callback(cog, interaction)

        interaction.response.defer.assert_awaited_once()
        embed = interaction.followup.send.await_args.kwargs["embed"]
        field_text = "\n".join(field.value for field in embed.fields)
        self.assertIn("Mention me with a message", field_text)
        self.assertIn("/clear_chat", field_text)
        self.assertIn("/settings", field_text)
        self.assertIn("/voice", field_text)
        self.assertIn("/tempban", field_text)


if __name__ == "__main__":
    unittest.main()
