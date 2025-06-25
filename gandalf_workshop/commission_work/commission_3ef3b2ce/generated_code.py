# adder.py


def add_numbers(x, y):
    """Adds two numbers and returns the sum.

    Args:
        x: The first number.
        y: The second number.

    Returns:
        The sum of x and y.  Raises TypeError if inputs are not numbers.

    """
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise TypeError("Inputs must be numbers.")
    return x + y


# test_adder.py

import pytest
from adder import add_numbers


def test_positive_integers():
    assert add_numbers(2, 3) == 5


def test_negative_integers():
    assert add_numbers(-2, -3) == -5


def test_mixed_integers():
    assert add_numbers(2, -3) == -1
    assert add_numbers(-2, 3) == 1


def test_positive_floats():
    assert add_numbers(2.5, 3.5) == 6.0


def test_negative_floats():
    assert add_numbers(-2.5, -3.5) == -6.0


def test_mixed_floats():
    assert add_numbers(2.5, -3.5) == -1.0
    assert add_numbers(-2.5, 3.5) == 1.0


def test_zero_positive():
    assert add_numbers(0, 5) == 5
    assert add_numbers(5, 0) == 5


def test_zero_negative():
    assert add_numbers(0, -5) == -5
    assert add_numbers(-5, 0) == -5


def test_type_error():
    with pytest.raises(TypeError):
        add_numbers("2", 3)
    with pytest.raises(TypeError):
        add_numbers(2, "3")
    with pytest.raises(TypeError):
        add_numbers("2", "3")
