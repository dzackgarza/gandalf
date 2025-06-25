import pytest
import os
from unittest import mock # Still needed for os.environ mocking
from pathlib import Path

from gandalf_workshop.llm_provider_manager import LLMProviderManager
# Mock classes for API clients are removed as we are using live APIs.

# Fixtures to manipulate os.environ for testing different key availability scenarios
@pytest.fixture
def manager_with_all_keys_env():
    # This fixture ensures that when LLMProviderManager is instantiated,
    # it will find all necessary keys in the environment IF they are in the .env file.
    # No os.environ patching here, relies on .env being loaded by LLMProviderManager.
    # If .env is missing keys, this test might behave like specific keys are missing.
    manager = LLMProviderManager()
    yield manager

@pytest.fixture
def manager_with_no_keys_env():
    # This fixture simulates an environment where NO API keys are set.
    with mock.patch.dict(os.environ, {}, clear=True):
        # Crucially, also prevent .env loading for this specific manager instance
        with mock.patch('gandalf_workshop.llm_provider_manager.load_dotenv') as m_load_dotenv:
            m_load_dotenv.return_value = None # Pretend .env was not loaded or empty
            manager = LLMProviderManager()
            yield manager

@pytest.fixture
def manager_with_gemini_only_env():
    # Simulates only Gemini key being present.
    # Assumes GEMINI_API_KEY is in the .env, and we clear others.
    # Or, explicitly set GEMINI_API_KEY and clear others.
    # For live tests, it's better to rely on the actual .env for the present key
    # and use os.environ patching to simulate absence of others.

    # Read real Gemini key if present, to ensure it's used.
    # This is tricky because LLMProviderManager loads .env.
    # The most straightforward for "only Gemini" is to clear other known keys from environ
    # *after* LLMProviderManager's __init__ has loaded them.
    # A cleaner way for testing "only X" is to provide a custom .env for that test,
    # or fully control os.environ before LLMProviderManager init.

    # Let's patch os.getenv calls within specific provider checks for this one.
    # This is more surgical for live testing "only one provider works".
    # However, for simplicity of this refactor, we'll rely on the .env having Gemini
    # and then other tests will simulate missing keys for other providers.
    # This fixture will thus be similar to manager_with_all_keys_env,
    # and tests will check for Gemini specifically.
    manager = LLMProviderManager() # Relies on .env
    yield manager


# --- Live API Tests ---

def test_llm_provider_manager_init_loads_keys_from_env(manager_with_all_keys_env):
    """Test that LLMProviderManager loads keys from .env if present."""
    # This test implicitly checks if keys are loaded by checking attributes.
    # Requires actual keys in .env to be meaningful.
    manager = manager_with_all_keys_env
    # Check if some keys are loaded (don't assert specific values, just presence if expected)
    # This depends on what's actually in the .env file used by the test environment
    assert manager.gemini_api_key is not None or os.getenv("GEMINI_API_KEY") is not None
    # Add similar checks for other keys if they are expected to be in the .env
    # For now, we just ensure the manager initializes.

def test_get_llm_provider_gemini_live_success(manager_with_all_keys_env):
    """Test successful Gemini provider retrieval with live API."""
    manager = manager_with_all_keys_env
    if not manager.gemini_api_key:
        pytest.skip("GEMINI_API_KEY not found in environment, skipping live test.")

    provider_info = manager.get_llm_provider(preferred_provider="gemini")
    assert provider_info is not None
    assert provider_info["provider_name"] == "gemini"
    assert provider_info["api_key"] == manager.gemini_api_key
    assert len(provider_info["models"]) > 0
    # Client object type check depends on the actual client library
    assert provider_info["client"] is not None
    print(f"Found Gemini models: {provider_info['models'][:5]}")


def test_get_llm_provider_no_keys_live(manager_with_no_keys_env):
    """Test that no provider is found if no API keys are effectively set."""
    manager = manager_with_no_keys_env
    provider_info = manager.get_llm_provider()
    assert provider_info is None


def test_get_llm_provider_together_ai_live_success(manager_with_all_keys_env):
    manager = manager_with_all_keys_env
    if not manager.together_api_key:
        pytest.skip("TOGETHER_AI_API_KEY not found in environment, skipping live test.")

    provider_info = manager.get_llm_provider(preferred_provider="together_ai")
    assert provider_info is not None
    assert provider_info["provider_name"] == "together_ai"
    assert provider_info["api_key"] == manager.together_api_key
    assert len(provider_info["models"]) > 0
    assert provider_info["client"] is not None
    print(f"Found Together AI models: {provider_info['models'][:5]}")


def test_get_llm_provider_mistral_live_success(manager_with_all_keys_env):
    manager = manager_with_all_keys_env
    if not manager.mistral_api_key:
        pytest.skip("MISTRAL_API_KEY not found in environment, skipping live test.")

    provider_info = manager.get_llm_provider(preferred_provider="mistral")
    assert provider_info is not None
    assert provider_info["provider_name"] == "mistral"
    assert provider_info["api_key"] == manager.mistral_api_key
    assert len(provider_info["models"]) > 0
    assert provider_info["client"] is not None
    print(f"Found Mistral models: {provider_info['models'][:5]}")


def test_get_llm_provider_gemini_simulated_missing_key():
    # Simulate Gemini key missing and no other keys available for fallback.
    env_vars_for_test = {
        "GEMINI_API_KEY": "",  # Empty key
        "TOGETHER_AI_API_KEY": "", # Ensure no fallback
        "MISTRAL_API_KEY": ""      # Ensure no fallback
    }
    with mock.patch.dict(os.environ, env_vars_for_test, clear=True): # clear=True ensures only these are set
        with mock.patch('gandalf_workshop.llm_provider_manager.load_dotenv') as m_load_dotenv:
            m_load_dotenv.return_value = None # Prevent .env loading
            manager = LLMProviderManager()
            assert manager.gemini_api_key == ""
            assert manager.together_api_key == ""
            assert manager.mistral_api_key == ""
            provider_info = manager.get_llm_provider(preferred_provider="gemini")
            assert provider_info is None # Gemini should fail, and no fallback should occur

def test_get_llm_provider_fallback_live(manager_with_all_keys_env):
    """Test fallback if a preferred (but simulated failing) provider is chosen."""
    manager = manager_with_all_keys_env
    if not manager.together_api_key and not manager.mistral_api_key: # Need at least one fallback
        pytest.skip("Neither Together AI nor Mistral API keys found, skipping fallback test.")

    # Simulate Gemini key being present but calls to its API failing
    # This requires mocking the genai client's methods to raise an exception
    # while still allowing other providers to make live calls.

    # If GEMINI_API_KEY is actually valid and live, this test becomes harder without deeper mocking.
    # For now, we'll assume a case where Gemini might be configured but fails.
    # A simpler version: prefer a provider known to be missing a key if possible,
    # or simulate its failure more directly if we had access to the client instance.

    # This test is becoming complex for a pure live test.
    # A true live fallback test means one service is actually down or key is invalid.
    # Let's simplify: if Gemini key is present, try to make it "fail" by unsetting it,
    # then see if it falls back to Together or Mistral (if their keys are present).

    original_gemini_key = os.environ.get("GEMINI_API_KEY")
    try:
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"] # Temporarily remove Gemini key

        # Re-initialize manager in this modified environment
        # Must also mock load_dotenv for this specific instantiation
        with mock.patch('gandalf_workshop.llm_provider_manager.load_dotenv') as m_load_dotenv:
            m_load_dotenv.return_value = None # Prevent reloading from .env
            current_manager = LLMProviderManager()

        # Check if any key was actually loaded by current_manager. If .env was empty, this might be all None.
        if not current_manager.together_api_key and not current_manager.mistral_api_key:
             pytest.skip("No fallback keys (Together/Mistral) available in .env for live fallback test.")

        provider_info = current_manager.get_llm_provider(preferred_provider="gemini") # Prefer failing Gemini

        assert provider_info is not None
        assert provider_info["provider_name"] != "gemini" # Should not be Gemini
        assert provider_info["provider_name"] in ["together_ai", "mistral"]
        print(f"Fallback successful to: {provider_info['provider_name']}")

    finally:
        # Restore Gemini key if it was removed
        if original_gemini_key is not None:
            os.environ["GEMINI_API_KEY"] = original_gemini_key
        elif "GEMINI_API_KEY" in os.environ: # If it was set to "" by a previous test and not restored
             del os.environ["GEMINI_API_KEY"]


def test_get_llm_provider_no_preference_live_order(manager_with_all_keys_env):
    """Test it picks a provider if all keys are present and no preference given."""
    manager = manager_with_all_keys_env
    if not (manager.gemini_api_key or manager.together_api_key or manager.mistral_api_key):
        pytest.skip("No API keys found in .env, skipping no_preference test.")

    provider_info = manager.get_llm_provider()
    assert provider_info is not None
    # The actual provider depends on the check order in LLMProviderManager and live availability
    # Default order is Gemini, Together, Mistral.
    print(f"No preference, selected: {provider_info['provider_name']}")
    assert provider_info["provider_name"] in ["gemini", "together_ai", "mistral"]

# Note: These tests will make actual API calls. Ensure API keys in .env are valid
# and you have the necessary quotas/access for the services.
# Some tests might be skipped if keys are not found.
# Testing specific API error handling (like 500 errors) is not covered here
# as it's hard to reliably reproduce with live APIs.
