import pytest
import shutil
from pathlib import Path
import pytest
import shutil
from pathlib import Path
from gandalf_workshop.workshop_manager import WorkshopManager

# from gandalf_workshop.specs.data_models import PMReviewDecision # No longer directly used here

# Define test commission IDs and prompts
TEST_COMMISSION_ID_SUCCESS = "test_workflow_success_001"
TEST_PROMPT_SUCCESS = "Create a simple CLI tool for basic math operations. MVP focus."

TEST_COMMISSION_ID_PM_REJECT_ONCE = "test_workflow_pm_reject_once_002"
# Mock PM will reject this
TEST_PROMPT_PM_REJECT_ONCE = "Develop a complex enterprise system for global logistics."

TEST_COMMISSION_ID_PM_FAIL = "test_workflow_pm_fail_003"
TEST_PROMPT_PM_FAIL = (
    "Build an extremely complex AI that solves all world problems " "immediately."
)


@pytest.fixture(scope="function", autouse=True)
def cleanup_test_dirs():
    """Cleans up test-specific directories before and after each test."""
    base_dirs = [
        Path("gandalf_workshop/blueprints"),
        Path("gandalf_workshop/reviews"),
        Path("gandalf_workshop/commissions_in_progress"),
        Path("gandalf_workshop/quality_control_lab"),
        Path("gandalf_workshop/completed_commissions"),
    ]
    test_commission_ids = [
        TEST_COMMISSION_ID_SUCCESS,
        TEST_COMMISSION_ID_PM_REJECT_ONCE,
        TEST_COMMISSION_ID_PM_FAIL,
        "legacy_rev_test_004",  # From the legacy test
    ]

    dirs_to_clean_this_run = []
    for commission_id in test_commission_ids:
        for base_dir in base_dirs:
            dirs_to_clean_this_run.append(base_dir / commission_id)

    for test_dir in dirs_to_clean_this_run:
        if test_dir.exists():
            shutil.rmtree(test_dir)
    yield  # This is where the test runs
    for test_dir in dirs_to_clean_this_run:  # Corrected variable name here
        if test_dir.exists():
            shutil.rmtree(test_dir)


def test_workshop_manager_initialization():
    """Tests basic initialization of WorkshopManager."""
    manager = WorkshopManager(max_pm_review_cycles=1)
    assert manager is not None
    assert manager.max_pm_review_cycles == 1


def test_full_workflow_pm_direct_approval(capsys):
    """Tests the full workflow where PM approves the blueprint on the first review."""
    manager = WorkshopManager(max_pm_review_cycles=1)
    success = manager.execute_full_commission_workflow(
        user_prompt=TEST_PROMPT_SUCCESS,  # Mock PM approves "simple" or "MVP"
        commission_id=TEST_COMMISSION_ID_SUCCESS,
    )
    assert success is True

    # Verify directories were created
    blueprint_file = (
        Path("gandalf_workshop/blueprints")
        / TEST_COMMISSION_ID_SUCCESS
        / "blueprint.yaml"
    )
    assert blueprint_file.exists()

    # PM review file name is timestamped, so check if any review file exists
    review_dir = Path("gandalf_workshop/reviews") / TEST_COMMISSION_ID_SUCCESS
    review_files = list(review_dir.glob("pm_review_*.json"))
    assert len(review_files) > 0, "No PM review files found"

    # Check product, qc lab, and completed commissions (mocked parts)
    product_file = (
        Path("gandalf_workshop/commissions_in_progress")
        / TEST_COMMISSION_ID_SUCCESS
        / "product_v_scaffold"
        / "product_content.txt"
    )
    assert product_file.exists()

    qc_report_file = (
        Path("gandalf_workshop/quality_control_lab")
        / TEST_COMMISSION_ID_SUCCESS
        / "product_v_scaffold_inspection_report.json"
    )
    assert qc_report_file.exists()

    completed_dir = (
        Path("gandalf_workshop/completed_commissions") / TEST_COMMISSION_ID_SUCCESS
    )
    assert completed_dir.is_dir()

    captured = capsys.readouterr()
    assert (
        f"===== Full Workflow for Commission: {TEST_COMMISSION_ID_SUCCESS} Completed Successfully ====="  # noqa: E501
        in captured.out
    )
    assert "APPROVED by PM" in captured.out  # Ensure PM approval message is present


def test_full_workflow_pm_rejection_then_approval(capsys):
    """Tests the workflow where PM rejects, blueprint is revised, then PM approves."""
    manager = WorkshopManager(max_pm_review_cycles=2)  # Allow for one revision cycle

    # This prompt will be initially rejected by the mock PM, then revised to be "simple"
    success = manager.execute_full_commission_workflow(
        user_prompt=TEST_PROMPT_PM_REJECT_ONCE,
        commission_id=TEST_COMMISSION_ID_PM_REJECT_ONCE,
    )
    assert success is True

    captured = capsys.readouterr()
    assert "REVISION REQUESTED by PM" in captured.out  # First review
    # The "Revised project summary..." is written to the blueprint, not stdout by default
    # So we check the content of the revised blueprint file.
    assert "APPROVED by PM" in captured.out  # Second review
    assert (
        f"===== Full Workflow for Commission: {TEST_COMMISSION_ID_PM_REJECT_ONCE} Completed Successfully ====="  # noqa: E501
        in captured.out
    )

    # Check that a revised blueprint was created and contains the updated summary
    blueprint_dir = (
        Path("gandalf_workshop/blueprints") / TEST_COMMISSION_ID_PM_REJECT_ONCE
    )
    original_bp_path = blueprint_dir / "blueprint.yaml"
    revised_bp_paths = [
        p
        for p in blueprint_dir.iterdir()
        if p.name != original_bp_path.name and p.suffix == ".yaml"
    ]
    assert len(revised_bp_paths) > 0, "No revised blueprint file found"

    # Assume the latest revised blueprint is the one to check
    # This logic might need to be more robust if multiple revisions create multiple files
    # and the naming isn't strictly sequential for testing.
    # For the current mock, request_blueprint_strategic_revision creates a new file.
    revised_bp_to_check = max(revised_bp_paths, key=lambda p: p.stat().st_mtime)

    import yaml

    with open(revised_bp_to_check, "r") as f:
        revised_content = yaml.safe_load(f)
    assert "Revised project summary: now simple and MVP focused" in revised_content.get(
        "project_summary", ""
    ), "Revised project summary not found in the final revised blueprint"
    assert "Revised based on PM Review" in revised_content.get("revisions", [{}])[
        -1
    ].get("notes", "")


def test_full_workflow_pm_fails_max_cycles(capsys):
    """Tests the workflow where PM review fails due to exceeding max review cycles."""
    manager = WorkshopManager(
        max_pm_review_cycles=1
    )  # Only one attempt, will fail if first is REVISION_REQUESTED

    # This prompt will be rejected by the mock PM, and since max_pm_review_cycles is 1, it should fail.
    success = manager.execute_full_commission_workflow(
        user_prompt=TEST_PROMPT_PM_FAIL, commission_id=TEST_COMMISSION_ID_PM_FAIL
    )
    assert success is False

    captured = capsys.readouterr()
    assert "REVISION REQUESTED by PM" in captured.out
    assert (
        f"Max PM review cycles reached for {TEST_COMMISSION_ID_PM_FAIL}. "
        "Blueprint not approved."
    ) in captured.out
    assert (
        f"Commission '{TEST_COMMISSION_ID_PM_FAIL}' halted due to failed "
        "PM review process."
    ) in captured.out

    # Ensure product generation etc. did not happen
    product_dir = (
        Path("gandalf_workshop/commissions_in_progress") / TEST_COMMISSION_ID_PM_FAIL
    )
    assert not product_dir.exists()


def test_legacy_blueprint_revision_method_exists_and_runs():
    """
    Tests that the old `request_blueprint_revision` method still exists and
    can be called. This method is not part of the primary PM-driven flow for
    initial blueprinting but might be used for technical revisions later.
    """
    manager = WorkshopManager()
    commission_id = "legacy_rev_test_004"
    blueprint_dir = Path("gandalf_workshop/blueprints") / commission_id
    blueprint_dir.mkdir(parents=True, exist_ok=True)
    original_bp_path = blueprint_dir / "blueprint.yaml"
    with open(original_bp_path, "w") as f:
        f.write(
            "commission_id: legacy_rev_test_004\n"
            "project_summary: Test for legacy revision."
        )

    failure_history = {"error": "Technical flaw found by QA", "details": "..."}

    try:
        revised_path = manager.request_blueprint_revision(
            commission_id=commission_id,
            original_blueprint_path=original_bp_path,
            failure_history=failure_history,
        )
        assert revised_path.exists()
        assert revised_path.name != original_bp_path.name
    finally:
        if blueprint_dir.exists():
            shutil.rmtree(blueprint_dir)

    # To run these tests, navigate to the repository root and use:
    # python -m pytest
    # or if pytest is not found, ensure it's installed (pip install pytest)
    # and your PYTHONPATH is set up if needed, e.g.:
    # PYTHONPATH=. python -m pytest
    # For coverage:
    # PYTHONPATH=. python -m pytest --cov=gandalf_workshop --cov-report=html
    # (then open htmlcov/index.html)
    commission_id = "legacy_rev_test_004"
    blueprint_dir = Path("gandalf_workshop/blueprints") / commission_id
    blueprint_dir.mkdir(parents=True, exist_ok=True)
    original_bp_path = blueprint_dir / "blueprint.yaml"
    with open(original_bp_path, "w") as f:
        f.write(
            "commission_id: legacy_rev_test_004\n"
            "project_summary: Test for legacy revision."
        )

    failure_history = {"error": "Technical flaw found by QA", "details": "..."}

    try:
        revised_path = manager.request_blueprint_revision(
            commission_id=commission_id,
            original_blueprint_path=original_bp_path,
            failure_history=failure_history,
        )
        assert revised_path.exists()
        assert revised_path.name != original_bp_path.name
    finally:
        if blueprint_dir.exists():
            shutil.rmtree(blueprint_dir)


# To run these tests, navigate to the repository root and use:
# python -m pytest
# or if pytest is not found, ensure it's installed (pip install pytest)
# and your PYTHONPATH is set up if needed, e.g.:
# PYTHONPATH=. python -m pytest
# For coverage:
# PYTHONPATH=. python -m pytest --cov=gandalf_workshop --cov-report=html
# (then open htmlcov/index.html)
