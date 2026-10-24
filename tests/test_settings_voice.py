import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import discord

from bot.cogs.settings import AISettingsView
from bot.cogs.voice import VoicePanel
from bot.utils.ai_settings_store import AISettings, AISettingsStore


class SettingsVoiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.defaults = AISettings("low", 512, 5)
        self.store = AISettingsStore(
            Path(self.temp_directory.name) / "settings.sqlite3",
            self.defaults,
        )
        self.bot = SimpleNamespace(user=None)

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_server_settings_persist_independently_and_reset(self):
        self.store.update(10, "reasoning_effort", "high")
        self.store.update(10, "max_completion_tokens", 2048)
        self.store.update(20, "history_turns", 2)

        self.assertEqual(self.store.get(10), AISettings("high", 2048, 5))
        self.assertEqual(self.store.get(20), AISettings("low", 512, 2))
        self.assertEqual(self.store.reset(10), self.defaults)
        self.assertEqual(self.store.get(10), self.defaults)

    def test_server_settings_reject_unsupported_values(self):
        with self.assertRaises(ValueError):
            self.store.update(10, "reasoning_effort", "turbo")

    async def test_settings_panel_contains_all_controls_and_denies_non_managers(self):
        view = AISettingsView(self.store, 10, self.bot)
        selects = [
            item for item in view.children if isinstance(item, discord.ui.Select)
        ]
        buttons = [
            item
            for item in view.children
            if isinstance(item, discord.ui.Button) and item.label == "Reset defaults"
        ]

        self.assertEqual(len(selects), 3)
        self.assertEqual(len(buttons), 1)
        self.assertEqual(
            [[option.value for option in item.options] for item in selects],
            [
                ["low", "medium", "high"],
                ["256", "512", "1024", "2048"],
                ["2", "5", "10"],
            ],
        )

        response = SimpleNamespace(send_message=AsyncMock())
        interaction = SimpleNamespace(
            guild_id=10,
            user=SimpleNamespace(),
            response=response,
        )
        self.assertFalse(await view.interaction_check(interaction))
        response.send_message.assert_awaited_once()

    async def test_voice_panel_handles_join_and_leave_without_channel(self):
        view = VoicePanel(self.bot)
        join_button = next(item for item in view.children if item.label == "Join my voice")
        leave_button = next(item for item in view.children if item.label == "Leave voice")

        join_response = SimpleNamespace(send_message=AsyncMock())
        join_interaction = SimpleNamespace(
            guild=SimpleNamespace(),
            user=SimpleNamespace(voice=None),
            response=join_response,
        )
        await join_button.callback(join_interaction)
        join_response.send_message.assert_awaited_once()

        leave_response = SimpleNamespace(send_message=AsyncMock())
        leave_interaction = SimpleNamespace(
            guild=SimpleNamespace(voice_client=None),
            response=leave_response,
        )
        await leave_button.callback(leave_interaction)
        leave_response.send_message.assert_awaited_once()

    async def test_voice_panel_joins_and_disconnects_with_expected_controls(self):
        view = VoicePanel(self.bot)
        join_button = next(item for item in view.children if item.label == "Join my voice")
        leave_button = next(item for item in view.children if item.label == "Leave voice")

        channel = SimpleNamespace(
            id=30,
            name="General",
            permissions_for=Mock(return_value=SimpleNamespace(connect=True)),
            connect=AsyncMock(),
        )
        member = Mock(spec=discord.Member)
        member.voice = SimpleNamespace(channel=channel)
        member.guild_permissions = SimpleNamespace(manage_channels=False)
        guild = SimpleNamespace(
            id=10,
            me=SimpleNamespace(),
            voice_client=None,
        )
        join_response = SimpleNamespace(send_message=AsyncMock())
        join_interaction = SimpleNamespace(
            guild=guild,
            user=member,
            response=join_response,
        )

        await join_button.callback(join_interaction)

        channel.connect.assert_awaited_once_with(self_deaf=True)
        join_response.send_message.assert_awaited_once()

        voice_client = SimpleNamespace(
            channel=channel,
            disconnect=AsyncMock(),
        )
        guild.voice_client = voice_client
        leave_response = SimpleNamespace(send_message=AsyncMock())
        leave_interaction = SimpleNamespace(
            guild=guild,
            user=member,
            response=leave_response,
        )

        await leave_button.callback(leave_interaction)

        voice_client.disconnect.assert_awaited_once_with(force=True)
        leave_response.send_message.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
