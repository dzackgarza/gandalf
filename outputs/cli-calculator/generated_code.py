# calculator/arithmetic_operations.py
def add(x, y):
    """Adds two numbers."""
    return x + y

def subtract(x, y):
    """Subtracts two numbers."""
    return x - y

def multiply(x, y):
    """Multiplies two numbers."""
    return x * y

def divide(x, y):
    """Divides two numbers; handles division by zero."""
    if y == 0:
        raise ZeroDivisionError("Division by zero is not allowed.")
    return x / y

# calculator/input_output.py
def parse_input(input_str):
    """Parses user input, handles invalid input."""
    try:
        parts = input_str.split()
        if len(parts) != 3:
            raise ValueError("Invalid input format. Use 'num1 operator num2'.")
        num1 = float(parts[0])
        operator = parts[1]
        num2 = float(parts[2])
        return num1, operator, num2
    except ValueError as e:
        raise ValueError(f"Invalid input: {e}")


def format_output(result):
    """Formats and displays results clearly."""
    return f"Result: {result}"

# calculator/error_handling.py
def handle_exception(e):
    """Handles exceptions gracefully."""
    if isinstance(e, ZeroDivisionError):
        return "Error: Division by zero."
    elif isinstance(e, ValueError):
        return f"Error: {e}"
    else:
        return f"An unexpected error occurred: {e}"


# calculator/cli_calculator.py
import argparse
from arithmetic_operations import add, subtract, multiply, divide
from input_output import parse_input, format_output
from error_handling import handle_exception

def main():
    parser = argparse.ArgumentParser(description="A simple CLI calculator.")
    parser.add_argument("expression", help="Arithmetic expression (e.g., 10 + 20)")
    args = parser.parse_args()

    try:
        num1, operator, num2 = parse_input(args.expression)
        if operator == '+':
            result = add(num1, num2)
        elif operator == '-':
            result = subtract(num1, num2)
        elif operator == '*':
            result = multiply(num1, num2)
        elif operator == '/':
            result = divide(num1, num2)
        else:
            raise ValueError("Invalid operator.")
        print(format_output(result))
    except Exception as e:
        print(handle_exception(e))

if __name__ == "__main__":
    main()


# calculator/test_calculator.py
import pytest
from arithmetic_operations import add, subtract, multiply, divide
from input_output import parse_input
from cli_calculator import main

def test_addition():
    assert add(2, 3) == 5

def test_subtraction():
    assert subtract(5, 2) == 3

def test_multiplication():
    assert multiply(4, 5) == 20

def test_division():
    assert divide(10, 2) == 5
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_parse_input():
    assert parse_input("2 + 3") == (2.0, "+", 3.0)
    with pytest.raises(ValueError):
        parse_input("2 + 3 + 4")
    with pytest.raises(ValueError):
        parse_input("abc + 3")


#To run the tests:
# 1. Save the files above into folders: calculator/arithmetic_operations.py, calculator/input_output.py, calculator/error_handling.py, calculator/cli_calculator.py, calculator/test_calculator.py
# 2. Navigate to the calculator directory in your terminal.
# 3. Run: pytest
