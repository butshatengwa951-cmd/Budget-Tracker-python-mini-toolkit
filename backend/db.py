import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "productivity.db"

VALID_FREQUENCIES = ("daily", "weekly", "monthly", "yearly")


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def period_dates(day, frequency):
    if frequency == "daily":
        return day, day

    if frequency == "weekly":
        start = day - timedelta(days=day.weekday())
        return start, start + timedelta(days=6)

    if frequency == "monthly":
        start = day.replace(day=1)
        if day.month == 12:
            next_start = date(day.year + 1, 1, 1)
        else:
            next_start = date(day.year, day.month + 1, 1)
        return start, next_start - timedelta(days=1)

    if frequency == "yearly":
        start = date(day.year, 1, 1)
        return start, date(day.year, 12, 31)

    raise ValueError(f"Unsupported budget frequency: {frequency}")


def ensure_column(db, table, column, definition):
    columns = {row["name"] for row in db.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    db = get_db()

    db.executescript("""
    CREATE TABLE IF NOT EXISTS transactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      type TEXT NOT NULL CHECK(type IN ('income','expense')),
      amount REAL NOT NULL,
      category TEXT NOT NULL,
      note TEXT DEFAULT '',
      date TEXT NOT NULL,
      period_id INTEGER
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

    CREATE TABLE IF NOT EXISTS settings (
      id INTEGER PRIMARY KEY CHECK(id = 1),
      reset_frequency TEXT NOT NULL DEFAULT 'monthly',
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS budget_periods (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      frequency TEXT NOT NULL,
      start_date TEXT NOT NULL,
      end_date TEXT NOT NULL,
      is_current INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      closed_at TEXT,
      UNIQUE(frequency, start_date)
    );

    INSERT OR IGNORE INTO settings (id, reset_frequency)
    VALUES (1, 'monthly');
    """)

    ensure_column(db, "transactions", "period_id", "INTEGER")

    frequency = db.execute(
        "SELECT reset_frequency FROM settings WHERE id=1"
    ).fetchone()["reset_frequency"]

    if frequency not in VALID_FREQUENCIES:
        frequency = "monthly"
        db.execute(
            "UPDATE settings SET reset_frequency='monthly', updated_at=CURRENT_TIMESTAMP WHERE id=1"
        )

    # Give existing transactions a permanent home in budget history.
    legacy_rows = db.execute(
        "SELECT id, date FROM transactions WHERE period_id IS NULL ORDER BY date, id"
    ).fetchall()

    for row in legacy_rows:
        try:
            transaction_day = date.fromisoformat(str(row["date"])[:10])
        except ValueError:
            transaction_day = date.today()

        start, end = period_dates(transaction_day, frequency)
        db.execute(
            """
            INSERT OR IGNORE INTO budget_periods
              (frequency, start_date, end_date, is_current)
            VALUES (?, ?, ?, 0)
            """,
            (frequency, start.isoformat(), end.isoformat())
        )
        period_id = db.execute(
            """
            SELECT id FROM budget_periods
            WHERE frequency=? AND start_date=?
            """,
            (frequency, start.isoformat())
        ).fetchone()["id"]
        db.execute(
            "UPDATE transactions SET period_id=? WHERE id=?",
            (period_id, row["id"])
        )

    db.commit()
    db.close()


def get_setting(db, key="reset_frequency"):
    if key == "reset_frequency":
        row = db.execute(
            "SELECT reset_frequency FROM settings WHERE id=1"
        ).fetchone()
        return row["reset_frequency"] if row else "monthly"
    return None


def ensure_current_period(db):
    frequency = get_setting(db)
    today = date.today()
    start, end = period_dates(today, frequency)

    db.execute(
        "UPDATE budget_periods SET is_current=0 WHERE is_current=1"
    )
    db.execute(
        """
        INSERT OR IGNORE INTO budget_periods
          (frequency, start_date, end_date, is_current)
        VALUES (?, ?, ?, 1)
        """,
        (frequency, start.isoformat(), end.isoformat())
    )

    db.execute(
        """
        UPDATE budget_periods
        SET is_current=CASE WHEN frequency=? AND start_date=? THEN 1 ELSE 0 END,
            closed_at=CASE
              WHEN frequency=? AND start_date=? THEN NULL
              WHEN closed_at IS NULL AND end_date < ? THEN CURRENT_TIMESTAMP
              ELSE closed_at
            END
        """,
        (
            frequency,
            start.isoformat(),
            frequency,
            start.isoformat(),
            today.isoformat(),
        )
    )

    row = db.execute(
        """
        SELECT * FROM budget_periods
        WHERE frequency=? AND start_date=?
        """,
        (frequency, start.isoformat())
    ).fetchone()

    db.commit()
    return row


def get_period_summary(db, period_id):
    period = db.execute(
        "SELECT * FROM budget_periods WHERE id=?", (period_id,)
    ).fetchone()
    if not period:
        return None

    start = period["start_date"]
    end = period["end_date"]

    income = db.execute(
        """
        SELECT COALESCE(SUM(amount),0) FROM transactions
        WHERE period_id=? AND type='income'
        """,
        (period_id,),
    ).fetchone()[0]

    expenses = db.execute(
        """
        SELECT COALESCE(SUM(amount),0) FROM transactions
        WHERE period_id=? AND type='expense'
        """,
        (period_id,),
    ).fetchone()[0]

    recent = db.execute(
        """
        SELECT * FROM transactions
        WHERE period_id=?
        ORDER BY date DESC, id DESC
        LIMIT 8
        """,
        (period_id,),
    ).fetchall()

    categories = db.execute(
        """
        SELECT category, COALESCE(SUM(amount),0) AS total
        FROM transactions
        WHERE period_id=? AND type='expense'
        GROUP BY category
        ORDER BY total DESC
        """,
        (period_id,),
    ).fetchall()

    return {
        "id": period["id"],
        "frequency": period["frequency"],
        "startDate": start,
        "endDate": end,
        "isCurrent": bool(period["is_current"]),
        "income": income,
        "expenses": expenses,
        "balance": income - expenses,
        "transactionCount": db.execute(
            "SELECT COUNT(*) FROM transactions WHERE period_id=?",
            (period_id,),
        ).fetchone()[0],
        "recentTransactions": [dict(row) for row in recent],
        "categories": [dict(row) for row in categories],
    }
