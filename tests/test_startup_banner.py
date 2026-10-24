import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from bot.main import print_startup_banner


class StartupBannerTests(unittest.TestCase):
    def test_banner_shows_bot_runtime_and_voice_status(self):
        bot = SimpleNamespace(
            user=SimpleNamespace(name="ScooVice Bot"),
            guilds=[object(), object()],
        )
        output = io.StringIO()

        with redirect_stdout(output):
            print_startup_banner(bot, command_count=11)

        banner = output.getvalue()
        self.assertIn("ScooVice Bot", banner)
        self.assertIn("Online", banner)
        self.assertIn("2", banner)
        self.assertIn("11 synced", banner)
        self.assertIn("DAVE + PyNaCl", banner)
        self.assertIn("Ctrl+C", banner)


if __name__ == "__main__":
    unittest.main()
