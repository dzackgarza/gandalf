import pytest
from pathlib import Path
from pydantic import ValidationError

from gandalf_workshop.specs.data_models import (
    PlanOutput,
    CodeOutput,
    AuditOutput,
    AuditStatus,
)


def test_plan_output_valid():
    """Test valid PlanOutput instantiation."""
    plan = PlanOutput(tasks=["task1", "task2"], details={"key": "value"})
    assert plan.tasks == ["task1", "task2"]
    assert plan.details == {"key": "value"}

    plan_no_details = PlanOutput(tasks=["task1"])
    assert plan_no_details.tasks == ["task1"]
    assert plan_no_details.details is None


def test_plan_output_invalid():
    """Test invalid PlanOutput instantiation (e.g., missing tasks)."""
    with pytest.raises(ValidationError):
        PlanOutput(details={"key": "value"})  # tasks is required

    with pytest.raises(ValidationError):
        PlanOutput(tasks="not a list")  # tasks must be a list


def test_code_output_valid():
    """Test valid CodeOutput instantiation."""
    path = Path("/tmp/code.py")
    code_out = CodeOutput(code_path=path, message="Code generated.")
    assert code_out.code_path == path
    assert code_out.message == "Code generated."

    code_out_no_message = CodeOutput(code_path=path)
    assert code_out_no_message.code_path == path
    assert code_out_no_message.message is None


def test_code_output_invalid():
    """Test invalid CodeOutput instantiation (e.g., missing code_path)."""
    with pytest.raises(ValidationError):
        CodeOutput(message="Generated")  # code_path is required

    with pytest.raises(ValidationError):
        CodeOutput(code_path=123)  # code_path must be Path-like


def test_audit_output_valid():
    """Test valid AuditOutput instantiation."""
    report_path = Path("/tmp/audit.txt")
    audit_out_success = AuditOutput(
        status=AuditStatus.SUCCESS,
        message="All checks passed.",
        report_path=report_path,
    )
    assert audit_out_success.status == AuditStatus.SUCCESS
    assert audit_out_success.message == "All checks passed."
    assert audit_out_success.report_path == report_path

    audit_out_failure_no_report = AuditOutput(
        status=AuditStatus.FAILURE, message="Syntax error found."
    )
    assert audit_out_failure_no_report.status == AuditStatus.FAILURE
    assert audit_out_failure_no_report.message == "Syntax error found."
    assert audit_out_failure_no_report.report_path is None


def test_audit_output_invalid():
    """Test invalid AuditOutput instantiation (e.g., missing status)."""
    with pytest.raises(ValidationError):
        AuditOutput(message="Checks done")  # status is required

    with pytest.raises(ValidationError):
        AuditOutput(status="PASSED_WITH_WARNINGS")  # status must be AuditStatus enum

    with pytest.raises(ValidationError):
        AuditOutput(
            status=AuditStatus.SUCCESS, report_path=123
        )  # report_path must be Path-like


def test_audit_status_enum():
    """Test AuditStatus enum values."""
    assert AuditStatus.SUCCESS == "SUCCESS"
    assert AuditStatus.FAILURE == "FAILURE"
    # Check that it's a string enum
    assert isinstance(AuditStatus.SUCCESS.value, str)


# Example of how to run these tests with pytest:
# Ensure you are in the root directory of the project.
# Run: pytest gandalf_workshop/tests/test_data_models.py
