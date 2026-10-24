import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AISettings:
    reasoning_effort: str
    max_completion_tokens: int
    history_turns: int


class AISettingsStore:
    def __init__(self, database_path: Path, defaults: AISettings) -> None:
        self.database_path = database_path
        self.defaults = defaults
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_server_settings (
                    guild_id INTEGER PRIMARY KEY,
                    reasoning_effort TEXT NOT NULL,
                    max_completion_tokens INTEGER NOT NULL,
                    history_turns INTEGER NOT NULL
                )
                """
            )
            connection.commit()

    def get(self, guild_id: int) -> AISettings:
        with closing(sqlite3.connect(self.database_path)) as connection:
            row = connection.execute(
                """
                SELECT reasoning_effort, max_completion_tokens, history_turns
                FROM ai_server_settings
                WHERE guild_id = ?
                """,
                (guild_id,),
            ).fetchone()
        if row is None:
            return self.defaults
        return AISettings(
            reasoning_effort=str(row[0]),
            max_completion_tokens=int(row[1]),
            history_turns=int(row[2]),
        )

    def update(self, guild_id: int, setting: str, value: str | int) -> AISettings:
        columns = {
            "reasoning_effort": {"low", "medium", "high"},
            "max_completion_tokens": {256, 512, 1024, 2048},
            "history_turns": {2, 5, 10},
        }
        if setting not in columns or value not in columns[setting]:
            raise ValueError(f"Unsupported AI setting: {setting}={value}")

        current = self.get(guild_id)
        values: dict[str, str | int] = {
            "reasoning_effort": current.reasoning_effort,
            "max_completion_tokens": current.max_completion_tokens,
            "history_turns": current.history_turns,
        }
        values[setting] = value
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.execute(
                """
                INSERT INTO ai_server_settings (
                    guild_id, reasoning_effort, max_completion_tokens, history_turns
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                    reasoning_effort = excluded.reasoning_effort,
                    max_completion_tokens = excluded.max_completion_tokens,
                    history_turns = excluded.history_turns
                """,
                (
                    guild_id,
                    values["reasoning_effort"],
                    values["max_completion_tokens"],
                    values["history_turns"],
                ),
            )
            connection.commit()
        return AISettings(
            reasoning_effort=str(values["reasoning_effort"]),
            max_completion_tokens=int(values["max_completion_tokens"]),
            history_turns=int(values["history_turns"]),
        )

    def reset(self, guild_id: int) -> AISettings:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.execute(
                "DELETE FROM ai_server_settings WHERE guild_id = ?",
                (guild_id,),
            )
            connection.commit()
        return self.defaults
