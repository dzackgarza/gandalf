import pytest
from gandalf_workshop.artisan_guildhall.artisans import initialize_coder_agent_v1


def test_initialize_coder_agent_v1_hello_world():
    """
    Tests the V1 Coder agent with a 'hello world' task.
    """
    task_description = "Create a Python script that prints 'Hello, World!'"
    expected_code = "print('Hello, World!')"
    generated_code = initialize_coder_agent_v1(
        task_description, commission_id="test_hw_01"
    )
    assert generated_code == expected_code


def test_initialize_coder_agent_v1_add_function():
    """
    Tests the V1 Coder agent with an 'add function' task.
    """
    task_description = "Write a Python function called 'add' that takes two numbers and returns their sum."
    expected_code = (
        "def add(a, b):\n" '    """Adds two numbers."""\n' "    return a + b"
    )
    generated_code = initialize_coder_agent_v1(
        task_description, commission_id="test_add_func_01"
    )
    assert generated_code == expected_code


def test_initialize_coder_agent_v1_dog_class():
    """
    Tests the V1 Coder agent with a 'Dog class' task.
    """
    task_description = "Create a Python class named Dog with an __init__ method that takes a name, and a bark method."
    expected_code = (
        "class Dog:\n"
        "    def __init__(self, name):\n"
        "        self.name = name\n\n"
        "    def bark(self):\n"
        '        return f"{self.name} says woof!"'
    )
    generated_code = initialize_coder_agent_v1(
        task_description, commission_id="test_dog_class_01"
    )
    assert generated_code == expected_code


def test_initialize_coder_agent_v1_generic_task():
    """
    Tests the V1 Coder agent with a generic task it doesn't have specific mock logic for.
    """
    task_description = "Implement a sorting algorithm."
    expected_code = (
        f"# Code for: {task_description}\n" "pass  # Placeholder implementation"
    )
    generated_code = initialize_coder_agent_v1(
        task_description, commission_id="test_generic_01"
    )
    assert generated_code == expected_code


def test_initialize_coder_agent_v1_no_commission_id():
    """
    Tests that the agent works fine when no commission_id is provided (using default).
    """
    task_description = "Simple print statement"
    # The actual output for "Simple print statement" will be the generic one
    expected_code = (
        f"# Code for: {task_description}\n" "pass  # Placeholder implementation"
    )
    generated_code = initialize_coder_agent_v1(task_description)
    assert generated_code == expected_code
