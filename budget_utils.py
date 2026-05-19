# CUSTOM MODULE: demonstrates custom modules
# Variables, data types, functions, parameters, return values

DATA_FILE = "budget_data.json" # Variable, string data type
BACK_COMMAND = 'b' # Variable, string data type

def get_input(prompt, allow_back=True):
    """
    Function with parameters + return value
    Demonstrates: user input, output, if statement, boolean expression, string methods
    """
    val = input(prompt).strip() # User input, string data type
    # Comparison operator ==, logical operator and, boolean expression
    if allow_back and val.lower() == BACK_COMMAND:
        return None # Return value
    return val # Return value

def validate_amount(amount_str):
    """
    Demonstrates: type casting, try/except, if/else, comparison operators, boolean expression
    """
    try:
        amount = float(amount_str) # Type casting: string -> float
        # Comparison operator >, logical operator and
        if amount > 0 and amount < 1000000: # Nested condition, boolean expression
            return amount # Return value
        else:
            return None
    except ValueError: # Handles type casting error
        return None

def format_currency(value):
    """Demonstrates: f-strings, type casting, return value"""
    return f"R{value:.2f}" # Float data type, type casting in f-string