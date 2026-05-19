# Budget Tracker CLI

### Short project description
A menu-based Python app that helps you track income and expenses from your terminal. Add transactions, view your balance, break down spending by category, and see your full history. All data is saved locally in a JSON file so nothing is lost between runs.

### Features
- **Add transactions**: Record income or expenses with amount, category, date, and note
- **View balance**: See total income, total expenses, and net balance at a glance
- **Category breakdown**: Totals for each category with income vs expense comparison
- **Transaction history**: List all transactions with dates and details
- **Go back anytime**: Enter `b` at any prompt to cancel and return to the main menu
- **Data persistence**: Automatically saves to `budget_data.json` after each change
- **Input validation**: Handles bad input without crashing

### Python concepts used
| Concept | Where it's used |
| --- | --- |
| **Variables & data types** | `app_name` string, `version` float, `is_running` bool, `transaction` dict, `categories` list |
| **User input/output** | `input()` for menus, `print()` for tables and feedback |
| **Type casting** | `float(amount_str)` for money values, f-strings for currency format |
| **Operators** | Arithmetic `+`, `-`, `+=`, comparison `==`, `<`, logical `and`, `or`, `not` |
| **Conditionals** | `if/elif/else` for menu choices, nested conditions for category validation |
| **Loops** | `while` loop for main menu, `for` loops to sum totals and list transactions |
| **Loop control** | `break` to exit validation loops, `return` to go back to main menu |
| **Functions** | Modular functions like `add_transaction()`, `load_data()`, `format_currency()` |
| **Parameters & return values** | `get_input(prompt)` returns user input or `None` for back command |
| **Passing functions as arguments** | `list_transactions(data, is_expense)` uses `filter()` with a function |
| **Lists & dictionaries** | `transactions` list of dicts, `totals` defaultdict for category sums |
| **Built-in modules** | `json` for save/load, `os` for file checks, `datetime` for timestamps |
| **Custom modules** | `budget_utils.py` stores helper functions and constants |
| **Exception handling** | `try/except` catches invalid number input |

### How to run the project
First run: The program will create budget_data.json automatically to store your data.
Controls: Use number keys 1-6 to navigate menus. Enter b at any prompt to go back.

### Challenges you faced
The main challenge was making input foolproof. Early versions crashed if a user typed letters for an amount or wanted to cancel halfway through adding a transaction. Fixing it meant adding a central get_input() function, wrapping type casting in try/except, and returning early whenever the user typed b.

### What you learned
I learned how to structure a larger program using multiple functions and a separate utility module. I also learned that good user experience matters even in CLI apps — things like "press Enter to continue" and "type b to go back" make it feel usable. Handling files with JSON taught me the basics of data persistence.

### Future improvements
Date filtering: View transactions for this week, this month, or a custom range
Budget limits: Set a cap for each category and get warnings when close to overspending
CSV export: Dump data to a spreadsheet for Excel or Google Sheets
Charts: Add matplotlib to show a pie chart of expenses by category
Search: Find transactions by note or date

### Author
Butsha Tengwa