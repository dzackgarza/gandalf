import sys

class ArithmeticOperations:
    """Handles all arithmetic operations for the calculator."""

    @staticmethod
    def add(a: float, b: float) -> float:
        """Add two numbers and return the result."""
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        """Subtract two numbers and return the result."""
        return a - b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        """Multiply two numbers and return the result."""
        return a * b

    @staticmethod
    def divide(a: float, b: float) -> float:
        """Divide two numbers and return the result."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

class UserInterface:
    """Handles all user interactions for the calculator."""

    def __init__(self):
        self.operations = ArithmeticOperations()

    def display_welcome(self):
        """Display welcome message and instructions."""
        print("Welcome to CLI Calculator!")
        print("Available operations: +, -, *, /")
        print("Enter 'quit' to exit the application.\n")

    def get_user_input(self) -> tuple:
        """Get user input for calculation and return the operation and numbers."""
        while True:
            user_input = input("Enter calculation (e.g., 2 + 3): ").strip()

            if user_input.lower() == 'quit':
                sys.exit("Goodbye!")

            try:
                parts = user_input.split()
                if len(parts) != 3:
                    raise ValueError("Invalid input format")

                num1 = float(parts[0])
                operator = parts[1]
                num2 = float(parts[2])

                if operator not in ['+', '-', '*', '/']:
                    raise ValueError("Invalid operator")

                return operator, num1, num2

            except ValueError as e:
                print(f"Error: {e}. Please try again.")
                print("Example format: 2 + 3 or 5.5 * 2.1")

    def perform_calculation(self, operator: str, num1: float, num2: float) -> float:
        """Perform the calculation based on the operator and return the result."""
        try:
            if operator == '+':
                return self.operations.add(num1, num2)
            elif operator == '-':
                return self.operations.subtract(num1, num2)
            elif operator == '*':
                return self.operations.multiply(num1, num2)
            elif operator == '/':
                return self.operations.divide(num1, num2)
        except ValueError as e:
            print(f"Error: {e}")
            return None

    def display_result(self, result: float):
        """Display the result of the calculation."""
        if result is not None:
            print(f"Result: {result}\n")

    def run(self):
        """Main loop for the calculator application."""
        self.display_welcome()

        while True:
            operator, num1, num2 = self.get_user_input()
            result = self.perform_calculation(operator, num1, num2)
            self.display_result(result)

def main():
    """Entry point for the calculator application."""
    calculator = UserInterface()
    calculator.run()

if __name__ == "__main__":
    main()