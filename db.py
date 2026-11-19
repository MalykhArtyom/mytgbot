import sqlite3
from contextlib import closing

DB_PATH = "bot.db"


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                task TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        conn.commit()


def save_user(user_id: int, username: str | None, first_name: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username, first_name),
        )
        conn.commit()


def save_request(user_id: int, name: str, task: str) -> int:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            "INSERT INTO requests (user_id, name, task) VALUES (?, ?, ?)",
            (user_id, name, task),
        )
        conn.commit()
        return cur.lastrowid
def get_last_requests(limit: int = 10):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            "SELECT id, name, task, user_id, created_at "
            "FROM requests ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()