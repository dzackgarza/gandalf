import streamlit as st
import numpy as np


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


st.title("Simple Calculator")

st.write("Enter two numbers:")

num1 = st.number_input("Number 1", value=0.0)
num2 = st.number_input("Number 2", value=0.0)

operation = st.selectbox("Select Operation", ["+", "-", "*", "/"])

if st.button("Calculate"):
    if operation == "+":
        result = add(num1, num2)
    elif operation == "-":
        result = subtract(num1, num2)
    elif operation == "*":
        result = multiply(num1, num2)
    elif operation == "/":
        result = divide(num1, num2)
    else:
        result = "Invalid Operation"
    st.success(f"Result: {result}")


# Testing functions (can be moved to a separate test file for better organization)
def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(1, -1) == 2
    assert subtract(0, 0) == 0


def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-1, 1) == -1
    assert multiply(0, 5) == 0


def test_divide():
    assert divide(6, 3) == 2.0
    assert divide(1, -1) == -1.0
    assert divide(10, 0) == "Division by zero!"


# Run tests (this part would ideally be in a separate test file and run with pytest)
test_add()
test_subtract()
test_multiply()
test_divide()
