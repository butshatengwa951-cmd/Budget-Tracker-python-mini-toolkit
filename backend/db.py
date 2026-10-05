import os
import ssl
from datetime import date, datetime, timedelta, timezone

import pymysql
from pymysql.cursors import DictCursor

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:
    ZoneInfo = None
    ZoneInfoNotFoundError = Exception

VALID_FREQUENCIES = ("daily", "weekly", "monthly", "yearly")
VALID_TIME_UNITS = ("seconds", "minutes", "hours")


try:
    LOCAL_TZ = (
        ZoneInfo("Africa/Johannesburg")
        if ZoneInfo
        else timezone(timedelta(hours=2))
    )
except ZoneInfoNotFoundError:
    LOCAL_TZ = timezone(timedelta(hours=2))


def local_now():
    return datetime.now(LOCAL_TZ)


def local_today():
    return local_now().date()


def local_timestamp():
    return local_now().strftime("%Y-%m-%d %H:%M:%S")


def _ssl_context():
    mode = os.getenv("MYSQL_SSL_MODE", "VERIFY_CA").upper()
    ca_value = os.getenv("MYSQL_SSL_CA", "").strip()

    if mode == "DISABLED":
        return None

    if ca_value:
        if "BEGIN CERTIFICATE" in ca_value:
            return ssl.create_default_context(cadata=ca_value)
        return ssl.create_default_context(cafile=ca_value)

    if mode == "REQUIRED":
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

    raise RuntimeError(
        "MYSQL_SSL_CA is required when MYSQL_SSL_MODE is VERIFY_CA."
    )


class Database:
    def __init__(self):
        host = os.getenv("MYSQL_HOST")
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        database = os.getenv("MYSQL_DATABASE")
        port = int(os.getenv("MYSQL_PORT", "3306"))

        missing = [
            name
            for name, value in {
                "MYSQL_HOST": host,
                "MYSQL_USER": user,
                "MYSQL_PASSWORD": password,
                "MYSQL_DATABASE": database,
            }.items()
            if not value
        ]

        if missing:
            raise RuntimeError(
                "Missing MySQL configuration: " + ", ".join(missing)
            )

        connect_kwargs = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "charset": "utf8mb4",
            "cursorclass": DictCursor,
            "autocommit": False,
            "connect_timeout": 15,
            "read_timeout": 30,
            "write_timeout": 30,
        }

        ssl_context = _ssl_context()
        if ssl_context is not None:
            connect_kwargs["ssl"] = ssl_context

        self.connection = pymysql.connect(**connect_kwargs)

    def execute(self, sql, params=None):
        sql = sql.replace("?", "%s")
        sql = sql.replace("INSERT OR IGNORE", "INSERT IGNORE")
        cursor = self.connection.cursor()
        cursor.execute(sql, params or ())
        return cursor

    def executescript(self, script):
        statements = [
            statement.strip()
            for statement in script.split(";")
            if statement.strip()
        ]
        for statement in statements:
            self.execute(statement)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def get_db():
    return Database()


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
    row = db.execute(
        """
        SELECT COUNT(*) AS column_count
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA=DATABASE()
          AND TABLE_NAME=?
          AND COLUMN_NAME=?
        """,
        (table, column),
    ).fetchone()

    if row["column_count"] == 0:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    db = get_db()

    try:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS transactions (
              id INT PRIMARY KEY AUTO_INCREMENT,
              type VARCHAR(20) NOT NULL,
              amount DOUBLE NOT NULL,
              category VARCHAR(255) NOT NULL,
              note TEXT DEFAULT NULL,
              date VARCHAR(32) NOT NULL,
              period_id INT,
              CHECK(type IN ('income','expense'))
            );

            CREATE TABLE IF NOT EXISTS tasks (
              id INT PRIMARY KEY AUTO_INCREMENT,
              name VARCHAR(255) NOT NULL,
              priority VARCHAR(20) NOT NULL DEFAULT 'medium',
              done TINYINT(1) NOT NULL DEFAULT 0,
              created VARCHAR(32) NOT NULL
            );

            CREATE TABLE IF NOT EXISTS study_sessions (
              id INT PRIMARY KEY AUTO_INCREMENT,
              subject VARCHAR(255) NOT NULL,
              duration DOUBLE NOT NULL,
              date VARCHAR(32) NOT NULL,
              done TINYINT(1) NOT NULL DEFAULT 0,
              unit VARCHAR(16) NOT NULL DEFAULT 'minutes',
              duration_seconds INT NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS settings (
              id INT PRIMARY KEY,
              reset_frequency VARCHAR(20) NOT NULL DEFAULT 'monthly',
              updated_at VARCHAR(32) NOT NULL
            );

            CREATE TABLE IF NOT EXISTS budget_periods (
              id INT PRIMARY KEY AUTO_INCREMENT,
              frequency VARCHAR(20) NOT NULL,
              start_date VARCHAR(32) NOT NULL,
              end_date VARCHAR(32) NOT NULL,
              is_current TINYINT(1) NOT NULL DEFAULT 0,
              created_at VARCHAR(32) NOT NULL,
              closed_at VARCHAR(32) NULL,
              UNIQUE KEY unique_frequency_start (frequency, start_date)
            );

            INSERT IGNORE INTO settings (id, reset_frequency, updated_at)
            VALUES (1, 'monthly', ?);
            """,
            (local_timestamp(),),
        )

        ensure_column(db, "transactions", "period_id", "INT")
        ensure_column(
            db,
            "study_sessions",
            "unit",
            "VARCHAR(16) NOT NULL DEFAULT 'minutes'",
        )
        ensure_column(
            db,
            "study_sessions",
            "duration_seconds",
            "INT NOT NULL DEFAULT 0",
        )

        db.execute(
            """
            UPDATE study_sessions
            SET unit='minutes',
                duration_seconds=ROUND(duration * 60)
            WHERE duration_seconds IS NULL OR duration_seconds=0
            """
        )

        frequency_row = db.execute(
            "SELECT reset_frequency FROM settings WHERE id=1"
        ).fetchone()
        frequency = (
            frequency_row["reset_frequency"]
            if frequency_row
            else "monthly"
        )

        if frequency not in VALID_FREQUENCIES:
            frequency = "monthly"
            db.execute(
                """
                UPDATE settings
                SET reset_frequency='monthly', updated_at=?
                WHERE id=1
                """,
                (local_timestamp(),),
            )

        transaction_rows = db.execute(
            "SELECT id, date, period_id FROM transactions ORDER BY date, id"
        ).fetchall()

        for row in transaction_rows:
            try:
                transaction_day = date.fromisoformat(str(row["date"])[:10])
            except ValueError:
                transaction_day = local_today()

            transaction_frequency = frequency

            if row["period_id"]:
                period = db.execute(
                    "SELECT frequency FROM budget_periods WHERE id=?",
                    (row["period_id"],),
                ).fetchone()
                if period:
                    transaction_frequency = period["frequency"]

            start, end = period_dates(
                transaction_day,
                transaction_frequency,
            )

            db.execute(
                """
                INSERT IGNORE INTO budget_periods
                  (frequency, start_date, end_date, is_current, created_at)
                VALUES (?, ?, ?, 0, ?)
                """,
                (
                    transaction_frequency,
                    start.isoformat(),
                    end.isoformat(),
                    local_timestamp(),
                ),
            )

            period_row = db.execute(
                """
                SELECT id FROM budget_periods
                WHERE frequency=? AND start_date=?
                """,
                (
                    transaction_frequency,
                    start.isoformat(),
                ),
            ).fetchone()

            db.execute(
                "UPDATE transactions SET period_id=? WHERE id=?",
                (period_row["id"], row["id"]),
            )

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
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
    today = local_today()
    start, end = period_dates(today, frequency)
    now = local_timestamp()

    db.execute(
        "UPDATE budget_periods SET is_current=0 WHERE is_current=1"
    )

    db.execute(
        """
        INSERT IGNORE INTO budget_periods
          (frequency, start_date, end_date, is_current, created_at)
        VALUES (?, ?, ?, 1, ?)
        """,
        (
            frequency,
            start.isoformat(),
            end.isoformat(),
            now,
        ),
    )

    db.execute(
        """
        UPDATE budget_periods
        SET is_current=CASE
              WHEN frequency=? AND start_date=? THEN 1
              ELSE 0
            END,
            closed_at=CASE
              WHEN frequency=? AND start_date=? THEN NULL
              WHEN closed_at IS NULL AND end_date < ? THEN ?
              ELSE closed_at
            END
        """,
        (
            frequency,
            start.isoformat(),
            frequency,
            start.isoformat(),
            today.isoformat(),
            now,
        ),
    )

    row = db.execute(
        """
        SELECT * FROM budget_periods
        WHERE frequency=? AND start_date=?
        """,
        (frequency, start.isoformat()),
    ).fetchone()

    db.commit()
    return row


def get_period_summary(db, period_id):
    period = db.execute(
        "SELECT * FROM budget_periods WHERE id=?",
        (period_id,),
    ).fetchone()

    if not period:
        return None

    income = db.execute(
        """
        SELECT COALESCE(SUM(amount),0) AS value
        FROM transactions
        WHERE period_id=? AND type='income'
        """,
        (period_id,),
    ).fetchone()["value"]

    expenses = db.execute(
        """
        SELECT COALESCE(SUM(amount),0) AS value
        FROM transactions
        WHERE period_id=? AND type='expense'
        """,
        (period_id,),
    ).fetchone()["value"]

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

    transaction_count = db.execute(
        """
        SELECT COUNT(*) AS value
        FROM transactions
        WHERE period_id=?
        """,
        (period_id,),
    ).fetchone()["value"]

    return {
        "id": period["id"],
        "frequency": period["frequency"],
        "startDate": period["start_date"],
        "endDate": period["end_date"],
        "isCurrent": bool(period["is_current"]),
        "income": income,
        "expenses": expenses,
        "balance": income - expenses,
        "transactionCount": transaction_count,
        "recentTransactions": [dict(row) for row in recent],
        "categories": [dict(row) for row in categories],
    }
