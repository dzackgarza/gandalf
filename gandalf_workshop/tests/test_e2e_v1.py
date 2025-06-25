import pytest
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from gandalf_workshop.workshop_manager import WorkshopManager
from gandalf_workshop.specs.data_models import (
    PlanOutput,
    CodeOutput,
    AuditOutput,
    AuditStatus,
    # AgentOutputStatus, # Not currently used, consider removing if not planned for V1
)

# Standard base directory for commission work as used by WorkshopManager
COMMISSION_WORK_BASE_DIR = Path("gandalf_workshop/commission_work")


@pytest.fixture(scope="function")
def manager_v1():
    """Provides a WorkshopManager instance for V1 E2E tests."""
    # WorkshopManager __init__ is simple and takes no args currently
    return WorkshopManager()


@pytest.fixture
def unique_commission_id(request):
    """Creates a unique commission ID based on the test function name."""
    # Using a prefix to easily identify test-generated commission directories
    return f"e2e_v1_{request.node.name}"


@pytest.fixture(scope="function")
def auto_cleanup_commission_dir(unique_commission_id):
    """
    Cleans up the specific commission work directory created by a test
    using its unique_commission_id. This runs after each test that uses it.
    """
    test_commission_dir = COMMISSION_WORK_BASE_DIR / unique_commission_id

    # Clean before test, if it exists from a previous failed run
    if test_commission_dir.exists():
        shutil.rmtree(test_commission_dir)

    yield  # Test runs here

    # Clean after test
    if test_commission_dir.exists():
        shutil.rmtree(test_commission_dir)


# Dummy test to ensure fixtures are working as expected.
# It uses auto_cleanup_commission_dir to ensure its generated directory is cleaned.
def test_dummy_e2e_v1_setup_works(
    manager_v1, unique_commission_id, auto_cleanup_commission_dir, capsys
):
    """
    A dummy test to ensure the fixture setup for manager, commission ID,
    and cleanup works.
    It will create a dummy directory to check the cleanup.
    """
    assert manager_v1 is not None
    assert unique_commission_id.startswith("e2e_v1_test_dummy_e2e_v1_setup_works")

    # Simulate WorkshopManager creating this directory during a commission run
    dummy_commission_path = COMMISSION_WORK_BASE_DIR / unique_commission_id
    dummy_commission_path.mkdir(parents=True, exist_ok=True)
    assert dummy_commission_path.exists()

    # The auto_cleanup_commission_dir fixture will remove this after the test.
    print(f"Dummy test ran with commission ID: {unique_commission_id}")
    print(f"Created dummy directory: {dummy_commission_path}")


USER_PROMPT = "Create a simple Python script that prints numbers 1 to 5."
MOCK_PLAN_TASKS = ["Write a for loop to print numbers 1 to 5 in Python."]


@patch("gandalf_workshop.workshop_manager.initialize_planner_agent_v1")
@patch(
    "gandalf_workshop.workshop_manager.CodeOutput"
)  # Mocking direct instantiation for Coder
@patch(
    "gandalf_workshop.workshop_manager.AuditOutput"
)  # Mocking direct instantiation for Auditor
def test_successful_v1_workflow(
    MockAuditOutput,
    MockCodeOutput,
    MockInitializePlannerV1,
    manager_v1,
    unique_commission_id,
    auto_cleanup_commission_dir,  # Ensures cleanup
    capsys,
):
    """
    Tests the V1 commission workflow for a successful scenario,
    mocking all agent interactions.
    """
    # Configure Mocks
    # 1. Planner
    mock_plan_instance = PlanOutput(tasks=MOCK_PLAN_TASKS)
    MockInitializePlannerV1.return_value = mock_plan_instance

    # 2. Coder (mocking CodeOutput which is how WorkshopManager currently gets coder result)
    # The actual code file will be created by WorkshopManager's current mock Coder logic
    # based on the plan. We need to ensure our mock plan is compatible or enhance this.
    # For this test, we'll assume the mock coder in WorkshopManager handles the MOCK_PLAN_TASKS
    # and creates a predictable file.
    # Let's make the mock plan generic enough that the WM's mock coder handles it.
    # The WM's mock coder creates 'output.txt' for non-hello-world plans.
    expected_code_filename = "output.txt"
    mock_code_path = (
        COMMISSION_WORK_BASE_DIR / unique_commission_id / expected_code_filename
    )

    # This CodeOutput is what the WM's *internal* mock Coder part would effectively return.
    # The test is more about the WM calling these parts in sequence.
    # So, MockCodeOutput is for the *Auditor's* input, not the Coder's direct output to WM.
    # The WM's internal mock coder creates a file and returns its path.
    # Then it *instantiates* CodeOutput for the auditor.
    # This is a bit confusing due to current WM structure. We mock what WM *uses*.

    # The actual CodeOutput instance will be created *inside* WorkshopManager's run_v1_commission.
    # We are mocking the *class* CodeOutput so when WM calls CodeOutput(...), it gets our mock.
    mock_code_output_instance = MagicMock(spec=CodeOutput)
    mock_code_output_instance.code_path = mock_code_path
    mock_code_output_instance.message = "Mock code generated successfully."
    MockCodeOutput.return_value = mock_code_output_instance

    # 3. Auditor (mocking AuditOutput)
    mock_audit_output_instance = MagicMock(spec=AuditOutput)
    mock_audit_output_instance.status = AuditStatus.SUCCESS
    mock_audit_output_instance.message = "Mock audit passed."
    MockAuditOutput.return_value = mock_audit_output_instance

    # Run the commission
    result_path = manager_v1.run_v1_commission(USER_PROMPT, unique_commission_id)

    # Assertions
    # 1. Planner was called
    MockInitializePlannerV1.assert_called_once_with(USER_PROMPT, unique_commission_id)

    # 2. Coder produced output (file exists as per WM's internal mock Coder)
    assert (
        result_path == mock_code_path
    )  # WM returns the code_path from its internal Coder logic
    assert (
        mock_code_path.exists()
    )  # Check the file was actually created by WM's mock Coder
    # Content check for the WM's current mock coder output for generic plan
    with open(mock_code_path, "r") as f:
        content = f.read()
        assert f"Content for: {USER_PROMPT}" in content
        assert f"Based on plan: {MOCK_PLAN_TASKS}" in content

    # 3. Auditor was called (implicitly, because MockAuditOutput was used by WM)
    # We verify that WorkshopManager instantiated CodeOutput with the correct path
    # (or rather, the path that its internal mock coder determined)
    # And that AuditOutput was instantiated with the success status.
    # This is indirect. A direct check would be to mock `initialize_coder_agent_v1` and `initialize_auditor_agent_v1`
    # if WM used them. Since it directly instantiates CodeOutput/AuditOutput for now (or has mock logic),
    # we patch those classes.

    # Verify CodeOutput was instantiated by WM as expected (for the auditor's input)
    # The path used here should be what WM's mock coder actually created.
    # WM's internal Coder logic:
    # output_file = commission_work_dir / "output.txt" (if not hello world)
    # code_output = CodeOutput(code_path=output_file, message=...)
    # We mocked CodeOutput class, so its call args can be checked if needed, but it's tricky
    # because the instance is `mock_code_output_instance`.
    # It's simpler to assert that the final `result_path` is correct and the flow completed.

    # 4. Final result and logs
    captured = capsys.readouterr()
    assert (
        f"===== Starting V1 Workflow for Commission: {unique_commission_id} ====="
        in captured.out
    )
    # Check for truncated plan log
    expected_plan_log = str(MOCK_PLAN_TASKS)
    if len(expected_plan_log) > 50:
        expected_plan_log = expected_plan_log[:47] + "..."
    assert (
        f"Planner Agent returned plan: {expected_plan_log}" in captured.out
    )  # WM logs the plan
    assert (
        f"Coder Agent generated code at: {mock_code_path}" in captured.out
    )  # WM logs the path from its mock coder
    assert (
        f"Auditor Agent reported: {AuditStatus.SUCCESS} - Mock audit passed."
        in captured.out
    )
    assert (
        f"===== V1 Workflow for Commission: {unique_commission_id} Completed Successfully ====="
        in captured.out
    )


@patch("gandalf_workshop.workshop_manager.initialize_planner_agent_v1")
@patch("gandalf_workshop.workshop_manager.CodeOutput")
@patch("gandalf_workshop.workshop_manager.AuditOutput")
def test_audit_failure_v1_workflow(
    MockAuditOutput,
    MockCodeOutput,
    MockInitializePlannerV1,
    manager_v1,
    unique_commission_id,
    auto_cleanup_commission_dir,
    capsys,
):
    """
    Tests the V1 commission workflow where the auditor reports a failure.
    """
    # Configure Mocks
    mock_plan_instance = PlanOutput(tasks=MOCK_PLAN_TASKS)
    MockInitializePlannerV1.return_value = mock_plan_instance

    expected_code_filename = "output.txt"  # From WM's mock coder
    mock_code_path = (
        COMMISSION_WORK_BASE_DIR / unique_commission_id / expected_code_filename
    )

    mock_code_output_instance = MagicMock(spec=CodeOutput)
    mock_code_output_instance.code_path = mock_code_path
    mock_code_output_instance.message = "Mock code generated (for failure test)."
    MockCodeOutput.return_value = mock_code_output_instance

    mock_audit_failure_message = "Critical security flaw detected by mock!"
    mock_audit_output_instance = MagicMock(spec=AuditOutput)
    mock_audit_output_instance.status = AuditStatus.FAILURE
    mock_audit_output_instance.message = mock_audit_failure_message
    MockAuditOutput.return_value = mock_audit_output_instance

    # Run the commission and expect an exception
    with pytest.raises(Exception) as excinfo:
        manager_v1.run_v1_commission(USER_PROMPT, unique_commission_id)

    # Assertions
    MockInitializePlannerV1.assert_called_once_with(USER_PROMPT, unique_commission_id)

    # File should still be created by WM's mock coder before audit
    assert mock_code_path.exists()

    assert (
        f"Audit failed for commission '{unique_commission_id}': {mock_audit_failure_message}"
        in str(excinfo.value)
    )

    captured = capsys.readouterr()
    assert (
        f"===== Starting V1 Workflow for Commission: {unique_commission_id} ====="
        in captured.out
    )
    # Check for truncated plan log
    expected_plan_log = str(MOCK_PLAN_TASKS)
    if len(expected_plan_log) > 50:
        expected_plan_log = expected_plan_log[:47] + "..."
    assert f"Planner Agent returned plan: {expected_plan_log}" in captured.out
    assert f"Coder Agent generated code at: {mock_code_path}" in captured.out
    assert (
        f"Auditor Agent reported: {AuditStatus.FAILURE} - {mock_audit_failure_message}"
        in captured.out
    )
    assert (
        f"Commission '{unique_commission_id}' failed audit. Reason: {mock_audit_failure_message}"
        in captured.out
    )
    assert (
        f"===== V1 Workflow for Commission: {unique_commission_id} Completed Successfully ====="
        not in captured.out
    )


# No new dependencies are needed for this structure; pytest and unittest.mock are standard.
# requirements-dev.txt should already cover these.
