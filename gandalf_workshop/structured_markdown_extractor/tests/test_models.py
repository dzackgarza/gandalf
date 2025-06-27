import pytest
from pydantic import ValidationError
from datetime import datetime
import yaml

from gandalf_workshop.structured_markdown_extractor.models import (
    LogicalUnit, PaperSource, NotationExplanations, ThesisContent,
    ProofDevelopment, LineByLineProofStep, Audit, SuspicionScores,
    LogicalUnitsFile
)

# --- Fixtures for common model instances ---

@pytest.fixture
def minimal_paper_source_data():
    return {
        "file_path": "test.md",
        "start_line": 1,
        "end_line": 10,
        "verbatim_content": "This is a test."
    }

@pytest.fixture
def minimal_notation_explanations_data():
    return {
        "latex_macros": {"\\test": "\\mathcal{T}"},
        "mathematical_context": {"T": "A test variable"}
    }

@pytest.fixture
def minimal_thesis_content_data():
    return {
        "condensed_summary": "Summary.",
        "detailed_analysis": "Detailed analysis.",
        "expansion_notes": "Expansion notes."
    }

@pytest.fixture
def minimal_suspicion_scores_data():
    return {
        "source_fidelity": 1.0,
        "mathematical_accuracy": 1.0,
        "citation_validity": 1.0,
        "proof_correctness": 1.0,
        "formalization_readiness": 1.0,
        "expansion_quality": 1.0,
    }

@pytest.fixture
def minimal_audit_data(minimal_suspicion_scores_data):
    return {
        "audit_id": "audit_test_001",
        "auditor_role": "extractor",
        "audit_date": "2024-07-27T10:00:00Z", # Needs to be valid ISO datetime
        "suspicion_scores": minimal_suspicion_scores_data,
        "audit_notes": "Initial test audit."
    }

@pytest.fixture
def minimal_proof_step_data():
    return {
        "step": 1,
        "statement": "Statement of step 1.",
        "justification": "Justification for step 1.",
        "citations": ["Citation1"],
        "assumptions": "Assumptions for step 1."
    }

@pytest.fixture
def minimal_proof_development_data(minimal_proof_step_data):
    return {
        "paper_proof_content": "Paper proof.",
        "thesis_proof_outline": "Thesis outline.",
        "rigorous_proof": "Rigorous proof.",
        "line_by_line_proof": [minimal_proof_step_data],
        "proof_references": ["Ref1"]
    }

@pytest.fixture
def minimal_logical_unit_data(
    minimal_paper_source_data,
    minimal_notation_explanations_data,
    minimal_thesis_content_data,
    minimal_audit_data
):
    return {
        "unit_id": "test_unit_remark",
        "unit_type": "remark",
        "thesis_title": "Test Remark Unit",
        "dependencies": [],
        "paper_source": minimal_paper_source_data,
        "notation_explanations": minimal_notation_explanations_data,
        "thesis_content": minimal_thesis_content_data,
        "audits": [minimal_audit_data]
        # proof_development is optional for 'remark'
    }

@pytest.fixture
def logical_unit_data_theorem(minimal_logical_unit_data, minimal_proof_development_data):
    data = minimal_logical_unit_data.copy()
    data["unit_id"] = "test_unit_theorem"
    data["unit_type"] = "theorem"
    data["thesis_title"] = "Test Theorem Unit"
    data["proof_development"] = minimal_proof_development_data
    return data

# --- Basic Model Validation Tests ---

def test_paper_source_creation(minimal_paper_source_data):
    ps = PaperSource(**minimal_paper_source_data)
    assert ps.file_path == "test.md"
    assert ps.verbatim_content == "This is a test."

def test_notation_explanations_creation(minimal_notation_explanations_data):
    ne = NotationExplanations(**minimal_notation_explanations_data)
    assert ne.latex_macros["\\test"] == "\\mathcal{T}"

def test_thesis_content_creation(minimal_thesis_content_data):
    tc = ThesisContent(**minimal_thesis_content_data)
    assert tc.condensed_summary == "Summary."

def test_suspicion_scores_creation(minimal_suspicion_scores_data):
    ss = SuspicionScores(**minimal_suspicion_scores_data)
    assert ss.source_fidelity == 1.0

def test_audit_creation(minimal_audit_data): # Takes fixture as argument
    # Pydantic automatically converts valid ISO string to datetime
    audit = Audit(**minimal_audit_data) # Uses the fixture data
    assert audit.audit_id == "audit_test_001"
    assert isinstance(audit.audit_date, datetime)
    assert audit.audit_date.year == 2024

def test_line_by_line_proof_step_creation(minimal_proof_step_data):
    step = LineByLineProofStep(**minimal_proof_step_data)
    assert step.step == 1
    assert "Statement" in step.statement

def test_proof_development_creation(minimal_proof_development_data):
    pd = ProofDevelopment(**minimal_proof_development_data)
    assert pd.paper_proof_content == "Paper proof."
    assert len(pd.line_by_line_proof) == 1

# --- LogicalUnit Validation Tests ---

def test_logical_unit_remark_creation(minimal_logical_unit_data):
    lu = LogicalUnit(**minimal_logical_unit_data)
    assert lu.unit_id == "test_unit_remark"
    assert lu.unit_type == "remark"
    assert lu.proof_development is None

def test_logical_unit_theorem_creation(logical_unit_data_theorem):
    lu = LogicalUnit(**logical_unit_data_theorem)
    assert lu.unit_id == "test_unit_theorem"
    assert lu.unit_type == "theorem"
    assert lu.proof_development is not None
    assert lu.proof_development.rigorous_proof == "Rigorous proof."

def test_logical_unit_id_snake_case_valid(minimal_logical_unit_data): # Added fixture arg
    valid_ids = ["test_unit", "unit1", "another_complex_id_123"]
    for unit_id in valid_ids:
        data = minimal_logical_unit_data.copy() # Use copy of fixture data
        data["unit_id"] = unit_id
        try:
            LogicalUnit(**data)
        except ValidationError:
            pytest.fail(f"unit_id '{unit_id}' should be valid snake_case")

def test_logical_unit_id_snake_case_invalid(minimal_logical_unit_data): # Added fixture arg
    invalid_ids = ["TestUnit", "unit-1", "Unit 1", "test_unit!"]
    for unit_id in invalid_ids:
        data = minimal_logical_unit_data.copy() # Use copy of fixture data
        data["unit_id"] = unit_id
        with pytest.raises(ValidationError, match="unit_id must be in snake_case"):
            LogicalUnit(**data)

def test_proof_development_required_for_theorem(minimal_logical_unit_data): # Added fixture arg
    data = minimal_logical_unit_data.copy()
    data["unit_type"] = "theorem"
    data["unit_id"] = "theorem_no_proof"
    # proof_development is missing
    with pytest.raises(ValidationError, match="proof_development is required for unit_type 'theorem'"):
        LogicalUnit(**data)

def test_proof_development_not_strictly_required_for_remark(minimal_logical_unit_data, minimal_proof_development_data): # Added fixture args
    # Our current validator allows proof_development to be present for non-proof types,
    # even if not semantically "required". This test confirms it doesn't raise error if present.
    # If the rule was "MUST NOT be present", this test would change.
    data = minimal_logical_unit_data.copy() # Already a remark
    data["proof_development"] = minimal_proof_development_data # Use fixture data
    try:
        LogicalUnit(**data)
    except ValidationError as e:
        pytest.fail(f"proof_development, though not typical, should not cause validation error for remark if present: {e}")


def test_audits_min_length(minimal_logical_unit_data): # Added fixture arg
    data = minimal_logical_unit_data.copy()
    data["audits"] = [] # Empty list
    with pytest.raises(ValidationError, match="List should have at least 1 item after validation"):
        LogicalUnit(**data)


# --- LogicalUnitsFile (RootModel) Tests ---

def test_logical_units_file_creation(minimal_logical_unit_data, logical_unit_data_theorem):
    lusf = LogicalUnitsFile.model_validate([minimal_logical_unit_data, logical_unit_data_theorem])
    assert len(lusf.root) == 2
    assert lusf[0].unit_id == "test_unit_remark"
    assert lusf[1].unit_id == "test_unit_theorem"

def test_logical_units_file_iteration(minimal_logical_unit_data):
    lusf = LogicalUnitsFile.model_validate([minimal_logical_unit_data])
    count = 0
    for unit in lusf:
        assert unit.unit_id == "test_unit_remark"
        count += 1
    assert count == 1

def test_logical_units_file_yaml_parsing_valid(minimal_logical_unit_data):
    # Construct the Python object that model_validate_yaml expects in string form
    data_for_yaml = {"logical_units": [minimal_logical_unit_data]}
    yaml_str = yaml.dump(data_for_yaml, sort_keys=False, allow_unicode=True)

    lusf = LogicalUnitsFile.model_validate_yaml(yaml_str)
    assert len(lusf.root) == 1
    assert lusf[0].unit_id == "test_unit_remark"
    assert lusf[0].paper_source.file_path == "test.md" # Check nested parsing

def test_logical_units_file_yaml_parsing_invalid_structure():
    invalid_yaml_str = """
invalid_top_key:
  - unit_id: "test"
    # ... rest of fields
"""
    with pytest.raises(ValueError, match="YAML must have a top-level 'logical_units' key"):
        LogicalUnitsFile.model_validate_yaml(invalid_yaml_str)

def test_logical_units_file_yaml_parsing_validation_error(minimal_logical_unit_data):
    # Create YAML with an invalid field (e.g. unit_id not snake_case)
    bad_data = minimal_logical_unit_data.copy()
    bad_data["unit_id"] = "Invalid ID"
    yaml_str = f"""
logical_units:
  - {yaml.dump(bad_data, sort_keys=False)}
"""
    with pytest.raises(ValidationError): # Pydantic's ValidationError
        LogicalUnitsFile.model_validate_yaml(yaml_str)


def test_logical_units_file_yaml_dumping(minimal_logical_unit_data):
    lusf = LogicalUnitsFile.model_validate([minimal_logical_unit_data])
    yaml_output = lusf.model_dump_yaml()

    # Basic check that it's valid YAML and contains key elements
    assert "logical_units:" in yaml_output
    assert "unit_id: test_unit_remark" in yaml_output
    assert "auditor_role: extractor" in yaml_output # Check datetime serialization

    # Try to load it back
    loaded_data = yaml.safe_load(yaml_output)
    assert loaded_data["logical_units"][0]["unit_id"] == "test_unit_remark"
    # When mode='python' is used in model_dump, datetime objects remain datetime objects.
    # PyYAML then serializes them. When loaded back by PyYAML, they become datetime objects again.
    assert isinstance(loaded_data["logical_units"][0]["audits"][0]["audit_date"], datetime)

    # Validate the dumped YAML back into the model
    try:
        LogicalUnitsFile.model_validate_yaml(yaml_output)
    except Exception as e:
        pytest.fail(f"Dumped YAML could not be re-validated: {e}\nYAML:\n{yaml_output}")

def test_datetime_serialization_in_dump(minimal_audit_data, minimal_logical_unit_data): # Added fixture
    audit_obj = Audit(**minimal_audit_data)
    dumped_audit_python_mode = audit_obj.model_dump(mode='python')
    # In 'python' mode, datetime objects remain datetime objects
    assert isinstance(dumped_audit_python_mode['audit_date'], datetime)
    assert dumped_audit_python_mode['audit_date'].isoformat().startswith("2024-07-27T10:00:00")

    # Test how it appears in the final YAML from LogicalUnitsFile.model_dump_yaml()
    lu_data_with_specific_audit = minimal_logical_unit_data.copy() # Use fixture
    lu_data_with_specific_audit["audits"] = [minimal_audit_data]

    lusf = LogicalUnitsFile.model_validate([lu_data_with_specific_audit])
    yaml_output = lusf.model_dump_yaml() # This uses mode='python' then yaml.dump

    # PyYAML's default string representation for datetime might vary slightly (e.g., space vs T)
    # but it should be a valid ISO-like format that can be parsed back.
    # Let's load and check the type and value.
    reloaded_data = yaml.safe_load(yaml_output)
    reloaded_audit_date = reloaded_data["logical_units"][0]["audits"][0]["audit_date"]
    assert isinstance(reloaded_audit_date, datetime)
    assert reloaded_audit_date == audit_obj.audit_date # Compare datetime objects

if __name__ == '__main__':
    pytest.main()
