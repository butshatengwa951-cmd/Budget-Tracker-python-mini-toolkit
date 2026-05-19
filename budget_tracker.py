# BUILT-IN MODULES: json, os, datetime, collections
import json
import os
from datetime import datetime # Built-in module
from collections import defaultdict
import budget_utils # CUSTOM MODULE import

# VARIABLES + DATA TYPES
app_name = "Budget Tracker v2" # String
version = 2.1 # Float
is_running = True # Boolean
menu_options = [1, 2, 3, 4, 5] # List data type

def load_data():
    """
    Demonstrates: if statement, boolean expression, dictionary data type, list data type
    """
    # Comparison operator, boolean expression
    if os.path.exists(budget_utils.DATA_FILE):
        with open(budget_utils.DATA_FILE, 'r') as f:
            data = json.load(f) # Dictionary data type
            # Logical operator not in
            if "transactions" not in data:
                data["transactions"] = [] # List data type, assignment operator
            return data
    else:
        # Dictionary + list data types
        return {"transactions": [], "categories": ["Food", "Rent", "Transport", "Salary", "Other"]}

def save_data(data):
    """Demonstrates: file output, parameters"""
    with open(budget_utils.DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_transaction(data):
    """
    Demonstrates: nested conditions, while loop, loop control, elif, else
    """
    print(f"\n=== Add Transaction === (enter '{budget_utils.BACK_COMMAND}' to go back)")

    # WHILE LOOP + LOOP CONTROL
    while True:
        t_type = budget_utils.get_input("Type [1] Income or [2] Expense: ")
        if t_type is None: # User chose to go back
            return # Loop control: return exits function + loop

        # IF, ELIF, ELSE + COMPARISON + LOGICAL OPERATORS
        if t_type == '1':
            t_type = "income"
            break # Loop control: break exits while loop
        elif t_type == '2':
            t_type = "expense"
            break
        else:
            print("Invalid choice. Try again.") # Output

    # TYPE CASTING + FUNCTION CALL WITH ARGUMENT
    amount_str = budget_utils.get_input("Amount: R")
    if amount_str is None: return

    # PASSING FUNCTION AS ARGUMENT concept: we pass result of get_input to validate_amount
    amount = budget_utils.validate_amount(amount_str) # Arguments, return value
    if amount is None:
        print("Invalid amount. Must be positive number < 1,000,000.")
        return

    print("Categories:", ", ".join(data["categories"])) # List method, string method
    category = budget_utils.get_input("Category: ")
    if category is None: return
    category = category.title() # String method

    # NESTED CONDITION
    if category not in data["categories"]:
        add_cat = budget_utils.get_input(f"'{category}' not found. Add it? [y/n]: ")
        if add_cat is None: return
        # Boolean expression with logical operator or
        if add_cat.lower() == 'y' or add_cat.lower() == 'yes':
            data["categories"].append(category) # List method
        else:
            category = "Other" # Assignment operator

    note = budget_utils.get_input("Note: ")
    if note is None: return

    date = datetime.now().strftime("%Y-%m-%d %H:%M") # Built-in module usage

    # DICTIONARY DATA TYPE
    transaction = {
        "type": t_type,
        "amount": amount,
        "category": category,
        "note": note,
        "date": date
    }

    data["transactions"].append(transaction) # List method
    save_data(data)
    # ARITHMETIC OPERATOR not needed here, but output uses formatted currency
    print(f"{t_type.title()} of {budget_utils.format_currency(amount)} added.")

def view_balance(data):
    """
    Demonstrates: for loop, arithmetic operators, comparison operators, augmented assignment
    """
    income = 0.0 # Float data type, assignment operator
    expenses = 0.0 # Float data type

    # FOR LOOP through list
    for t in data["transactions"]:
        # IF/ELIF/ELSE + COMPARISON OPERATOR
        if t["type"] == "income":
            income += t["amount"] # Augmented assignment, arithmetic operator +=
        elif t["type"] == "expense":
            expenses += t["amount"] # Augmented assignment

    balance = income - expenses # Arithmetic operator -

    print("\n=== Balance Summary ===")
    print(f"Total Income: {budget_utils.format_currency(income)}")
    print(f"Total Expenses: {budget_utils.format_currency(expenses)}")
    print(f"Net Balance: {budget_utils.format_currency(balance)}")

    # COMPARISON OPERATOR + BOOLEAN EXPRESSION
    if balance < 0:
        print("⚠️ You're over budget!")
    elif balance == 0: # ELIF
        print("Break even!")
    else:
        print("You're in the green! 💰")

    input("\nPress Enter to return...")

def view_by_category(data):
    """
    Demonstrates: for loop with range, lists, nested conditions, logical operators
    """
    if not data["transactions"]: # Logical operator not, boolean expression
        print("No transactions yet.")
        input("\nPress Enter to return...")
        return

    totals = defaultdict(lambda: {"income": 0, "expense": 0})

    # FOR LOOP
    for t in data["transactions"]:
        totals[t["category"]][t["type"]] += t["amount"]

    print("\n=== Spending by Category ===")
    print(f"{'Category':<15} {'Income':<12} {'Expense':<12} {'Net':<12}")
    print("-" * 51)

    # FOR LOOP + range + len for indexed iteration
    sorted_cats = sorted(totals.keys()) # List data type
    for i in range(len(sorted_cats)): # range() + len()
        cat = sorted_cats[i] # List indexing
        vals = totals[cat]
        net = vals["income"] - vals["expense"] # Arithmetic operator
        print(f"{cat:<15} {budget_utils.format_currency(vals['income']):<12} "
              f"{budget_utils.format_currency(vals['expense']):<12} "
              f"{budget_utils.format_currency(net):<12}")

    input("\nPress Enter to return...")

def list_transactions(data, filter_func=None):
    """
    Demonstrates: PASSING FUNCTION AS ARGUMENT, default parameters, for loop with enumerate
    """
    transactions = data["transactions"]

    # If a filter function was passed as argument
    if filter_func is not None: # Comparison operator
        transactions = list(filter(filter_func, transactions)) # Passing function as argument

    if not transactions:
        print("No transactions to show.")
        input("\nPress Enter to return...")
        return

    print("\n=== Transactions ===")
    print(f"{'#':<4} {'Date':<17} {'Type':<8} {'Amount':<10} {'Category':<12} {'Note'}")
    print("-" * 80)

    # FOR LOOP with enumerate + range concept
    for i, t in enumerate(transactions, 1): # enumerate starts at 1
        print(f"{i:<4} {t['date']:<17} {t['type']:<8} "
              f"{budget_utils.format_currency(t['amount']):<10} {t['category']:<12} {t['note']}")

    input("\nPress Enter to return...")

# FUNCTIONS FOR PASSING AS ARGUMENTS DEMO
def is_expense(transaction):
    """Return True if expense. Used for passing as argument."""
    return transaction["type"] == "expense" # Boolean expression, comparison

def is_income(transaction):
    """Return True if income. Used for passing as argument."""
    return transaction["type"] == "income" # Boolean expression

def main_menu():
    """
    Demonstrates: while loop, if/elif/else chain, boolean expressions, loop control
    """
    data = load_data()

    # WHILE LOOP - main program loop
    while is_running: # Boolean expression
        print(f"\n======== {app_name} ========") # Variables in output
        print("1. Add Income/Expense")
        print("2. View Balance")
        print("3. View by Category")
        print("4. List All Transactions")
        print("5. List Only Expenses") # Shows passing function as argument
        print("6. Exit")
        print("=" * 30)

        choice = budget_utils.get_input("Choose [1-6]: ", allow_back=False)

        # IF/ELIF/ELSE CHAIN + COMPARISON OPERATORS
        if choice == '1':
            add_transaction(data)
        elif choice == '2':
            view_balance(data)
        elif choice == '3':
            view_by_category(data)
        elif choice == '4':
            list_transactions(data) # No filter function passed
        elif choice == '5':
            list_transactions(data, is_expense) # PASSING FUNCTION AS ARGUMENT
        elif choice == '6':
            print("Saving... Goodbye!")
            save_data(data)
            break # LOOP CONTROL: break exits while loop
        else:
            print("Invalid option. Pick 1-6.") # Output

# Program starts here
if __name__ == "__main__":
    main_menu()