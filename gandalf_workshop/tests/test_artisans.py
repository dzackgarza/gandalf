from gandalf_workshop.artisan_guildhall import artisans
from gandalf_workshop.specs.data_models import (
    PlanOutput,
    CodeOutput,
    AuditOutput,
    AuditStatus,
    PMReviewDecision,  # Added this as it was used later but not imported with others
)
from pathlib import Path  # For test file creation


def test_initialize_planning_crew():
    """Tests that the placeholder planning crew function can be called."""
    # The function currently just prints.
    # In a real scenario, we'd check for a crew object or mock its dependencies.
    artisans.initialize_planning_crew()


def test_initialize_coding_crew():
    """Tests that the placeholder coding crew function can be called."""
    artisans.initialize_coding_crew()


def test_initialize_inspection_crew():
    """Tests that the placeholder inspection crew function can be called."""
    artisans.initialize_inspection_crew()


# Note: initialize_pm_review_crew is implicitly tested via test_workshop_manager.py
# and its own __main__ block in artisans.py provides some direct test cases.
# Adding a dedicated test here could be done for completeness if desired,
# but might be redundant if WorkshopManager tests cover its usage well.
# For now, focusing on the otherwise uncovered ones.


def test_initialize_pm_review_crew_mock_logic(tmp_path):
    """
    Tests the mock logic of initialize_pm_review_crew directly.
    This replicates the tests previously in artisans.py's __main__ block.
    """
    import yaml

    # PMReviewDecision is imported at the top of the file

    # Path is used by tmp_path fixture implicitly, but explicit import not needed here.

    commission_id = "pm_crew_test_001"
    mock_bp_dir = tmp_path / "blueprints" / commission_id
    mock_bp_dir.mkdir(parents=True, exist_ok=True)
    mock_bp_path = mock_bp_dir / "blueprint.yaml"

    # Test case 1: Complex project, expect REVISION_REQUESTED
    with open(mock_bp_path, "w") as bp_file:
        yaml.dump(
            {
                "commission_id": commission_id,
                "project_summary": "A very complex project that needs simplification for the MVP.",
                "key_objectives": ["Achieve world peace"],
                "revisions": [
                    {"version": "0.9", "date": "2023-01-01", "notes": "Initial Draft"}
                ],
            },
            bp_file,
        )

    review_path_complex = artisans.initialize_pm_review_crew(
        mock_bp_path, commission_id, blueprint_version="0.9"
    )
    assert review_path_complex.exists()
    with open(review_path_complex, "r") as rf:
        review_content_complex = yaml.safe_load(
            rf
        )  # PMReview is JSON, but yaml can load basic JSON
    assert (
        review_content_complex["decision"] == PMReviewDecision.REVISION_REQUESTED.value
    )
    assert "complex" in review_content_complex["rationale"].lower()

    # Test case 2: Simple project, expect APPROVED
    with open(mock_bp_path, "w") as bp_file:  # Overwrite the same blueprint file
        yaml.dump(
            {
                "commission_id": commission_id,
                "project_summary": "A very simple project.",
                "key_objectives": ["Achieve local peace"],
                "revisions": [
                    {"version": "1.0", "date": "2023-01-02", "notes": "Revised Draft"}
                ],
            },
            bp_file,
        )

    review_path_simple = artisans.initialize_pm_review_crew(
        mock_bp_path, commission_id, blueprint_version="1.0"
    )
    assert review_path_simple.exists()
    with open(review_path_simple, "r") as rf:
        review_content_simple = yaml.safe_load(rf)
    assert review_content_simple["decision"] == PMReviewDecision.APPROVED.value
    assert "simple or mvp scope" in review_content_simple["rationale"].lower()

    # Test case 3: Blueprint read error (e.g., non-existent file)
    # For this, we can pass a bad path. The function should handle it gracefully.
    # Note: The actual reviews_dir for this will be based on the commission_id.
    # We are primarily testing that it defaults to REVISION_REQUESTED.
    bad_bp_path = tmp_path / "blueprints" / "non_existent_bp.yaml"
    review_path_error = artisans.initialize_pm_review_crew(
        bad_bp_path, "error_test_commission", blueprint_version="0.0"
    )
    assert review_path_error.exists()
    with open(review_path_error, "r") as rf:
        review_content_error = yaml.safe_load(rf)
    assert review_content_error["decision"] == PMReviewDecision.REVISION_REQUESTED.value
    assert "Error reading blueprint" in review_content_error["rationale"]


# Tests for V1 Basic Agents
# PlanOutput is now imported at the top of the file.


def test_initialize_planner_agent_v1_hello_world():
    """Tests the V1 basic planner for a 'hello world' prompt."""
    prompt = "Please create a simple hello world program."
    commission_id = "test_hw_planner_001"

    plan_output = artisans.initialize_planner_agent_v1(prompt, commission_id)

    assert isinstance(plan_output, PlanOutput)
    assert plan_output.tasks == ["Create a Python file that prints 'Hello, World!'"]


# Tests for V1 Basic Coder Agent

# Path, PlanOutput, CodeOutput are imported at the top.
# We'll use tmp_path fixture for creating temporary files/dirs.


def test_initialize_coder_agent_v1_hello_world(tmp_path):
    """Tests V1 Coder Agent for 'Hello, World!' task."""
    commission_id = "test_coder_hw_001"
    plan = PlanOutput(tasks=["Create a Python file that prints 'Hello, World!'"])

    # Use a subdirectory within tmp_path for generated code to mimic real structure
    generated_code_dir = tmp_path / "generated_code"

    code_output = artisans.initialize_coder_agent_v1(
        plan, commission_id, output_dir=generated_code_dir
    )

    expected_file_path = generated_code_dir / commission_id / "main.py"

    assert isinstance(code_output, CodeOutput)
    assert code_output.code_path == expected_file_path
    assert "Successfully created main.py" in code_output.message
    assert expected_file_path.exists()
    assert expected_file_path.is_file()

    with open(expected_file_path, "r") as f:
        content = f.read()
    assert content == 'print("Hello, World!")\n'


def test_initialize_coder_agent_v1_generic_task(tmp_path):
    """Tests V1 Coder Agent for a generic task."""
    commission_id = "test_coder_generic_002"
    task_description = "Implement user login functionality."
    plan = PlanOutput(tasks=[task_description])

    generated_code_dir = tmp_path / "generated_code"

    code_output = artisans.initialize_coder_agent_v1(
        plan, commission_id, output_dir=generated_code_dir
    )

    expected_file_path = generated_code_dir / commission_id / "task_output.txt"

    assert isinstance(code_output, CodeOutput)
    assert code_output.code_path == expected_file_path
    assert "Successfully created task_output.txt" in code_output.message
    assert expected_file_path.exists()
    assert expected_file_path.is_file()

    with open(expected_file_path, "r") as f:
        content = f.read()
    assert content == f"Task from plan:\n{task_description}\n"


def test_initialize_coder_agent_v1_no_tasks(tmp_path):
    """Tests V1 Coder Agent when the plan has no tasks."""
    commission_id = "test_coder_notasks_003"
    plan = PlanOutput(tasks=[])  # Empty task list

    generated_code_dir = tmp_path / "generated_code"
    expected_output_path = generated_code_dir / commission_id

    code_output = artisans.initialize_coder_agent_v1(
        plan, commission_id, output_dir=generated_code_dir
    )

    assert isinstance(code_output, CodeOutput)
    assert code_output.code_path == expected_output_path  # Should be the directory
    assert "Coder Error: No tasks found in plan." in code_output.message
    # Ensure the directory was created even if no file was made
    assert expected_output_path.exists()
    assert expected_output_path.is_dir()
    # Check that no unexpected files were created
    assert not list(expected_output_path.glob("*"))


def test_initialize_coder_agent_v1_output_directory_creation(tmp_path):
    """Tests that the coder agent creates the commission-specific output directory."""
    commission_id = "test_coder_dir_creation_004"
    plan = PlanOutput(tasks=["Create a simple text file."])

    # Use a non-existent base directory to ensure it's created
    base_output_dir = tmp_path / "custom_generated_code_base"
    expected_commission_dir = base_output_dir / commission_id

    assert not base_output_dir.exists()  # Pre-condition: base directory does not exist

    artisans.initialize_coder_agent_v1(plan, commission_id, output_dir=base_output_dir)

    assert expected_commission_dir.exists()
    assert expected_commission_dir.is_dir()
    # Check if the task_output.txt was created inside
    expected_file_path = expected_commission_dir / "task_output.txt"
    assert expected_file_path.exists()
    assert expected_file_path.is_file()


# It might be challenging to directly test IOErrors for file writing
# without more complex mocking (e.g., mocking `open` or file system permissions).
# For V1, the current tests cover the main logic paths.
# If more robustness is needed around file system errors, advanced mocking
# or OS-level permission manipulation (which is complex and platform-dependent)
# would be required for tests. The current implementation logs IOErrors,
# and the function returns a CodeOutput with an error message, which is testable
# if such an error could be reliably triggered.


# Tests for V1 Basic Auditor Agent


def test_initialize_auditor_agent_v1_valid_syntax(tmp_path):
    """Tests the V1 basic auditor with a syntactically valid Python file."""
    commission_id = "test_audit_valid_001"
    valid_py_file = tmp_path / "valid_script.py"
    valid_py_file.write_text("print('Hello, World!')\n")

    code_input = CodeOutput(code_path=valid_py_file)
    audit_output = artisans.initialize_auditor_agent_v1(code_input, commission_id)

    assert isinstance(audit_output, AuditOutput)
    assert audit_output.status == AuditStatus.SUCCESS
    assert audit_output.message == "Syntax OK."
    assert audit_output.report_path is None


def test_initialize_auditor_agent_v1_invalid_syntax(tmp_path):
    """Tests the V1 basic auditor with a syntactically invalid Python file."""
    commission_id = "test_audit_invalid_002"
    invalid_py_file = tmp_path / "invalid_script.py"
    invalid_py_file.write_text("print 'Hello, World!'\n")  # Python 2 syntax

    code_input = CodeOutput(code_path=invalid_py_file)
    audit_output = artisans.initialize_auditor_agent_v1(code_input, commission_id)

    assert isinstance(audit_output, AuditOutput)
    assert audit_output.status == AuditStatus.FAILURE
    assert "Syntax error" in audit_output.message
    # Specific error messages can be brittle, so just check for the presence of "Syntax error"
    # Example: "Syntax error: Missing parentheses in call to 'print'. Did you mean print(...)? (<unknown>, line 1)"
    assert audit_output.report_path is None


def test_initialize_auditor_agent_v1_file_not_found(tmp_path):
    """Tests the V1 basic auditor when the code file does not exist."""
    commission_id = "test_audit_notfound_003"
    non_existent_file = tmp_path / "non_existent_script.py"

    code_input = CodeOutput(code_path=non_existent_file)
    audit_output = artisans.initialize_auditor_agent_v1(code_input, commission_id)

    assert isinstance(audit_output, AuditOutput)
    assert audit_output.status == AuditStatus.FAILURE
    assert f"Code file not found: {non_existent_file}" in audit_output.message
    assert audit_output.report_path is None


def test_initialize_auditor_agent_v1_path_is_directory(tmp_path):
    """Tests the V1 basic auditor when the code_path is a directory."""
    commission_id = "test_audit_isdir_004"
    dir_path = tmp_path / "some_directory"
    dir_path.mkdir()

    code_input = CodeOutput(code_path=dir_path)
    audit_output = artisans.initialize_auditor_agent_v1(code_input, commission_id)

    assert isinstance(audit_output, AuditOutput)
    assert audit_output.status == AuditStatus.FAILURE
    assert (
        f"Code file not found: {dir_path}" in audit_output.message
    )  # Current implementation treats dir as not found
    assert audit_output.report_path is None


def test_initialize_planner_agent_v1_generic_prompt():
    """Tests the V1 basic planner for a generic prompt."""
    prompt = "Develop a new feature for user authentication."
    commission_id = "test_generic_planner_002"

    plan_output = artisans.initialize_planner_agent_v1(prompt, commission_id)

    assert isinstance(plan_output, PlanOutput)
    assert plan_output.tasks == [f"Task 1: Implement feature based on: {prompt}"]
    assert plan_output.details is None


def test_initialize_planner_agent_v1_case_insensitivity_for_hello_world():
    """Tests that 'hello world' detection is case-insensitive."""
    prompt = "Can you make a HELLO WORLD script?"
    commission_id = "test_hw_case_planner_003"

    plan_output = artisans.initialize_planner_agent_v1(prompt, commission_id)

    assert isinstance(plan_output, PlanOutput)
    assert plan_output.tasks == ["Create a Python file that prints 'Hello, World!'"]
