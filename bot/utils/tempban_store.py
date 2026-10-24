import sqlite3
from contextlib import closing
from pathlib import Path


class TempBanStore:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS temporary_bans (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    PRIMARY KEY (guild_id, user_id)
                )
                """
            )
            connection.commit()

    def schedule(self, guild_id: int, user_id: int, expires_at: int) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO temporary_bans (guild_id, user_id, expires_at)
                VALUES (?, ?, ?)
                """,
                (guild_id, user_id, expires_at),
            )
            connection.commit()

    def remove(self, guild_id: int, user_id: int) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.execute(
                "DELETE FROM temporary_bans WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id),
            )
            connection.commit()

    def expired(self, now: int) -> list[tuple[int, int]]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            rows = connection.execute(
                """
                SELECT guild_id, user_id
                FROM temporary_bans
                WHERE expires_at <= ?
                ORDER BY expires_at
                """,
                (now,),
            ).fetchall()
        return [(int(guild_id), int(user_id)) for guild_id, user_id in rows]
