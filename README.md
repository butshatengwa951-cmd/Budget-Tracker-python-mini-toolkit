Markdown
# Productivity Suite

### Short project description
A menu-based Python program with 3 integrated tools: Budget Tracker, To-Do List, and Study Planner. Run everything from one terminal app. Each tool saves to its own JSON file so your data persists between sessions. Built to practice functions, modules, file I/O, and user input handling while making something genuinely useful.

### Features
- **Budget Tracker**: Add income/expenses, view balance, category breakdown, transaction history
- **To-Do List**: Add tasks with priority levels, mark done/undone, delete tasks, view all tasks
- **Study Planner**: Schedule study sessions with subject, duration, and date. View today’s plan or full schedule
- **Go back option**: Type `b` at any prompt to cancel the current step and return to the previous menu
- **Data persistence**: Auto-saves to `budget_data.json`, `todo_data.json`, and `study_data.json`
- **Input validation**: Handles invalid numbers, dates, and empty input without crashing across all three tools
- **Modular design**: Shared utility functions prevent code repetition

### Python concepts used
| Concept | Where it's used |
| --- | --- |
| **Variables & data types** | `string`, `int`, `float`, `bool`, `list`, `dict` for app state across all tools |
| **User input/output** | `input()` for all prompts, `print()` for menus and formatted tables |
| **Type casting** | `float()` for amounts, `int()` for durations/task numbers, f-strings for formatting |
| **Operators** | Arithmetic `+`, `-`, `+=`, `//`, `%`, comparison `==`, `<`, `>`, logical `and`, `or`, `not` |
| **Conditionals** | `if/elif/else` for menu logic, validation, and priority checks in all tools |
| **Loops** | `while` loops for main + sub menus, `for` loops to sum totals and list items |
| **Loop control** | `break` to exit menus, `continue` to skip, `return` to go back when user types `b` |
| **Functions** | Separate functions per feature + shared utils: `get_input()`, `save_json()`, `load_json()` |
| **Parameters & return values** | `get_input(prompt, allow_back)` returns input or `None` for back command |
| **Lambda functions** | `key=lambda x: x["date"]` for sorting study sessions |
| **Lists & dictionaries** | Lists of dicts for transactions, tasks, sessions. `defaultdict` for category totals |
| **Built-in modules** | `json` for save/load, `os` for file checks, `datetime` for dates/timestamps |
| **Exception handling** | `try/except ValueError` when converting input to float/int and parsing dates |
| **List comprehensions** | `sum(t["amount"] for t in transactions if t["type"] == "income")` |

### How to run the project
1. **Requirements**: Python 3.8 or higher. No external packages needed.
2. **Setup**: Save the code as `productivity_suite.py`.
3. **Run command**:
   ```bash
   python productivity_suite.py
4. First run: The program creates budget_data.json, todo_data.json, and study_data.json automatically.
Controls: Use number keys to navigate menus. Enter b at any prompt to go back to the previous menu.

### Challenges I faced
The main challenge was making input foolproof across three different tools. Early versions crashed if a user typed letters for an amount or wanted to cancel halfway through adding a task. Fixing it meant adding a central get_input() function, wrapping type casting in try/except, and returning early whenever the user typed b. Managing three separate JSON files without repeating code also took refactoring.

### What I learned
I learned how to structure a larger program using multiple functions and shared utility functions to avoid repetition. I also learned that good user experience matters even in CLI apps — things like "press Enter to continue" and "type b to go back" make it feel usable. Handling files with JSON taught me the basics of data persistence, and using datetime showed me how to work with dates properly.

### Future improvements
Date filtering: View transactions for this week, this month, or a custom range
Budget limits: Set a cap for each category and get warnings when close to overspending
CSV export: Dump data to a spreadsheet for Excel or Google Sheets
Charts: Add matplotlib to show a pie chart of expenses by category
Search: Find transactions by note or date
Task deadlines: Add due dates to to-do items with overdue warnings
Study timer: Add a built-in Pomodoro timer for study sessions

### Author
Butsha Tengwa
