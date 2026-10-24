import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import discord
from discord import app_commands
from discord.ext import commands

from bot.main import ScooViceCommandTree


class CommandErrorTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_permissions_return_clear_ephemeral_error(self):
        bot = commands.Bot(
            command_prefix="!",
            intents=discord.Intents.none(),
            tree_cls=ScooViceCommandTree,
        )
        response = SimpleNamespace(
            is_done=Mock(return_value=False),
            send_message=AsyncMock(),
        )
        interaction = SimpleNamespace(
            response=response,
            followup=SimpleNamespace(send=AsyncMock()),
        )

        await bot.tree.on_error(
            interaction,
            app_commands.MissingPermissions(["ban_members"]),
        )

        response.send_message.assert_awaited_once()
        sent_embed = response.send_message.await_args.kwargs["embed"]
        self.assertEqual(sent_embed.title, "⛔  Command Error")
        self.assertIn("ban_members", sent_embed.description)
        self.assertTrue(response.send_message.await_args.kwargs["ephemeral"])
        await bot.close()

    async def test_generic_failure_uses_private_nontechnical_response(self):
        bot = commands.Bot(
            command_prefix="!",
            intents=discord.Intents.none(),
            tree_cls=ScooViceCommandTree,
        )
        response = SimpleNamespace(
            is_done=Mock(return_value=True),
            send_message=AsyncMock(),
        )
        followup = SimpleNamespace(send=AsyncMock())
        interaction = SimpleNamespace(response=response, followup=followup)

        await bot.tree.on_error(
            interaction,
            app_commands.CommandInvokeError(
                SimpleNamespace(name="test"),
                RuntimeError("private detail"),
            ),
        )

        followup.send.assert_awaited_once()
        sent_embed = followup.send.await_args.kwargs["embed"]
        self.assertNotIn("private detail", sent_embed.description)
        self.assertTrue(followup.send.await_args.kwargs["ephemeral"])
        await bot.close()


if __name__ == "__main__":
    unittest.main()
