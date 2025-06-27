import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pydantic import ValidationError, BaseModel as PydanticBaseModel

from gandalf_workshop.structured_markdown_extractor.llm_utils import call_llm_with_structured_output
from gandalf_workshop.structured_markdown_extractor.config import LLMConfig
from gandalf_workshop.structured_markdown_extractor.models import LogicalUnit # Any Pydantic model for testing
from pydantic import BaseModel as PydanticBaseModel # Changed import

# A simple Pydantic model for testing responses
class SimpleResponse(PydanticBaseModel): # Changed from instructor.BaseModel
    name: str
    value: int

@pytest.fixture
def mock_llm_config():
    config = LLMConfig(
        provider="openai",
        model_name="gpt-test",
        api_key="fake_api_key",
        max_retries=2 # Default for tests, can be overridden
    )
    return config

# --- Test successful LLM call ---
def test_call_llm_successful_first_try(mock_llm_config):
    # mock_client will be the one returned by get_configured_client, already patched by instructor
    mock_client = MagicMock()
    # We need to mock the 'create' method on the 'completions' attribute of 'chat'
    mock_client.chat.completions.create.return_value = SimpleResponse(name="test", value=123)

    with patch(
        'gandalf_workshop.structured_markdown_extractor.config.LLMConfig.get_configured_client',
        return_value=mock_client # This mock_client already has chat.completions.create mocked
    ) as mock_get_client:
        response = call_llm_with_structured_output(
            config=mock_llm_config,
            response_model=SimpleResponse,
            system_prompt="System prompt",
            user_prompt="User prompt"
        )

    mock_get_client.assert_called_once()
    mock_client.chat.completions.create.assert_called_once_with( # Changed here
        model="gpt-test",
        response_model=SimpleResponse,
        messages=[
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User prompt"},
        ],
        temperature=0.1
    )
    assert isinstance(response, SimpleResponse)
    assert response.name == "test"
    assert response.value == 123

# --- Test retry on Pydantic ValidationError ---
def test_call_llm_retry_on_validation_error(mock_llm_config):
    mock_client = MagicMock()

    # Simulate ValidationError on first call, success on second
    mock_client.chat.completions.create.side_effect = [
        ValidationError.from_exception_data(title="SimpleResponse", line_errors=[{'type': 'missing', 'loc': ('value',), 'input': {'name': 'test'}, 'msg': 'Field required'}]),
        SimpleResponse(name="test_retry", value=456)
    ]

    with patch(
        'gandalf_workshop.structured_markdown_extractor.config.LLMConfig.get_configured_client',
        return_value=mock_client
    ):
        response = call_llm_with_structured_output(
            config=mock_llm_config, # max_retries = 2
            response_model=SimpleResponse,
            system_prompt="System prompt",
            user_prompt="User prompt"
        )

    assert mock_client.chat.completions.create.call_count == 2 # Changed here
    # Check that the second call includes error context (simplified check)
    second_call_args = mock_client.chat.completions.create.call_args_list[1] # Changed here
    user_message_content_second_call = second_call_args[1]['messages'][1]['content']
    assert "There was a validation error in the previous attempt" in user_message_content_second_call
    assert "Original User Prompt:\nUser prompt" in user_message_content_second_call

    assert isinstance(response, SimpleResponse)
    assert response.name == "test_retry"
    assert response.value == 456

# --- Test exhaustion of retries on Pydantic ValidationError ---
def test_call_llm_exhaust_retries_on_validation_error(mock_llm_config):
    mock_client = MagicMock()

    # Simulate persistent ValidationError
    validation_error = ValidationError.from_exception_data(title="SimpleResponse", line_errors=[{'type': 'missing', 'loc': ('value',), 'input': {'name': 'test'}, 'msg': 'Field required'}])
    mock_client.chat.completions.create.side_effect = [validation_error] * (mock_llm_config.max_retries + 1)

    with patch(
        'gandalf_workshop.structured_markdown_extractor.config.LLMConfig.get_configured_client',
        return_value=mock_client
    ):
        response = call_llm_with_structured_output(
            config=mock_llm_config,
            response_model=SimpleResponse,
            system_prompt="System prompt",
            user_prompt="User prompt"
        )

    assert mock_client.chat.completions.create.call_count == mock_llm_config.max_retries + 1 # Changed here
    assert response is None

# --- Test retry on generic Exception ---
def test_call_llm_retry_on_generic_exception(mock_llm_config):
    mock_client = MagicMock()

    # Simulate generic Exception on first call, success on second
    mock_client.chat.completions.create.side_effect = [
        Exception("API connection error"),
        SimpleResponse(name="test_exception_retry", value=789)
    ]

    with patch(
        'gandalf_workshop.structured_markdown_extractor.config.LLMConfig.get_configured_client',
        return_value=mock_client
    ):
        response = call_llm_with_structured_output(
            config=mock_llm_config,
            response_model=SimpleResponse,
            system_prompt="System prompt",
            user_prompt="User prompt"
        )

    assert mock_client.chat.completions.create.call_count == 2 # Changed here
    # Check that the second call includes error context
    second_call_args = mock_client.chat.completions.create.call_args_list[1] # Changed here
    user_message_content_second_call = second_call_args[1]['messages'][1]['content']
    assert "An unexpected error occurred in the previous attempt: API connection error" in user_message_content_second_call

    assert isinstance(response, SimpleResponse)
    assert response.name == "test_exception_retry"
    assert response.value == 789

# --- Test exhaustion of retries on generic Exception ---
def test_call_llm_exhaust_retries_on_generic_exception(mock_llm_config):
    mock_client = MagicMock()

    # Simulate persistent generic Exception
    generic_exception = Exception("Persistent API error")
    mock_client.chat.completions.create.side_effect = [generic_exception] * (mock_llm_config.max_retries + 1)

    with patch(
        'gandalf_workshop.structured_markdown_extractor.config.LLMConfig.get_configured_client',
        return_value=mock_client
    ):
        response = call_llm_with_structured_output(
            config=mock_llm_config,
            response_model=SimpleResponse,
            system_prompt="System prompt",
            user_prompt="User prompt"
        )

    assert mock_client.chat.completions.create.call_count == mock_llm_config.max_retries + 1 # Changed here
    assert response is None

# --- Test client initialization failure ---
def test_call_llm_client_initialization_failure(mock_llm_config):
    with patch(
        'gandalf_workshop.structured_markdown_extractor.config.LLMConfig.get_configured_client',
        side_effect=ValueError("Client init failed")
    ) as mock_get_client:
        response = call_llm_with_structured_output(
            config=mock_llm_config,
            response_model=SimpleResponse,
            system_prompt="System prompt",
            user_prompt="User prompt"
        )

    mock_get_client.assert_called_once()
    assert response is None

# --- Test max_retries override ---
def test_call_llm_max_retries_override(mock_llm_config):
    # mock_llm_config.max_retries is 2. We override to 1.
    # Expect 1 initial call + 1 retry = 2 calls total if errors persist.

    mock_client = MagicMock()

    validation_error = ValidationError.from_exception_data(title="SimpleResponse", line_errors=[{'type': 'missing', 'loc': ('value',), 'input': {'name': 'test'}, 'msg': 'Field required'}])
    mock_client.chat.completions.create.side_effect = [validation_error] * 2 # Should fail after 2 calls (1 initial + 1 retry)

    with patch(
        'gandalf_workshop.structured_markdown_extractor.config.LLMConfig.get_configured_client',
        return_value=mock_client
    ):
        response = call_llm_with_structured_output(
            config=mock_llm_config,
            response_model=SimpleResponse,
            system_prompt="System prompt",
            user_prompt="User prompt",
            max_retries=1 # Override
        )

    assert mock_client.chat.completions.create.call_count == 1 + 1 # Changed here
    assert response is None


if __name__ == '__main__':
    pytest.main()
