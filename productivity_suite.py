import json
import os
from datetime import datetime
from collections import defaultdict

# ===== SHARED UTILS =====
BUDGET_FILE = "budget_data.json"
TODO_FILE = "todo_data.json"
STUDY_FILE = "study_data.json"
BACK_COMMAND = 'b'

def get_input(prompt, allow_back=True):
    """Handles user input with 'back' command support. Returns None if user types b"""
    val = input(prompt).strip()
    if allow_back and val.lower() == BACK_COMMAND:
        return None
    return val

def validate_amount(amount_str):
    try:
        amount = float(amount_str)
        if 0 < amount < 1000000:
            return amount
        return None
    except ValueError:
        return None

def format_currency(value):
    return f"R{value:.2f}"

def load_json(filename, default_data):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return default_data

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def pause():
    input("\nPress Enter to return...")

# ===== 1. BUDGET TRACKER =====
def budget_load_data():
    default = {"transactions": [], "categories": ["Food", "Rent", "Transport", "Salary", "Other"]}
    return load_json(BUDGET_FILE, default)

def budget_add_transaction(data):
    print(f"\n=== Add Transaction === (enter '{BACK_COMMAND}' to go back)")

    while True:
        t_type = get_input("Type [1] Income or [2] Expense: ")
        if t_type is None: return # Go back
        if t_type == '1': t_type = "income"; break
        elif t_type == '2': t_type = "expense"; break
        else: print("Invalid choice. Try again.")

    amount_str = get_input("Amount: R")
    if amount_str is None: return # Go back
    amount = validate_amount(amount_str)
    if amount is None:
        print("Invalid amount. Must be positive number < 1,000,000.")
        return

    print("Categories:", ", ".join(data["categories"]))
    category = get_input("Category: ")
    if category is None: return # Go back
    category = category.title()

    if category not in data["categories"]:
        add_cat = get_input(f"'{category}' not found. Add it? [y/n]: ")
        if add_cat is None: return # Go back
        if add_cat.lower() in ['y', 'yes']:
            data["categories"].append(category)
        else:
            category = "Other"

    note = get_input("Note: ")
    if note is None: return # Go back

    transaction = {
        "type": t_type,
        "amount": amount,
        "category": category,
        "note": note,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    data["transactions"].append(transaction)
    save_json(BUDGET_FILE, data)
    print(f"{t_type.title()} of {format_currency(amount)} added.")

def budget_view_balance(data):
    income = sum(t["amount"] for t in data["transactions"] if t["type"] == "income")
    expenses = sum(t["amount"] for t in data["transactions"] if t["type"] == "expense")
    balance = income - expenses

    print("\n=== Balance Summary ===")
    print(f"Total Income: {format_currency(income)}")
    print(f"Total Expenses: {format_currency(expenses)}")
    print(f"Net Balance: {format_currency(balance)}")

    if balance < 0: print("⚠️ You're over budget!")
    elif balance == 0: print("Break even!")
    else: print("You're in the green! 💰")
    pause()

def budget_view_by_category(data):
    if not data["transactions"]:
        print("No transactions yet.")
        pause()
        return

    totals = defaultdict(lambda: {"income": 0, "expense": 0})
    for t in data["transactions"]:
        totals[t["category"]][t["type"]] += t["amount"]

    print("\n=== Spending by Category ===")
    print(f"{'Category':<15} {'Income':<12} {'Expense':<12} {'Net':<12}")
    print("-" * 51)

    for cat in sorted(totals.keys()):
        vals = totals[cat]
        net = vals["income"] - vals["expense"]
        print(f"{cat:<15} {format_currency(vals['income']):<12} "
              f"{format_currency(vals['expense']):<12} "
              f"{format_currency(net):<12}")
    pause()

def budget_menu():
    data = budget_load_data()
    while True:
        print("\n====== Budget Tracker ======")
        print("1. Add Income/Expense")
        print("2. View Balance")
        print("3. View by Category")
        print("4. List All Transactions")
        print("5. Back to Main Menu")
        choice = get_input("Choose [1-5] or 'b' to go back: ")

        if choice is None or choice == '5': break # Go back
        elif choice == '1': budget_add_transaction(data)
        elif choice == '2': budget_view_balance(data)
        elif choice == '3': budget_view_by_category(data)
        elif choice == '4':
            if not data["transactions"]:
                print("No transactions to show.")
            else:
                print("\n=== Transactions ===")
                for i, t in enumerate(data["transactions"], 1):
                    print(f"{i:<3} {t['date']:<17} {t['type']:<8} {format_currency(t['amount']):<10} {t['category']:<12} {t['note']}")
            pause()
        else: print("Invalid option.")

# ===== 2. TO-DO LIST =====
def todo_load_data():
    return load_json(TODO_FILE, {"tasks": []})

def todo_add_task(data):
    print(f"\n=== Add Task === (enter '{BACK_COMMAND}' to go back)")
    task_name = get_input("Task name: ")
    if task_name is None: return # Go back

    priority = get_input("Priority [low/medium/high]: ")
    if priority is None: return # Go back
    if priority.lower() not in ['low', 'medium', 'high']:
        priority = 'medium'

    task = {
        "name": task_name,
        "priority": priority,
        "done": False,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    data["tasks"].append(task)
    save_json(TODO_FILE, data)
    print(f"Task '{task_name}' added.")

def todo_list_tasks(data):
    tasks = data["tasks"]
    if not tasks:
        print("No tasks yet.")
        pause()
        return

    print("\n=== To-Do List ===")
    print(f"{'#':<4} {'Status':<8} {'Priority':<10} {'Task'}")
    print("-" * 50)

    for i, t in enumerate(tasks, 1):
        status = "✓ Done" if t["done"] else "○ Todo"
        print(f"{i:<4} {status:<8} {t['priority']:<10} {t['name']}")
    pause()

def todo_toggle_task(data):
    if not data["tasks"]:
        print("No tasks to mark.")
        pause()
        return

    print("\n=== To-Do List ===")
    for i, t in enumerate(data["tasks"], 1):
        status = "✓ Done" if t["done"] else "○ Todo"
        print(f"{i:<4} {status:<8} {t['priority']:<10} {t['name']}")

    idx_str = get_input("Enter task number to toggle done/undone or 'b' to go back: ")
    if idx_str is None: return # Go back

    try:
        idx = int(idx_str) - 1
        if 0 <= idx < len(data["tasks"]):
            data["tasks"][idx]["done"] = not data["tasks"][idx]["done"]
            status = "done" if data["tasks"][idx]["done"] else "undone"
            save_json(TODO_FILE, data)
            print(f"Task marked as {status}.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a number.")

def todo_menu():
    data = todo_load_data()
    while True:
        print("\n====== To-Do List ======")
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. Mark Task Done/Undone")
        print("4. Back to Main Menu")
        choice = get_input("Choose [1-4] or 'b' to go back: ")

        if choice is None or choice == '4': break # Go back
        elif choice == '1': todo_add_task(data)
        elif choice == '2': todo_list_tasks(data)
        elif choice == '3': todo_toggle_task(data)
        else: print("Invalid option.")

# ===== 3. STUDY PLANNER =====
def study_load_data():
    return load_json(STUDY_FILE, {"sessions": []})

def study_add_session(data):
    print(f"\n=== Add Study Session === (enter '{BACK_COMMAND}' to go back)")
    subject = get_input("Subject: ")
    if subject is None: return # Go back

    duration_str = get_input("Duration in minutes: ")
    if duration_str is None: return # Go back

    try:
        duration = int(duration_str)
        if duration <= 0 or duration > 480:
            print("Duration must be 1-480 minutes.")
            return
    except ValueError:
        print("Invalid number.")
        return

    date_str = get_input("Date [YYYY-MM-DD] or 'today': ")
    if date_str is None: return # Go back

    if date_str.lower() == 'today':
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            date = date_str
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return

    session = {
        "subject": subject.title(),
        "duration": duration,
        "date": date,
        "done": False
    }
    data["sessions"].append(session)
    save_json(STUDY_FILE, data)
    print(f"Added {duration}min session for {subject} on {date}.")

def study_view_schedule(data):
    sessions = sorted(data["sessions"], key=lambda x: x["date"])
    if not sessions:
        print("No study sessions planned.")
        pause()
        return

    print("\n=== Study Schedule ===")
    print(f"{'#':<4} {'Date':<12} {'Subject':<15} {'Duration':<10} {'Status'}")
    print("-" * 55)

    for i, s in enumerate(sessions, 1):
        status = "✓ Done" if s["done"] else "○ Planned"
        print(f"{i:<4} {s['date']:<12} {s['subject']:<15} {s['duration']}min{'':<5} {status}")

    total_mins = sum(s["duration"] for s in sessions if not s["done"])
    print(f"\nTotal planned: {total_mins} minutes ({total_mins//60}h {total_mins%60}m)")
    pause()

def study_today(data):
    today = datetime.now().strftime("%Y-%m-%d")
    today_sessions = [s for s in data["sessions"] if s["date"] == today]

    print(f"\n=== Today's Study Plan: {today} ===")
    if not today_sessions:
        print("No sessions scheduled for today.")
        pause()
        return

    for i, s in enumerate(today_sessions, 1):
        status = "✓" if s["done"] else "○"
        print(f"{i}. {status} {s['subject']}: {s['duration']} minutes")

    total = sum(s["duration"] for s in today_sessions if not s["done"])
    print(f"\nRemaining: {total} minutes")
    pause()

def study_menu():
    data = study_load_data()
    while True:
        print("\n====== Study Planner ======")
        print("1. Add Study Session")
        print("2. View Full Schedule")
        print("3. View Today's Plan")
        print("4. Back to Main Menu")
        choice = get_input("Choose [1-4] or 'b' to go back: ")

        if choice is None or choice == '4': break # Go back
        elif choice == '1': study_add_session(data)
        elif choice == '2': study_view_schedule(data)
        elif choice == '3': study_today(data)
        else: print("Invalid option.")

# ===== MAIN MENU =====
def main():
    while True:
        print("\n======== Productivity Suite ========")
        print("1. Budget Tracker")
        print("2. To-Do List")
        print("3. Study Planner")
        print("4. Exit")
        print("=" * 36)

        choice = get_input("Choose [1-4] or 'b' to exit: ")

        if choice is None or choice == '4': # Go back / exit
            print("Goodbye! Your data is saved.")
            break
        elif choice == '1': budget_menu()
        elif choice == '2': todo_menu()
        elif choice == '3': study_menu()
        else:
            print("Invalid option. Pick 1-4.")

if __name__ == "__main__":
    main()