import streamlit as st

class Calculator:
    def __init__(self):
        self.current_input = ""
        self.previous_input = ""
        self.operation = None
        self.reset_calculator()

    def reset_calculator(self):
        self.current_input = "0"
        self.previous_input = ""
        self.operation = None

    def update_display(self, value):
        if self.current_input == "0" or self.current_input == "Error":
            self.current_input = value
        else:
            self.current_input += value

    def clear(self):
        self.reset_calculator()

    def backspace(self):
        if len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
        else:
            self.current_input = "0"

    def set_operation(self, op):
        if self.current_input != "Error":
            self.previous_input = self.current_input
            self.operation = op
            self.current_input = "0"

    def calculate(self):
        if self.operation and self.previous_input and self.current_input != "Error":
            try:
                prev = float(self.previous_input)
                current = float(self.current_input)

                if self.operation == "+":
                    result = prev + current
                elif self.operation == "-":
                    result = prev - current
                elif self.operation == "*":
                    result = prev * current
                elif self.operation == "/":
                    if current == 0:
                        self.current_input = "Error"
                        return
                    result = prev / current

                self.current_input = str(result)
                self.operation = None
                self.previous_input = ""
            except ValueError:
                self.current_input = "Error"

def create_button(label, on_click=None, args=None, width=1):
    if args is None:
        args = []
    return st.button(label, on_click=on_click, args=args, use_container_width=True)

def main():
    st.set_page_config(page_title="Streamlit Calculator", layout="centered")
    st.title("Calculator")

    calculator = Calculator()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_button("7", calculator.update_display, ["7"])
    with col2:
        create_button("8", calculator.update_display, ["8"])
    with col3:
        create_button("9", calculator.update_display, ["9"])
    with col4:
        create_button("/", calculator.set_operation, ["/"])

    with col1:
        create_button("4", calculator.update_display, ["4"])
    with col2:
        create_button("5", calculator.update_display, ["5"])
    with col3:
        create_button("6", calculator.update_display, ["6"])
    with col4:
        create_button("*", calculator.set_operation, ["*"])

    with col1:
        create_button("1", calculator.update_display, ["1"])
    with col2:
        create_button("2", calculator.update_display, ["2"])
    with col3:
        create_button("3", calculator.update_display, ["3"])
    with col4:
        create_button("-", calculator.set_operation, ["-"])

    with col1:
        create_button("0", calculator.update_display, ["0"])
    with col2:
        create_button("C", calculator.clear)
    with col3:
        create_button("⌫", calculator.backspace)
    with col4:
        create_button("+", calculator.set_operation, ["+"])

    with st.container():
        create_button("=", calculator.calculate, width=4)

    st.display(calculator.current_input)

if __name__ == "__main__":
    main()