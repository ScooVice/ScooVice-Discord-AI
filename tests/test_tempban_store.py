import tempfile
import unittest
from pathlib import Path

from bot.utils.tempban_store import TempBanStore


class TempBanStoreTests(unittest.TestCase):
    def test_expired_bans_survive_store_recreation(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "tempbans.sqlite3"
            store = TempBanStore(database_path)
            store.schedule(guild_id=1, user_id=10, expires_at=100)
            store.schedule(guild_id=1, user_id=11, expires_at=200)

            reopened_store = TempBanStore(database_path)

            self.assertEqual(reopened_store.expired(now=100), [(1, 10)])

    def test_schedule_replaces_existing_expiry_and_remove_clears_it(self):
        with tempfile.TemporaryDirectory() as directory:
            store = TempBanStore(Path(directory) / "tempbans.sqlite3")
            store.schedule(guild_id=1, user_id=10, expires_at=100)
            store.schedule(guild_id=1, user_id=10, expires_at=200)

            self.assertEqual(store.expired(now=100), [])

            store.remove(guild_id=1, user_id=10)
            self.assertEqual(store.expired(now=200), [])


if __name__ == "__main__":
    unittest.main()
