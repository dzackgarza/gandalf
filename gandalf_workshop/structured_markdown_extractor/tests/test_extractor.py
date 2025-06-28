import pytest
from unittest.mock import patch, MagicMock
from typing import List, Optional

from gandalf_workshop.structured_markdown_extractor.extractor import MarkdownExtractor
from gandalf_workshop.structured_markdown_extractor.config import LLMConfig
from gandalf_workshop.structured_markdown_extractor.models import LogicalUnitsFile, LogicalUnit, PaperSource, NotationExplanations, ThesisContent, Audit, SuspicionScores
from gandalf_workshop.structured_markdown_extractor.prompts import get_system_prompt, get_user_prompt # For verifying calls

@pytest.fixture
def mock_llm_config_for_extractor():
    return LLMConfig(provider="openai", model_name="gpt-test", api_key="fake_key", max_retries=1)

@pytest.fixture
def sample_markdown_content():
    return """
# Test Title
Some introductory text.

## Section 1: Definition
A test definition.
"""

@pytest.fixture
def mock_successful_llm_response():
    # Create a mock LogicalUnitsFile response
    unit = LogicalUnit(
        unit_id="test_def",
        unit_type="definition",
        thesis_title="Test Definition",
        dependencies=[],
        paper_source=PaperSource(
            file_path="test.md",
            start_line=4,
            end_line=5,
            verbatim_content="A test definition."
        ),
        notation_explanations=NotationExplanations(
            latex_macros={},
            mathematical_context={}
        ),
        thesis_content=ThesisContent(
            condensed_summary="A summary.",
            detailed_analysis="A detailed analysis.",
            expansion_notes="Needs expansion."
        ),
        audits=[Audit(
            audit_id="audit1",
            auditor_role="extractor",
            audit_date="2024-01-01T00:00:00Z",
            suspicion_scores=SuspicionScores(
                source_fidelity=1.0, mathematical_accuracy=1.0, citation_validity=1.0,
                proof_correctness=1.0, formalization_readiness=1.0, expansion_quality=1.0
            ),
            audit_notes="Initial."
        )]
    )
    return LogicalUnitsFile(root=[unit])

@pytest.fixture
def mock_successful_extraction_result(mock_successful_llm_response): # Depends on the LogicalUnitsFile fixture
    # This fixture will provide an ExtractionResult model instance
    # The mock_successful_llm_response provides a LogicalUnitsFile, so we take its root
    return ExtractionResult(logical_units=mock_successful_llm_response.root)


# --- Test successful extraction ---
@patch('gandalf_workshop.structured_markdown_extractor.extractor.call_llm_with_structured_output')
def test_extract_logical_units_successful(
    mock_call_llm,
    mock_llm_config_for_extractor,
    sample_markdown_content,
    mock_successful_extraction_result # Changed fixture
):
    mock_call_llm.return_value = mock_successful_extraction_result # Changed return value

    extractor = MarkdownExtractor(config=mock_llm_config_for_extractor)
    source_filename = "test.md"

    result = extractor.extract_logical_units_from_file_content( # Renamed
        file_content=sample_markdown_content, # Renamed
        source_filename=source_filename
    )

    mock_call_llm.assert_called_once_with(
        config=mock_llm_config_for_extractor,
        response_model=ExtractionResult, # Changed to ExtractionResult
        system_prompt=get_system_prompt(),
        user_prompt=get_user_prompt(sample_markdown_content, source_filename),
        max_retries=None # Default from extract_logical_units_from_markdown
    )

    assert result is not None
    assert isinstance(result, LogicalUnitsFile)
    assert len(result.root) == 1
    assert result.root[0].unit_id == "test_def"

# --- Test LLM call failure ---
@patch('gandalf_workshop.structured_markdown_extractor.extractor.call_llm_with_structured_output')
def test_extract_logical_units_llm_failure(
    mock_call_llm,
    mock_llm_config_for_extractor,
    sample_markdown_content
):
    mock_call_llm.return_value = None # Simulate LLM failure after retries

    extractor = MarkdownExtractor(config=mock_llm_config_for_extractor)
    source_filename = "test_failure.md"

    result = extractor.extract_logical_units_from_file_content( # Renamed
        file_content=sample_markdown_content, # Renamed
        source_filename=source_filename
    )

    mock_call_llm.assert_called_once()
    assert result is None

# --- Test empty markdown content ---
@patch('gandalf_workshop.structured_markdown_extractor.extractor.call_llm_with_structured_output')
def test_extract_logical_units_empty_markdown(mock_call_llm, mock_llm_config_for_extractor):
    extractor = MarkdownExtractor(config=mock_llm_config_for_extractor)
    result = extractor.extract_logical_units_from_file_content( # Renamed
        file_content="", # Empty content, Renamed
        source_filename="empty.md"
    )

    mock_call_llm.assert_not_called() # Should not call LLM for empty content
    assert isinstance(result, LogicalUnitsFile)
    assert len(result.root) == 0

# --- Test max_llm_retries override ---
@patch('gandalf_workshop.structured_markdown_extractor.extractor.call_llm_with_structured_output')
def test_extract_logical_units_max_retries_override(
    mock_call_llm,
    mock_llm_config_for_extractor,
    sample_markdown_content,
    mock_successful_llm_response
):
    mock_call_llm.return_value = mock_successful_llm_response

    extractor = MarkdownExtractor(config=mock_llm_config_for_extractor)
    source_filename = "test_retry_override.md"
    custom_max_retries = 3

    extractor.extract_logical_units_from_file_content( # Renamed
        file_content=sample_markdown_content, # Renamed
        source_filename=source_filename,
        max_llm_retries=custom_max_retries
    )

    mock_call_llm.assert_called_once_with(
        config=mock_llm_config_for_extractor,
        response_model=ExtractionResult, # Changed to ExtractionResult
        system_prompt=get_system_prompt(),
        user_prompt=get_user_prompt(sample_markdown_content, source_filename),
        max_retries=custom_max_retries
    )


# --- Test YAML serialization ---
def test_units_to_yaml(mock_llm_config_for_extractor, mock_successful_llm_response):
    extractor = MarkdownExtractor(config=mock_llm_config_for_extractor)
    yaml_output = extractor.units_to_yaml(mock_successful_llm_response)

    assert "logical_units:" in yaml_output
    assert "unit_id: test_def" in yaml_output
    assert "file_path: test.md" in yaml_output # From mock_successful_llm_response

    # Try to load it back to verify it's valid YAML (basic check)
    import yaml
    try:
        loaded_data = yaml.safe_load(yaml_output)
        assert isinstance(loaded_data, dict)
        assert "logical_units" in loaded_data
        assert len(loaded_data["logical_units"]) == 1
        assert loaded_data["logical_units"][0]["unit_id"] == "test_def"
    except yaml.YAMLError as e:
        pytest.fail(f"Generated YAML is invalid: {e}\nYAML:\n{yaml_output}")

# --- Tests for TeX input ---

@pytest.fixture
def sample_tex_file_content():
    return r"\documentclass{article}\begin{document}Hello \TeX\ world. $E=mc^2$.\end{document}"

@patch('gandalf_workshop.structured_markdown_extractor.extractor.convert_tex_to_markdown')
@patch('gandalf_workshop.structured_markdown_extractor.extractor.call_llm_with_structured_output')
def test_extract_from_tex_file_conversion_success(
    mock_call_llm,
    mock_convert_tex,
    mock_llm_config_for_extractor,
    sample_tex_file_content,
    mock_successful_extraction_result # Changed fixture
):
    converted_markdown = "Hello TeX world. $E=mc^2$."
    mock_convert_tex.return_value = converted_markdown
    mock_call_llm.return_value = mock_successful_extraction_result # Changed return value

    extractor = MarkdownExtractor(config=mock_llm_config_for_extractor)
    source_filename = "sample.tex"

    result = extractor.extract_logical_units_from_file_content(
        file_content=sample_tex_file_content,
        source_filename=source_filename
    )

    mock_convert_tex.assert_called_once_with(sample_tex_file_content)
    mock_call_llm.assert_called_once_with(
        config=mock_llm_config_for_extractor,
        response_model=ExtractionResult, # Extractor uses ExtractionResult internally now
        system_prompt=get_system_prompt(),
        user_prompt=get_user_prompt(converted_markdown, source_filename), # LLM gets converted content
        max_retries=None
    )
    assert result is not None
    assert len(result.root) == 1
    assert result.root[0].unit_id == "test_def" # From mock_successful_llm_response

@patch('gandalf_workshop.structured_markdown_extractor.extractor.convert_tex_to_markdown')
@patch('gandalf_workshop.structured_markdown_extractor.extractor.call_llm_with_structured_output')
def test_extract_from_tex_file_conversion_failure(
    mock_call_llm,
    mock_convert_tex,
    mock_llm_config_for_extractor,
    sample_tex_file_content
):
    mock_convert_tex.return_value = None # Simulate conversion failure

    extractor = MarkdownExtractor(config=mock_llm_config_for_extractor)
    source_filename = "sample_fail.tex"

    result = extractor.extract_logical_units_from_file_content(
        file_content=sample_tex_file_content,
        source_filename=source_filename
    )

    mock_convert_tex.assert_called_once_with(sample_tex_file_content)
    mock_call_llm.assert_not_called() # LLM should not be called if conversion fails
    assert result is None


if __name__ == '__main__':
    pytest.main()
