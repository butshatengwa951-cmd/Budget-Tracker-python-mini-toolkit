import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "productivity.db"

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS transactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      type TEXT NOT NULL CHECK(type IN ('income','expense')),
      amount REAL NOT NULL,
      category TEXT NOT NULL,
      note TEXT DEFAULT '',
      date TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS tasks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      priority TEXT NOT NULL DEFAULT 'medium',
      done INTEGER NOT NULL DEFAULT 0,
      created TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS study_sessions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      subject TEXT NOT NULL,
      duration INTEGER NOT NULL,
      date TEXT NOT NULL,
      done INTEGER NOT NULL DEFAULT 0
    );
    """)
    db.commit()
    db.close()
