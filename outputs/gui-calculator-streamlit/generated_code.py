import streamlit as st
import pytest

# Calculator Logic Module
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "Division by zero!"
    return x / y

# Streamlit UI Module
def main():
    st.title("Simple Calculator")

    st.write("Enter two numbers:")
    num1 = st.number_input("Number 1", value=0.0)
    num2 = st.number_input("Number 2", value=0.0)

    operation = st.selectbox("Select Operation:", ["+", "-", "*", "/"])

    if st.button("Calculate"):
        if operation == "+":
            result = add(num1, num2)
        elif operation == "-":
            result = subtract(num1, num2)
        elif operation == "*":
            result = multiply(num1, num2)
        elif operation == "/":
            result = divide(num1, num2)
        st.success(f"Result: {result}")


if __name__ == "__main__":
    main()


# Unit Tests
def test_add():
    assert add(2, 3) == 5
    assert add(-2, 3) == 1
    assert add(0, 0) == 0

def test_subtract():
    assert subtract(5, 2) == 3
    assert subtract(2, 5) == -3
    assert subtract(0, 0) == 0

def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-2, 3) == -6
    assert multiply(0, 0) == 0

def test_divide():
    assert divide(6, 2) == 3.0
    assert divide(5, 0) == "Division by zero!"
    assert divide(0, 5) == 0.0
