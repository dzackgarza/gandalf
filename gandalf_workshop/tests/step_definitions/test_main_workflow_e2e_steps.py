import subprocess
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load scenarios from the feature file
scenarios("../features/main_workflow_e2e.feature")


# Fixture to share data between steps
@pytest.fixture
def cli_result_context():
    return {}


@when(parsers.parse('I run the Gandalf Workshop CLI with the prompt "{prompt_text}"'))
def run_cli_with_prompt(cli_result_context, prompt_text):
    try:
        # Ensure that we are running the main.py from the repository root.
        # This assumes that pytest is run from the repository root.
        process = subprocess.run(
            ["python", "main.py", "--prompt", prompt_text],
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception for non-zero exit codes
            timeout=30,  # Add a timeout to prevent tests from hanging indefinitely
        )
        cli_result_context["stdout"] = process.stdout
        cli_result_context["stderr"] = process.stderr
        cli_result_context["returncode"] = process.returncode
    except FileNotFoundError:
        pytest.fail(
            "main.py not found. Make sure you are running pytest from the repository root."
        )
    except subprocess.TimeoutExpired:
        pytest.fail("CLI execution timed out.")
    except Exception as e:
        pytest.fail(f"CLI execution failed with an unexpected error: {e}")


@then("the output should indicate the commission was received")
def check_commission_received(cli_result_context):
    assert "Received new commission request" in cli_result_context.get(
        "stdout", ""
    ), f"Commission received message not found in stdout. Output:\n{cli_result_context.get('stdout')}"


@then("the output should show a commission ID being assigned")
def check_commission_id_assigned(cli_result_context):
    assert "Assigning Commission ID: commission_" in cli_result_context.get(
        "stdout", ""
    ), f"Commission ID assignment message not found in stdout. Output:\n{cli_result_context.get('stdout')}"


@then("the output should indicate the commission was processed")
def check_commission_processed(cli_result_context):
    # The commission can either succeed or fail, both count as "processed" in this context.
    # The workshop_manager.py currently does not produce functional code, so it might "fail"
    # in terms of its own logic, but the main.py script should still report completion.
    stdout = cli_result_context.get("stdout", "")
    assert (
        "processed successfully." in stdout
        or "failed or was halted during processing." in stdout
    ), f"Commission processed message not found in stdout. Output:\n{stdout}"
    # Additionally, we expect a zero return code if main.py completed its flow,
    # even if the underlying commission "failed" logically.
    # If main.py itself crashes, returncode would be non-zero.
    assert (
        cli_result_context.get("returncode") == 0
    ), f"Expected return code 0, but got {cli_result_context.get('returncode')}. Stderr:\n{cli_result_context.get('stderr')}"
