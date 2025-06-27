import os
from openai import OpenAI, AzureOpenAI
from pydantic import BaseModel, Field
from typing import Literal, Optional, Union
import instructor

# Load environment variables, e.g., from a .env file
# from dotenv import load_dotenv
# load_dotenv() # You might call this in your main CLI script or here if preferred

class LLMConfig(BaseModel):
    provider: Literal["openai", "azure", "anthropic", "google", "mistral", "together", "groq"] = Field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "openai"),
        description="The LLM provider to use."
    )
    model_name: str = Field(
        default_factory=lambda: os.getenv("LLM_MODEL_NAME", "gpt-4o"),
        description="The specific model name for the selected provider."
    )
    api_key: Optional[str] = Field(default=None, description="API key for the LLM provider. If None, will be sourced from provider-specific env vars.")
    azure_api_version: Optional[str] = Field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION"),
        description="Azure API version, required if provider is 'azure'."
    )
    azure_endpoint: Optional[str] = Field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT"),
        description="Azure endpoint, required if provider is 'azure'."
    )
    max_retries: int = Field(default=3, description="Maximum number of retries for LLM calls.")

    def get_api_key_for_provider(self) -> Optional[str]:
        """
        Gets the appropriate API key. Prioritizes explicitly passed `api_key` from initialization,
        then tries the provider-specific environment variable.
        """
        if self.api_key: # If api_key was provided directly to LLMConfig
            return self.api_key

        # If not provided directly, try the provider-specific environment variable
        if self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == "azure":
            return os.getenv("AZURE_OPENAI_API_KEY")
        elif self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        elif self.provider == "google":
            return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        elif self.provider == "mistral":
            return os.getenv("MISTRAL_API_KEY")
        elif self.provider == "together":
            return os.getenv("TOGETHER_AI_API_KEY")
        elif self.provider == "groq":
            return os.getenv("GROQ_API_KEY")
        return None # No specific key found

    def get_configured_client(self) -> Union[OpenAI, AzureOpenAI, None]:
        """
        Returns a configured LLM client based on the provider.
        Currently supports OpenAI and AzureOpenAI.
        The client is patched with `instructor` for structured output.
        """
        api_key = self.get_api_key_for_provider()
        if not api_key:
            print(f"Warning: API key for {self.provider} not found. LLM calls may fail.")
            # Depending on the provider, some might work without API keys (e.g. local models via OpenAI client)
            # For now, we proceed but issue a warning.

        if self.provider == "openai":
            client = OpenAI(api_key=api_key, max_retries=self.max_retries)
        elif self.provider == "azure":
            if not self.azure_endpoint or not self.azure_api_version:
                raise ValueError("Azure provider requires AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_VERSION.")
            client = AzureOpenAI(
                api_key=api_key,
                api_version=self.azure_api_version,
                azure_endpoint=self.azure_endpoint,
                max_retries=self.max_retries,
            )
        # Add other providers here as needed:
        # elif self.provider == "anthropic":
        #     from anthropic import Anthropic
        #     client = Anthropic(api_key=api_key)
        # elif self.provider == "google":
        #     # Requires google.generativeai
        #     # This would need a different client structure not directly compatible with instructor's OpenAI default
        #     print("Google provider via native SDK not yet fully integrated with instructor in this example.")
        #     return None # Or implement a compatible wrapper
        else:
            # Fallback for providers that might use an OpenAI-compatible API endpoint
            # E.g. Together, Mistral (some deployments), Groq
            # User might need to set OPENAI_API_BASE or similar for these.
            # For now, assume they are compatible with the OpenAI client if not explicitly handled.
            # This is a simplification; a more robust solution would use specific SDKs or a library like LiteLLM.
            print(f"Provider '{self.provider}' not explicitly supported, attempting to use OpenAI client. "
                  f"Ensure your environment is configured (e.g., OPENAI_API_BASE for compatible local/custom LLMs).")
            client = OpenAI(api_key=api_key, max_retries=self.max_retries)
            # For providers like Groq, Together, Mistral using their own SDKs,
            # you'd instantiate their clients here.
            # Example (conceptual, assuming `instructor` supports them similarly or via adapters):
            # if self.provider == "groq":
            #   from groq import Groq as GroqClient
            #   client = GroqClient(api_key=api_key, max_retries=self.max_retries)
            # elif self.provider == "mistral":
            #   from mistralai.client import MistralClient
            #   client = MistralClient(api_key=api_key)


        if client:
            # Patch the client with instructor
            # Mode can be instructor.Mode.FUNCTIONS, instructor.Mode.TOOLS, instructor.Mode.JSON, etc.
            # Default is FUNCTIONS for OpenAI
            return instructor.patch(client)

        raise ValueError(f"Unsupported LLM provider: {self.provider} or client could not be initialized.")

# Global config instance (optional, can be instantiated per request)
# Defaulting to environment variables or specified defaults.
# llm_config = LLMConfig()

if __name__ == "__main__":
    # Example of how to use it:
    print("Attempting to load default configuration (from environment or defaults):")

    # Test with default OpenAI (requires OPENAI_API_KEY to be set in env for actual calls)
    try:
        default_config = LLMConfig()
        print(f"Default Provider: {default_config.provider}")
        print(f"Default Model: {default_config.model_name}")
        print(f"Default API Key (masked): {'Set' if default_config.api_key else 'Not Set'}")
        print(f"Default Max Retries: {default_config.max_retries}")
        # client = default_config.get_configured_client()
        # print(f"Default client configured: {client is not None}")
    except Exception as e:
        print(f"Error with default config: {e}")

    print("\n--- Test Azure Configuration ---")
    # Simulate Azure environment variables for testing
    os.environ["LLM_PROVIDER"] = "azure"
    os.environ["LLM_MODEL_NAME"] = "gpt-35-turbo-instruct" # Example deployment name
    os.environ["AZURE_OPENAI_API_KEY"] = "test_azure_key"
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test-azure.openai.azure.com/"
    os.environ["AZURE_OPENAI_API_VERSION"] = "2023-07-01-preview"
    try:
        azure_config = LLMConfig()
        print(f"Azure Provider: {azure_config.provider}")
        print(f"Azure Model: {azure_config.model_name}")
        print(f"Azure API Key: {'Set' if azure_config.api_key else 'Not Set'}")
        print(f"Azure Endpoint: {azure_config.azure_endpoint}")
        print(f"Azure API Version: {azure_config.azure_api_version}")
        # azure_client = azure_config.get_configured_client()
        # print(f"Azure client configured: {azure_client is not None}")
    except ValueError as e:
        print(f"Error configuring Azure client: {e}")
    finally:
        # Clean up environment variables set for testing
        del os.environ["LLM_PROVIDER"]
        del os.environ["LLM_MODEL_NAME"]
        del os.environ["AZURE_OPENAI_API_KEY"]
        del os.environ["AZURE_OPENAI_ENDPOINT"]
        del os.environ["AZURE_OPENAI_API_VERSION"]

    print("\n--- Test Specific Provider API Key Retrieval ---")
    os.environ["MISTRAL_API_KEY"] = "test_mistral_key_env"
    mistral_config_test = LLMConfig(provider="mistral", model_name="mistral-large-latest")
    print(f"Mistral API Key: {mistral_config_test.get_api_key_for_provider()}")
    del os.environ["MISTRAL_API_KEY"]

    mistral_config_test_direct = LLMConfig(provider="mistral", model_name="mistral-large-latest", api_key="direct_mistral_key")
    print(f"Mistral API Key (direct): {mistral_config_test_direct.get_api_key_for_provider()}")

    print("\n--- Test Unset API Key Warning (OpenAI) ---")
    # Ensure OPENAI_API_KEY is not set for this test
    original_openai_key = os.environ.pop("OPENAI_API_KEY", None)
    try:
        openai_no_key_config = LLMConfig(provider="openai")
        print(f"OpenAI API Key (should be None): {openai_no_key_config.api_key}")
        # client_no_key = openai_no_key_config.get_configured_client() # This would print a warning
    except Exception as e:
        print(f"Error: {e}")
    if original_openai_key:
        os.environ["OPENAI_API_KEY"] = original_openai_key

    print("\nConfiguration script finished.")
