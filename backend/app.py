from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_db, init_db

app = Flask(__name__)
CORS(app)

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.get("/api/summary")
def summary():
    db = get_db()
    income = db.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE type='income'").fetchone()[0]
    expenses = db.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE type='expense'").fetchone()[0]
    transactions = db.execute("SELECT * FROM transactions ORDER BY date DESC, id DESC LIMIT 8").fetchall()
    categories = db.execute("""
      SELECT category, COALESCE(SUM(amount),0) AS total
      FROM transactions WHERE type='expense'
      GROUP BY category ORDER BY total DESC
    """).fetchall()
    tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE done=0").fetchone()[0]
    study = db.execute("SELECT COALESCE(SUM(duration),0) FROM study_sessions WHERE done=0").fetchone()[0]
    return jsonify({
        "income": income, "expenses": expenses, "balance": income - expenses,
        "recentTransactions": [dict(x) for x in transactions],
        "categories": [dict(x) for x in categories],
        "openTasks": tasks,
        "plannedStudyMinutes": study
    })

@app.get("/api/transactions")
def transactions():
    db = get_db()
    rows = db.execute("SELECT * FROM transactions ORDER BY date DESC, id DESC").fetchall()
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
    cur = db.execute(
      "INSERT INTO transactions(type, amount, category, note, date) VALUES (?,?,?,?,datetime('now'))",
      (data["type"], amount, category, note)
    )
    db.commit()
    return jsonify(dict(db.execute("SELECT * FROM transactions WHERE id=?", (cur.lastrowid,)).fetchone())), 201

@app.delete("/api/transactions/<int:item_id>")
def delete_transaction(item_id):
    db = get_db()
    db.execute("DELETE FROM transactions WHERE id=?", (item_id,))
    db.commit()
    return jsonify({"ok": True})

@app.get("/api/tasks")
def tasks():
    db = get_db()
    rows = db.execute("SELECT * FROM tasks ORDER BY done, id DESC").fetchall()
    return jsonify([dict(x) for x in rows])

@app.post("/api/tasks")
def add_task():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Task name is required"}), 400
    priority = data.get("priority") if data.get("priority") in ("low","medium","high") else "medium"
    db = get_db()
    cur = db.execute("INSERT INTO tasks(name, priority, done, created) VALUES (?,?,0,datetime('now'))", (name, priority))
    db.commit()
    return jsonify(dict(db.execute("SELECT * FROM tasks WHERE id=?", (cur.lastrowid,)).fetchone())), 201

@app.patch("/api/tasks/<int:item_id>")
def toggle_task(item_id):
    db = get_db()
    db.execute("UPDATE tasks SET done = CASE done WHEN 0 THEN 1 ELSE 0 END WHERE id=?", (item_id,))
    db.commit()
    row = db.execute("SELECT * FROM tasks WHERE id=?", (item_id,)).fetchone()
    return jsonify(dict(row)) if row else (jsonify({"error": "Task not found"}), 404)

@app.delete("/api/tasks/<int:item_id>")
def delete_task(item_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id=?", (item_id,))
    db.commit()
    return jsonify({"ok": True})

@app.get("/api/study")
def study():
    db = get_db()
    rows = db.execute("SELECT * FROM study_sessions ORDER BY date ASC, id ASC").fetchall()
    return jsonify([dict(x) for x in rows])

@app.post("/api/study")
def add_study():
    data = request.get_json() or {}
    subject = (data.get("subject") or "").strip()
    try:
        duration = int(data["duration"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Duration must be a number"}), 400
    date = (data.get("date") or "").strip()
    if not subject or duration < 1 or duration > 480 or len(date) != 10:
        return jsonify({"error": "Subject, duration and YYYY-MM-DD date are required"}), 400
    db = get_db()
    cur = db.execute(
      "INSERT INTO study_sessions(subject, duration, date, done) VALUES (?,?,?,0)",
      (subject.title(), duration, date)
    )
    db.commit()
    return jsonify(dict(db.execute("SELECT * FROM study_sessions WHERE id=?", (cur.lastrowid,)).fetchone())), 201

@app.patch("/api/study/<int:item_id>")
def toggle_study(item_id):
    db = get_db()
    db.execute("UPDATE study_sessions SET done = CASE done WHEN 0 THEN 1 ELSE 0 END WHERE id=?", (item_id,))
    db.commit()
    row = db.execute("SELECT * FROM study_sessions WHERE id=?", (item_id,)).fetchone()
    return jsonify(dict(row)) if row else (jsonify({"error": "Session not found"}), 404)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
