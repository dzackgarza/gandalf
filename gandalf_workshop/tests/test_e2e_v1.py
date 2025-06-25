import pytest
import shutil
import subprocess
import sys
import logging  # Added for caplog.set_level
from pathlib import Path

# from unittest.mock import patch, MagicMock # Not needed for true E2E if not mocking planner

from gandalf_workshop.workshop_manager import WorkshopManager
from gandalf_workshop.specs.data_models import (
    # PlanOutput, # Not directly used in test if not mocking planner
    # CodeOutput, # Not directly used in test as it's an internal detail
    # AuditOutput, # Not directly used in test as it's an internal detail
    AuditStatus,
)

# Standard base directory for commission work as used by WorkshopManager
COMMISSION_WORK_BASE_DIR = Path("gandalf_workshop/commission_work")


@pytest.fixture(scope="function")
def manager_v1():
    """Provides a WorkshopManager instance for V1 E2E tests."""
    return WorkshopManager()


@pytest.fixture
def unique_commission_id(request):
    """Creates a unique commission ID based on the test function name."""
    return f"e2e_v1_{request.node.name}"


@pytest.fixture(scope="function")
def auto_cleanup_commission_dir(unique_commission_id):
    """
    Cleans up the specific commission work directory created by a test
    using its unique_commission_id. This runs after each test that uses it.
    """
    test_commission_dir = COMMISSION_WORK_BASE_DIR / unique_commission_id
    if test_commission_dir.exists():
        shutil.rmtree(test_commission_dir)
    yield
    if test_commission_dir.exists():
        shutil.rmtree(test_commission_dir)


def test_e2e_hello_world_generation(
    manager_v1,
    unique_commission_id,
    auto_cleanup_commission_dir,
    caplog,  # Changed from capsys
):
    """
    Tests the full E2E V1 workflow for a 'hello world' prompt.
    It uses the actual basic Planner, Coder, and Auditor agents.
    """
    user_prompt = "Please create a hello world program in Python."
    expected_plan_tasks = ["Create a Python file that prints 'Hello, World!'"]
    expected_code_filename = "main.py"  # Coder agent now creates main.py
    expected_code_content = 'print("Hello, World!")\n'  # Indentation fixed
    expected_output_message = "Hello, World!\n"

    expected_output_message = "Hello, World!\n"

    # Run the commission
    caplog.set_level(
        logging.INFO, logger="gandalf_workshop.workshop_manager"
    )  # Set log level
    result_path = manager_v1.run_v1_commission(user_prompt, unique_commission_id)

    # Assertions
    # 1. Coder produced the correct output file
    expected_file_path = (
        COMMISSION_WORK_BASE_DIR / unique_commission_id / expected_code_filename
    )
    assert result_path == expected_file_path
    assert expected_file_path.exists(), "Generated code file should exist."
    assert expected_file_path.is_file(), "Generated code path should be a file."

    # 2. Content of the generated file is correct
    with open(expected_file_path, "r") as f:
        content = f.read()
    assert content == expected_code_content, "Generated file content is incorrect."

    # 3. Execute the generated Python script and check its output
    try:
        process_result = subprocess.run(
            [sys.executable, str(expected_file_path)],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,  # Add a timeout
        )
        assert (
            process_result.stdout == expected_output_message
        ), f"Script output incorrect. Got: '{process_result.stdout}'"
        assert process_result.stderr == "", "Script stderr should be empty."
    except subprocess.CalledProcessError as e:
        pytest.fail(
            f"Generated script failed to execute. Error: {e}\nStdout: {e.stdout}\nStderr: {e.stderr}"
        )
    except subprocess.TimeoutExpired:
        pytest.fail("Generated script execution timed out.")

    # 4. Check logs for key messages (Planner, Coder, Auditor success)
    log_text = caplog.text
    assert (
        f"===== Starting V1 Workflow for Commission: {unique_commission_id} ====="
        in log_text
    )
    # Check for planner log (actual planner is used)
    # Example: "Workshop Manager: Planner Agent returned plan: ['Create a Python file that prints \'Hello, Worl..."
    # Making this check more robust to minor string representation changes and truncation
    assert "Planner Agent returned plan:" in log_text
    # Check for the beginning of the task description, which should not be truncated.
    assert "[\"Create a Python file that prints 'Hello, W" in log_text

    # Check for coder log
    # Example: "Workshop Manager: Coder Agent completed. Code path: ..., Message: Successfully created main.py..."
    assert "Coder Agent completed." in log_text
    assert f"Code path: {expected_file_path}" in log_text
    assert "Successfully created main.py" in log_text  # Check for coder success message

    # Check for auditor log (actual auditor is used)
    # Example: "Workshop Manager: Auditor Agent reported: AuditStatus.SUCCESS - Syntax OK."
    assert "Auditor Agent reported:" in log_text
    assert f"{AuditStatus.SUCCESS.value}" in log_text  # Check for SUCCESS status
    assert "Syntax OK." in log_text  # Check for auditor success message

    assert (
        f"===== V1 Workflow for Commission: {unique_commission_id} Completed Successfully ====="
        in log_text
    )


def test_e2e_audit_failure_syntax_error(
    manager_v1,
    unique_commission_id,
    auto_cleanup_commission_dir,
    caplog,
    capsys,  # Added capsys back
    # We need to mock the Coder to produce bad code for this test
    # Or, have a specific plan that the V1 Coder interprets as "make bad code"
    # For true E2E, it's better if the Planner can instruct this.
    # Let's try to make the planner output a task that the coder will intentionally make syntax error for.
    # This requires modifying the planner and coder, which is beyond this step.
    # So, for now, we will mock `initialize_coder_agent_v1` to return a CodeOutput
    # pointing to a file with a syntax error.
    monkeypatch,
):
    """
    Tests the V1 E2E workflow where the Auditor correctly reports a failure
    due to a syntax error in the code produced by the Coder.
    """
    user_prompt = "Create a python program with a syntax error."
    # The actual planner will generate a generic plan for this.
    # We will then intercept the call to the coder to make it produce bad code.

    commission_dir = COMMISSION_WORK_BASE_DIR / unique_commission_id
    commission_dir.mkdir(
        parents=True, exist_ok=True
    )  # Ensure dir exists for bad_code_file

    bad_code_filename = "syntax_error.py"
    bad_code_file_path = commission_dir / bad_code_filename
    with open(bad_code_file_path, "w") as f:
        f.write("print 'this is a syntax error in Python 3'\n")

    # Mock the Coder to return the path to this bad file
    # We need to import CodeOutput for this mock
    from gandalf_workshop.specs.data_models import CodeOutput
    from gandalf_workshop.artisan_guildhall import (
        artisans,
    )  # to get the original function

    original_coder = artisans.initialize_coder_agent_v1

    def mock_initialize_coder_agent_v1(
        plan_input, commission_id, output_target_dir
    ):  # Changed commission_id_arg to commission_id
        # Log that mock is called
        print(
            f"MOCK initialize_coder_agent_v1 called for {commission_id} with target {output_target_dir}"
        )
        # It should still create the file in the designated output_target_dir
        # The file is already created above, this mock just returns its path.
        return CodeOutput(
            code_path=bad_code_file_path,
            message="Coder intentionally produced code with syntax error (mocked).",
        )

    monkeypatch.setattr(
        "gandalf_workshop.workshop_manager.initialize_coder_agent_v1",
        mock_initialize_coder_agent_v1,
    )
    # Alternative: monkeypatch.setattr(artisans, "initialize_coder_agent_v1", mock_initialize_coder_agent_v1)
    # but workshop_manager has its own import.

    # but workshop_manager has its own import.

    # Run the commission and expect an exception
    caplog.set_level(
        logging.INFO
    )  # Set overall level for caplog to capture INFO from all relevant loggers
    with pytest.raises(Exception) as excinfo:
        manager_v1.run_v1_commission(user_prompt, unique_commission_id)

    # Assertions
    # 1. Exception message should indicate audit failure
    assert "Audit failed" in str(excinfo.value)
    # The actual auditor should report a syntax error
    assert "Syntax error:" in str(excinfo.value)  # From initialize_auditor_agent_v1

    # 2. Check logs
    log_text = caplog.text  # Use caplog.text
    # The print from the mock coder will still go to stdout/stderr if not configured otherwise
    captured_stdout_stderr = capsys.readouterr()

    assert (
        f"===== Starting V1 Workflow for Commission: {unique_commission_id} ====="
        in log_text  # Check against log_text
    )
    # Planner log will be for the generic plan for "Create a python program with a syntax error."
    assert "Planner Agent returned plan:" in log_text  # Check against log_text

    # Coder log (from the mock - this part is tricky as the mock uses print)
    # The "MOCK initialize_coder_agent_v1 called..." message from the mock coder's print()
    # will be in captured_stdout_stderr.out, not caplog.text.
    assert "MOCK initialize_coder_agent_v1 called" in captured_stdout_stderr.out
    # The WorkshopManager's log about the coder completing will be in caplog.text
    assert f"Coder Agent completed. Code path: {bad_code_file_path}" in log_text
    assert "Coder intentionally produced code with syntax error (mocked)." in log_text

    # Auditor log should show failure
    assert "Auditor Agent reported:" in log_text  # Check against log_text
    assert f"{AuditStatus.FAILURE.value}" in log_text  # Check against log_text
    # Example from auditor: "Syntax error: Missing parentheses in call to 'print'. Did you mean print(...)? (<unknown>, line 1)"
    assert "Syntax error" in log_text  # Actual error message from auditor (in log_text)

    assert (
        f"Commission '{unique_commission_id}' failed audit."
        in log_text  # Check against log_text
    )
    assert (
        f"===== V1 Workflow for Commission: {unique_commission_id} Completed Successfully ====="
        not in log_text  # Check against log_text
    )

    # Restore original coder if other tests in the same session need it
    # monkeypatch automatically handles teardown, so this might not be strictly necessary
    # but good for clarity if needed.
    # monkeypatch.setattr(artisans, "initialize_coder_agent_v1", original_coder)


# The dummy test can be removed or kept if useful for verifying fixture setup.
# For now, let's remove it to keep the file focused on E2E tests.
# def test_dummy_e2e_v1_setup_works(...)

# Note: The test_audit_failure_v1_workflow was complex to make truly E2E
# without modifying the existing Coder to intentionally produce bad code based on a plan.
# The solution uses monkeypatch to substitute the coder at runtime for that specific test.
# This is a common pattern for testing error paths that are hard to trigger naturally.
