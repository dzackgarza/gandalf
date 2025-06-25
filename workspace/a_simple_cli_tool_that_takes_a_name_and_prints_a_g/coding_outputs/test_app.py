import pytest
from unittest.mock import patch
import subprocess
# APP_NAME_PLACEHOLDER will be replaced by the loader function
from app import generate_greeting, main as app_main

def test_generate_greeting_with_name():
    assert generate_greeting("Alice") == "Hello, Alice!"

def test_generate_greeting_without_name_default():
    assert generate_greeting() == "Hello, World!"
    assert generate_greeting("") == "Hello, World!" # Test empty string name

def test_cli_with_name_argument(capsys):
    # This tests the main function directly by mocking sys.argv
    with patch('sys.argv', ['app.py', '--name', 'Bob']):
        app_main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, Bob!"

def test_cli_without_name_argument(capsys):
    with patch('sys.argv', ['app.py']):
        app_main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, World!"

# Example of a subprocess test (might be more robust for CLI testing)
def test_cli_subprocess_with_name():
    result = subprocess.run(['python', 'app.py', '--name', 'Charlie'], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert result.stdout.strip() == "Hello, Charlie!"

def test_cli_subprocess_without_name():
    result = subprocess.run(['python', 'app.py'], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert result.stdout.strip() == "Hello, World!"
