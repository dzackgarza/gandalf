import pytest
import shutil
from pathlib import Path
from unittest.mock import patch

from gandalf_workshop.workshop_manager import WorkshopManager
from gandalf_workshop.specs.data_models import (
    PlanOutput,
    CodeOutput,
    AuditOutput,
    AuditStatus,
)

TEST_COMMISSION_ID = "test_v1_commission_001"
HELLO_WORLD_PROMPT = "Create a hello world program in Python."
OTHER_PROMPT = "Create something else."


@pytest.fixture(scope="function")
def manager():
    """Provides a WorkshopManager instance for V1 tests."""
    return WorkshopManager()


@pytest.fixture(scope="function", autouse=True)
def cleanup_commission_work_dir():
    """Cleans up the commission work directory before and after each test."""
    work_dir_base = Path("gandalf_workshop/commission_work")

    # Clean before test, if it exists from a previous failed run
    test_specific_dir = work_dir_base / TEST_COMMISSION_ID
    if test_specific_dir.exists():
        shutil.rmtree(test_specific_dir)

    yield  # This is where the test runs

    # Clean after test
    if test_specific_dir.exists():
        shutil.rmtree(test_specific_dir)
    # Clean up a generic dir too, if created by non-helloworld prompt tests
    generic_commission_id = "v1_commission"  # default id in run_v1_commission
    generic_dir = work_dir_base / generic_commission_id
    if generic_dir.exists():
        shutil.rmtree(generic_dir)


def test_workshop_manager_v1_initialization(manager):
    """Tests basic initialization of the V1 WorkshopManager."""
    assert manager is not None
    # V1 __init__ is very simple, mainly checking it doesn't error.


@patch("gandalf_workshop.workshop_manager.initialize_planner_agent_v1")
@patch(
    "gandalf_workshop.workshop_manager.CodeOutput"
)  # Still mocking CodeOutput as Coder is not yet real
@patch(
    "gandalf_workshop.workshop_manager.AuditOutput"
)  # Still mocking AuditOutput as Auditor is not yet real
def test_run_v1_commission_hello_world_success(
    MockAuditOutput, MockCodeOutput, MockInitializePlannerV1, manager, capsys
):
    """
    Tests the V1 commission workflow for a 'hello world' prompt,
    mocking the planner agent call and subsequent agent outputs.
    """
    # Configure mocks
    mock_plan_instance = PlanOutput(
        tasks=["Create a Python file that prints 'Hello, World!'"]
    )
    MockInitializePlannerV1.return_value = mock_plan_instance

    mock_code_path = Path(
        f"gandalf_workshop/commission_work/{TEST_COMMISSION_ID}/hello.py"
    )
    mock_code_instance = CodeOutput(
        code_path=mock_code_path, message="Python 'Hello, World!' generated."
    )
    MockCodeOutput.return_value = (
        mock_code_instance  # For when WorkshopManager instantiates it
    )

    mock_audit_instance = AuditOutput(
        status=AuditStatus.SUCCESS, message="Audit passed for 'Hello, World!'."
    )
    MockAuditOutput.return_value = (
        mock_audit_instance  # For when WorkshopManager instantiates it
    )

    result_path = manager.run_v1_commission(HELLO_WORLD_PROMPT, TEST_COMMISSION_ID)

    MockInitializePlannerV1.assert_called_once_with(
        HELLO_WORLD_PROMPT, TEST_COMMISSION_ID
    )
    assert result_path == mock_code_path
    assert result_path.exists()
    with open(result_path, "r") as f:
        content = f.read()
        assert content == "print('Hello, World!')\n"

    captured = capsys.readouterr()
    assert (
        f"===== Starting V1 Workflow for Commission: {TEST_COMMISSION_ID} ====="
        in captured.out
    )
    assert "Workshop Manager: Invoking Planner Agent" in captured.out
    assert "Workshop Manager: Invoking Coder Agent" in captured.out
    assert "Workshop Manager: Invoking Auditor Agent" in captured.out

    import re

    # Use regex for more flexible matching of the truncated planner log
    # Focusing on the key content due to inconsistencies in exact str representation
    planner_log_pattern = r"Workshop Manager: Planner Agent returned plan:.*?Create a Python file that prints 'Hello, Wor"
    assert re.search(
        planner_log_pattern, captured.out
    ), f"Expected planner log pattern not found in output. Pattern: {planner_log_pattern}\nOutput: {captured.out}"
    assert (
        f"Workshop Manager: Coder Agent generated code at: {mock_code_instance.code_path}"
        in captured.out
    )
    assert (
        f"Workshop Manager: Auditor Agent reported: {mock_audit_instance.status} - {mock_audit_instance.message}"
        in captured.out
    )
    assert (
        f"===== V1 Workflow for Commission: {TEST_COMMISSION_ID} Completed Successfully ====="
        in captured.out
    )


@patch("gandalf_workshop.workshop_manager.initialize_planner_agent_v1")
@patch("gandalf_workshop.workshop_manager.CodeOutput")  # Still mocking CodeOutput
@patch("gandalf_workshop.workshop_manager.AuditOutput")  # Still mocking AuditOutput
def test_run_v1_commission_audit_failure(
    MockAuditOutput, MockCodeOutput, MockInitializePlannerV1, manager, capsys
):
    """
    Tests the V1 commission workflow where the auditor reports a failure.
    """
    mock_plan_instance = PlanOutput(tasks=["Some task"])
    MockInitializePlannerV1.return_value = mock_plan_instance

    mock_code_path = Path(
        f"gandalf_workshop/commission_work/{TEST_COMMISSION_ID}/output.txt"
    )
    mock_code_instance = CodeOutput(code_path=mock_code_path, message="Some code.")
    MockCodeOutput.return_value = mock_code_instance

    mock_audit_failure_message = "Critical security flaw detected!"
    mock_audit_instance = AuditOutput(
        status=AuditStatus.FAILURE, message=mock_audit_failure_message
    )
    MockAuditOutput.return_value = mock_audit_instance

    with pytest.raises(Exception) as excinfo:
        manager.run_v1_commission(OTHER_PROMPT, TEST_COMMISSION_ID)

    MockInitializePlannerV1.assert_called_once_with(OTHER_PROMPT, TEST_COMMISSION_ID)
    assert (
        f"Audit failed for commission '{TEST_COMMISSION_ID}': {mock_audit_failure_message}"
        in str(excinfo.value)
    )

    # Check that the file was still created by the mock coder before audit failed
    assert mock_code_path.exists()

    captured = capsys.readouterr()
    assert (
        f"Workshop Manager: Commission '{TEST_COMMISSION_ID}' failed audit. Reason: {mock_audit_failure_message}"
        in captured.out
    )
    assert (
        f"===== V1 Workflow for Commission: {TEST_COMMISSION_ID} Completed Successfully ====="
        not in captured.out
    )


def test_run_v1_commission_other_prompt_mock_success(manager, capsys):
    """
    Tests V1 commission with a non-"hello world" prompt, relying on current mock success.
    This test verifies the path for generic prompts in the current mock implementation.
    """
    commission_id = "v1_non_hw_commission"
    other_prompt_work_dir = Path("gandalf_workshop/commission_work") / commission_id

    try:
        result_path = manager.run_v1_commission(OTHER_PROMPT, commission_id)
        assert result_path.name == "output.txt"
        assert result_path.exists()
        with open(result_path, "r") as f:
            content = f.read()
            assert f"Content for: {OTHER_PROMPT}" in content
            assert f"Task 1: Implement feature based on: {OTHER_PROMPT}" in content

        captured = capsys.readouterr()
        assert (
            f"===== V1 Workflow for Commission: {commission_id} Completed Successfully ====="
            in captured.out
        )
    finally:
        if other_prompt_work_dir.exists():
            shutil.rmtree(other_prompt_work_dir)


# Future tests could involve patching the actual agent initialization functions
# (e.g., initialize_planner_agent_v1) once they are implemented in artisans.py,
# rather than patching the data models themselves.
# For now, the direct patching of data model instantiation within run_v1_commission
# is a workaround for the current direct instantiation in the manager.
