from gandalf_workshop.artisan_guildhall import artisans
from gandalf_workshop.specs.data_models import PlanOutput  # Moved here


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
    from gandalf_workshop.specs.data_models import PMReviewDecision

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
    assert plan_output.details is None


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
