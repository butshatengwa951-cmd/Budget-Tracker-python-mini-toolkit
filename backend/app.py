from datetime import date as Date
from flask import Flask, jsonify, request
from flask_cors import CORS
from db import (
    VALID_FREQUENCIES,
    ensure_current_period,
    local_timestamp,
    get_db,
    get_period_summary,
    init_db,
    period_dates,
)

app = Flask(__name__)
CORS(app)
init_db()


def current_period(db):
    return ensure_current_period(db)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/settings")
def settings():
    db = get_db()
    period = current_period(db)
    frequency = db.execute(
        "SELECT reset_frequency FROM settings WHERE id=1"
    ).fetchone()["reset_frequency"]
    db.close()
    return jsonify({
        "resetFrequency": frequency,
        "currentPeriod": dict(period),
    })


@app.patch("/api/settings")
def update_settings():
    data = request.get_json() or {}
    frequency = data.get("resetFrequency")

    if frequency not in VALID_FREQUENCIES:
        return jsonify({
            "error": "Reset frequency must be daily, weekly, monthly or yearly"
        }), 400

    db = get_db()
    old_frequency = db.execute(
        "SELECT reset_frequency FROM settings WHERE id=1"
    ).fetchone()["reset_frequency"]

    if frequency != old_frequency:
        db.execute(
            """
            UPDATE budget_periods
            SET is_current=0
            WHERE is_current=1
            """
        )
        db.execute(
            """
            UPDATE settings
            SET reset_frequency=?, updated_at=?
            WHERE id=1
            """,
            (frequency, local_timestamp()),
        )

    period = current_period(db)
    db.close()

    return jsonify({
        "resetFrequency": frequency,
        "previousFrequency": old_frequency,
        "currentPeriod": dict(period),
        "message": (
            "A new budget period has been started. Your previous budgets remain in history."
            if frequency != old_frequency
            else "Settings saved."
        ),
    })


@app.get("/api/summary")
def summary():
    db = get_db()
    period = current_period(db)
    data = get_period_summary(db, period["id"])

    tasks = db.execute(
        "SELECT COUNT(*) FROM tasks WHERE done=0"
    ).fetchone()[0]
    study = db.execute(
        "SELECT COALESCE(SUM(duration),0) FROM study_sessions WHERE done=0"
    ).fetchone()[0]

    db.close()

    return jsonify({
        **data,
        "openTasks": tasks,
        "plannedStudyMinutes": study,
    })


@app.get("/api/transactions")
def transactions():
    db = get_db()
    period = current_period(db)
    rows = db.execute(
        """
        SELECT * FROM transactions
        WHERE period_id=?
        ORDER BY date DESC, id DESC
        """,
        (period["id"],),
    ).fetchall()
    db.close()
    return jsonify([dict(x) for x in rows])


@app.post("/api/transactions")
def add_transaction():
    data = request.get_json() or {}

    try:
        amount = float(data["amount"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Amount must be a number"}), 400

    if not 0 < amount < 1000000:
        return jsonify({"error": "Amount must be between 0 and 1,000,000"}), 400

    if data.get("type") not in ("income", "expense"):
        return jsonify({"error": "Type must be income or expense"}), 400

    category = (data.get("category") or "Other").strip().title()
    note = (data.get("note") or "").strip()

    db = get_db()
    period = current_period(db)

    cur = db.execute(
        """
        INSERT INTO transactions(type, amount, category, note, date, period_id)
        VALUES (?,?,?,?,?,?)
        """,
        (data["type"], amount, category, note, local_timestamp(), period["id"]),
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM transactions WHERE id=?", (cur.lastrowid,)
    ).fetchone()
    db.close()
    return jsonify(dict(row)), 201


@app.delete("/api/transactions/<int:item_id>")
def delete_transaction(item_id):
    db = get_db()
    period = current_period(db)
    db.execute(
        "DELETE FROM transactions WHERE id=? AND period_id=?",
        (item_id, period["id"]),
    )
    db.commit()
    db.close()
    return jsonify({"ok": True})


@app.get("/api/budgets")
def budgets():
    db = get_db()
    current_period(db)
    rows = db.execute(
        """
        SELECT * FROM budget_periods
        ORDER BY start_date DESC, id DESC
        """
    ).fetchall()

    result = []
    for row in rows:
        data = get_period_summary(db, row["id"])
        result.append(data)

    db.close()
    return jsonify(result)


@app.get("/api/budgets/<int:period_id>")
def budget_detail(period_id):
    db = get_db()
    current_period(db)
    data = get_period_summary(db, period_id)

    if not data:
        db.close()
        return jsonify({"error": "Budget period not found"}), 404

    rows = db.execute(
        """
        SELECT * FROM transactions
        WHERE period_id=?
        ORDER BY date DESC, id DESC
        """,
        (period_id,),
    ).fetchall()
    db.close()

    return jsonify({
        **data,
        "transactions": [dict(row) for row in rows],
    })


@app.get("/api/tasks")
def tasks():
    db = get_db()
    rows = db.execute("SELECT * FROM tasks ORDER BY done, id DESC").fetchall()
    db.close()
    return jsonify([dict(x) for x in rows])


@app.post("/api/tasks")
def add_task():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Task name is required"}), 400

    priority = (
        data.get("priority")
        if data.get("priority") in ("low", "medium", "high")
        else "medium"
    )

    db = get_db()
    cur = db.execute(
        "INSERT INTO tasks(name, priority, done, created) VALUES (?,?,0,?)",
        (name, priority, local_timestamp()),
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM tasks WHERE id=?", (cur.lastrowid,)
    ).fetchone()
    db.close()
    return jsonify(dict(row)), 201


@app.patch("/api/tasks/<int:item_id>")
def toggle_task(item_id):
    db = get_db()
    db.execute(
        "UPDATE tasks SET done = CASE done WHEN 0 THEN 1 ELSE 0 END WHERE id=?",
        (item_id,),
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM tasks WHERE id=?", (item_id,)
    ).fetchone()
    db.close()
    return jsonify(dict(row)) if row else (jsonify({"error": "Task not found"}), 404)


@app.delete("/api/tasks/<int:item_id>")
def delete_task(item_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id=?", (item_id,))
    db.commit()
    db.close()
    return jsonify({"ok": True})


@app.get("/api/study")
def study():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM study_sessions ORDER BY date ASC, id ASC"
    ).fetchall()
    db.close()
    return jsonify([dict(x) for x in rows])


@app.post("/api/study")
def add_study():
    data = request.get_json() or {}
    subject = (data.get("subject") or "").strip()

    try:
        duration = int(data["duration"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Duration must be a whole number"}), 400

    raw_date = (data.get("date") or "").strip()

    try:
        parsed_date = Date.fromisoformat(raw_date)
    except ValueError:
        return jsonify({"error": "Date must be a valid YYYY-MM-DD date"}), 400

    if not subject or duration < 1 or duration > 480:
        return jsonify({
            "error": "Subject is required and duration must be between 1 and 480 minutes"
        }), 400

    if parsed_date.isoformat() != raw_date:
        return jsonify({"error": "Date must be a valid YYYY-MM-DD date"}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO study_sessions(subject, duration, date, done) VALUES (?,?,?,0)",
        (subject.title(), duration, raw_date),
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM study_sessions WHERE id=?", (cur.lastrowid,)
    ).fetchone()
    db.close()
    return jsonify(dict(row)), 201


@app.patch("/api/study/<int:item_id>")
def toggle_study(item_id):
    db = get_db()
    db.execute(
        "UPDATE study_sessions SET done = CASE done WHEN 0 THEN 1 ELSE 0 END WHERE id=?",
        (item_id,),
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM study_sessions WHERE id=?", (item_id,)
    ).fetchone()
    db.close()
    return jsonify(dict(row)) if row else (jsonify({"error": "Session not found"}), 404)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
