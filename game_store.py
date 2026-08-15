import json
import os
from typing import TYPE_CHECKING

import psycopg
from psycopg.errors import UniqueViolation
from psycopg.types.json import Jsonb

if TYPE_CHECKING:
    from game import Game


class GameStoreError(Exception):
    pass


class GameNotFound(GameStoreError):
    pass


class GameVersionConflict(GameStoreError):
    pass


SCHEMA = """
CREATE TABLE IF NOT EXISTS chess_games (
    game_code INTEGER PRIMARY KEY,
    state JSONB NOT NULL,
    version INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""


def _connect():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise GameStoreError("DATABASE_URL must be configured")
    return psycopg.connect(database_url)


def _ensure_schema(connection):
    with connection.cursor() as cursor:
        cursor.execute(SCHEMA)


def create_game(game: "Game") -> bool:
    try:
        with _connect() as connection:
            _ensure_schema(connection)
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO chess_games (game_code, state) VALUES (%s, %s)",
                    (game.gamecode, Jsonb(game.to_state())),
                )
        game.version = 0
        return True
    except UniqueViolation:
        return False


def save_game(game: "Game") -> None:
    with _connect() as connection:
        _ensure_schema(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE chess_games
                SET state = %s, version = version + 1, updated_at = NOW()
                WHERE game_code = %s AND version = %s
                RETURNING version
                """,
                (Jsonb(game.to_state()), game.gamecode, game.version),
            )
            row = cursor.fetchone()
    if row is None:
        raise GameVersionConflict("The game changed before this request could be saved")
    game.version = row[0]


def load_game(game_code: int) -> "Game":
    with _connect() as connection:
        _ensure_schema(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT state, version FROM chess_games WHERE game_code = %s",
                (game_code,),
            )
            row = cursor.fetchone()
    if row is None:
        raise GameNotFound("No saved game found")

    state, version = row
    if isinstance(state, str):
        state = json.loads(state)
    from game import Game

    return Game.from_state(state, version)