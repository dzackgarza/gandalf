import pytest
import shutil
import logging # Added for caplog.set_level
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
@patch("gandalf_workshop.workshop_manager.initialize_coder_agent_v1")
@patch("gandalf_workshop.workshop_manager.initialize_auditor_agent_v1")
def test_run_v1_commission_hello_world_success(
    MockInitializeAuditorV1,
    MockInitializeCoderV1,
    MockInitializePlannerV1,
    manager,
    caplog,  # Changed from capsys
):
    """
    Tests the V1 commission workflow for a 'hello world' prompt,
    mocking all agent calls.
    """
    # --- Configure Mocks ---
    # 1. Planner Mock
    mock_plan_instance = PlanOutput(
        tasks=["Create a Python file that prints 'Hello, World!'"]
    )
    MockInitializePlannerV1.return_value = mock_plan_instance

    # 2. Coder Mock
    # The Coder agent is expected to create the file. For the unit test,
    # we simulate this by having the mock return a CodeOutput pointing to the expected path
    # and then we create this dummy file for assertion purposes.
    commission_work_dir = (
        Path("gandalf_workshop/commission_work") / TEST_COMMISSION_ID
    )
    # The actual coder agent creates 'main.py' for this plan
    expected_code_filename = "main.py"
    mock_code_path = commission_work_dir / expected_code_filename

    # Ensure the directory exists for the mock file creation
    commission_work_dir.mkdir(parents=True, exist_ok=True)
    # Create a dummy file that the Coder agent would have created
    with open(mock_code_path, "w") as f:
        f.write("print('Hello, World!')\n")

    mock_code_output_instance = CodeOutput(
        code_path=mock_code_path, message="Mock Coder: Python 'Hello, World!' generated."
    )
    MockInitializeCoderV1.return_value = mock_code_output_instance

    # 3. Auditor Mock
    mock_audit_output_instance = AuditOutput(
        status=AuditStatus.SUCCESS, message="Mock Auditor: Audit passed."
    )
    MockInitializeAuditorV1.return_value = mock_audit_output_instance

    # --- Run the Commission ---
    caplog.set_level(logging.INFO, logger="gandalf_workshop.workshop_manager") # Set log level
    result_path = manager.run_v1_commission(HELLO_WORLD_PROMPT, TEST_COMMISSION_ID)

    # --- Assertions ---
    # 1. Planner was called correctly
    MockInitializePlannerV1.assert_called_once_with(
        HELLO_WORLD_PROMPT, TEST_COMMISSION_ID
    )

    # 2. Coder was called correctly
    MockInitializeCoderV1.assert_called_once_with(
        plan_input=mock_plan_instance,
        commission_id=TEST_COMMISSION_ID,
        output_target_dir=commission_work_dir,
    )
    assert result_path == mock_code_path  # Path returned by WorkshopManager
    assert mock_code_path.exists()  # File created for the test
    with open(mock_code_path, "r") as f:
        content = f.read()
        assert content == "print('Hello, World!')\n"

    # 3. Auditor was called correctly
    MockInitializeAuditorV1.assert_called_once_with(
        code_input=mock_code_output_instance, commission_id=TEST_COMMISSION_ID
    )

    # 4. Check logs
    log_text = caplog.text
    assert (
        f"===== Starting V1 Workflow for Commission: {TEST_COMMISSION_ID} ====="
        in log_text
    )
    assert "Workshop Manager: Invoking Planner Agent" in log_text
    assert "Workshop Manager: Invoking Coder Agent" in log_text
    assert "Workshop Manager: Invoking Auditor Agent" in log_text

    # We need to import re for this
    import re
    # Use regex for more flexible matching of the truncated planner log
    # Focusing on the key content due to inconsistencies in exact str representation
    planner_log_pattern = r"Workshop Manager: Planner Agent returned plan:.*?Create a Python file that prints 'Hello, Wor"
    assert re.search(
        planner_log_pattern, log_text
    ), f"Expected planner log pattern not found in output. Pattern: {planner_log_pattern}\nOutput: {log_text}"

    # Check Coder agent completion log
    assert (
        f"Workshop Manager: Coder Agent completed. Code path: {mock_code_output_instance.code_path}, Message: {mock_code_output_instance.message}"
        in log_text
    )
    # Check Auditor agent reporting log
    assert (
        f"Workshop Manager: Auditor Agent reported: {mock_audit_output_instance.status} - {mock_audit_output_instance.message}"
        in log_text
    )
    assert (
        f"===== V1 Workflow for Commission: {TEST_COMMISSION_ID} Completed Successfully ====="
        in log_text
    )


@patch("gandalf_workshop.workshop_manager.initialize_planner_agent_v1")
@patch("gandalf_workshop.workshop_manager.initialize_coder_agent_v1")
@patch("gandalf_workshop.workshop_manager.initialize_auditor_agent_v1")
def test_run_v1_commission_audit_failure(
    MockInitializeAuditorV1,
    MockInitializeCoderV1,
    MockInitializePlannerV1,
    manager,
    caplog,  # Changed from capsys
):
    """
    Tests the V1 commission workflow where the auditor reports a failure.
    All agent calls are mocked.
    """
    # --- Configure Mocks ---
    # 1. Planner Mock
    mock_plan_instance = PlanOutput(tasks=["Some generic task"])
    MockInitializePlannerV1.return_value = mock_plan_instance

    # 2. Coder Mock
    commission_work_dir = (
        Path("gandalf_workshop/commission_work") / TEST_COMMISSION_ID
    )
    # For a generic task, the coder agent creates 'task_output.txt'
    expected_code_filename = "task_output.txt"
    mock_code_path = commission_work_dir / expected_code_filename

    commission_work_dir.mkdir(parents=True, exist_ok=True)
    # Create a dummy file that the Coder agent would have created
    with open(mock_code_path, "w") as f:
        f.write("Content for generic task.\n")

    mock_code_output_instance = CodeOutput(
        code_path=mock_code_path, message="Mock Coder: Generic content generated."
    )
    MockInitializeCoderV1.return_value = mock_code_output_instance

    # 3. Auditor Mock (configured to fail)
    mock_audit_failure_message = "Mock Auditor: Critical security flaw detected!"
    mock_audit_output_instance = AuditOutput(
        status=AuditStatus.FAILURE, message=mock_audit_failure_message
    )
    MockInitializeAuditorV1.return_value = mock_audit_output_instance

    MockInitializeAuditorV1.return_value = mock_audit_output_instance

    # --- Run the Commission ---
    caplog.set_level(logging.INFO, logger="gandalf_workshop.workshop_manager") # Set log level
    with pytest.raises(Exception) as excinfo:
        manager.run_v1_commission(OTHER_PROMPT, TEST_COMMISSION_ID)

    # --- Assertions ---
    # 1. Planner was called
    MockInitializePlannerV1.assert_called_once_with(OTHER_PROMPT, TEST_COMMISSION_ID)

    # 2. Coder was called
    MockInitializeCoderV1.assert_called_once_with(
        plan_input=mock_plan_instance,
        commission_id=TEST_COMMISSION_ID,
        output_target_dir=commission_work_dir,
    )
    # File should still be created by our mock setup before audit fails
    assert mock_code_path.exists()

    # 3. Auditor was called
    MockInitializeAuditorV1.assert_called_once_with(
        code_input=mock_code_output_instance, commission_id=TEST_COMMISSION_ID
    )

    # 4. Exception message check
    assert (
        f"Audit failed for commission '{TEST_COMMISSION_ID}': {mock_audit_failure_message}"
        in str(excinfo.value)
    )

    # 5. Check logs
    log_text = caplog.text
    assert (
        f"Workshop Manager: Commission '{TEST_COMMISSION_ID}' failed audit. Reason: {mock_audit_failure_message}"
        in log_text
    )
    # Check Coder agent completion log
    assert (
        f"Workshop Manager: Coder Agent completed. Code path: {mock_code_output_instance.code_path}, Message: {mock_code_output_instance.message}"
        in log_text
    )
    # Check Auditor agent reporting log - it should show failure
    assert (
        f"Workshop Manager: Auditor Agent reported: {mock_audit_output_instance.status} - {mock_audit_output_instance.message}"
        in log_text
    )
    assert (
        f"===== V1 Workflow for Commission: {TEST_COMMISSION_ID} Completed Successfully ====="
        not in log_text
    )


@patch("gandalf_workshop.workshop_manager.initialize_planner_agent_v1")
@patch("gandalf_workshop.workshop_manager.initialize_coder_agent_v1")
@patch("gandalf_workshop.workshop_manager.initialize_auditor_agent_v1")
def test_run_v1_commission_other_prompt_success_mocked_agents(
    MockInitializeAuditorV1,
    MockInitializeCoderV1,
    MockInitializePlannerV1,
    manager,
    caplog,  # Changed from capsys
):
    """
    Tests V1 commission with a non-"hello world" prompt, with all agent calls mocked
    to ensure the WorkshopManager logic flows correctly.
    """
    commission_id = "v1_other_prompt_commission" # Use a unique ID for this test

    # --- Configure Mocks ---
    # 1. Planner Mock for a generic prompt
    generic_task_description = f"Task based on: {OTHER_PROMPT}"
    mock_plan_instance = PlanOutput(tasks=[generic_task_description])
    MockInitializePlannerV1.return_value = mock_plan_instance

    # 2. Coder Mock for a generic task
    commission_work_dir = Path("gandalf_workshop/commission_work") / commission_id
    # Actual coder creates 'task_output.txt' for generic plans
    expected_code_filename = "task_output.txt"
    mock_code_path = commission_work_dir / expected_code_filename

    commission_work_dir.mkdir(parents=True, exist_ok=True)
    # Create a dummy file that the Coder agent would have created
    with open(mock_code_path, "w") as f:
        f.write(f"Content for: {OTHER_PROMPT}\nBased on plan: {[generic_task_description]}")

    mock_code_output_instance = CodeOutput(
        code_path=mock_code_path,
        message=f"Mock Coder: Generated content for {OTHER_PROMPT}.",
    )
    MockInitializeCoderV1.return_value = mock_code_output_instance

    # 3. Auditor Mock (successful audit)
    mock_audit_output_instance = AuditOutput(
        status=AuditStatus.SUCCESS, message="Mock Auditor: Audit passed for generic content."
    )
    MockInitializeAuditorV1.return_value = mock_audit_output_instance

    MockInitializeAuditorV1.return_value = mock_audit_output_instance

    # --- Run the Commission ---
    # Need to use the specific commission_id for this test
    caplog.set_level(logging.INFO, logger="gandalf_workshop.workshop_manager") # Set log level
    result_path = manager.run_v1_commission(OTHER_PROMPT, commission_id)

    # --- Assertions ---
    # 1. Planner was called
    MockInitializePlannerV1.assert_called_once_with(OTHER_PROMPT, commission_id)

    # 2. Coder was called
    MockInitializeCoderV1.assert_called_once_with(
        plan_input=mock_plan_instance,
        commission_id=commission_id,
        output_target_dir=commission_work_dir,
    )
    assert result_path == mock_code_path
    assert mock_code_path.exists()
    with open(mock_code_path, "r") as f:
        content = f.read()
        assert f"Content for: {OTHER_PROMPT}" in content
        assert generic_task_description in content

    # 3. Auditor was called
    MockInitializeAuditorV1.assert_called_once_with(
        code_input=mock_code_output_instance, commission_id=commission_id
    )

    # 4. Check logs for successful completion
    log_text = caplog.text
    assert (
        f"===== Starting V1 Workflow for Commission: {commission_id} ====="
        in log_text
    )
    assert (
        f"Workshop Manager: Coder Agent completed. Code path: {mock_code_path}" # Check part of message
        in log_text
    )
    assert (
        f"Workshop Manager: Auditor Agent reported: {AuditStatus.SUCCESS} - Mock Auditor: Audit passed for generic content."
        in log_text
    )
    assert (
        f"===== V1 Workflow for Commission: {commission_id} Completed Successfully ====="
        in log_text
    )

    # Cleanup for this specific test's directory if not covered by global fixture
    # The global fixture `cleanup_commission_work_dir` uses TEST_COMMISSION_ID and "v1_commission"
    # This test uses "v1_other_prompt_commission", so it needs its own cleanup.
    # This is better handled by parameterizing the cleanup fixture or ensuring unique IDs are always cleaned.
    # For now, explicit cleanup:
    if commission_work_dir.exists():
        shutil.rmtree(commission_work_dir)
