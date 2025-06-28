# Placeholder for actual LLM client libraries
# from langchain_community.llms import Gemini, Anthropic # Example, adjust as per actual LangChain model
# For direct SDK usage:
# import google.generativeai as genai
# import anthropic
import os # Added for __main__ block
import yaml # Added for __main__ block

from .config_manager import ConfigManager

class LLMManager:
    def __init__(self, config_manager: ConfigManager):
        """
        Manages LLM providers and clients.

        Args:
            config_manager (ConfigManager): An instance of ConfigManager for accessing settings and API keys.
        """
        if not isinstance(config_manager, ConfigManager):
            raise TypeError("config_manager must be an instance of ConfigManager")
        self.config_manager = config_manager
        self.current_provider_name = self.config_manager.get_setting("default_llm_provider", "gemini")
        self.llm_client = None # Will hold the initialized client

        # Initialize the client for the default provider
        # self.get_llm_client() # Optionally initialize on creation, or do it lazily

    def get_current_provider_name(self) -> str:
        """Returns the name of the currently configured LLM provider."""
        return self.current_provider_name

    def set_provider(self, provider_name: str):
        """
        Sets the LLM provider and attempts to initialize its client.
        (Note: Actual client switching logic will be more involved)
        """
        if provider_name != self.current_provider_name:
            print(f"Switching LLM provider from {self.current_provider_name} to {provider_name}")
            self.current_provider_name = provider_name
            self.llm_client = None # Reset client, will be re-initialized on next get_llm_client call
            # self.get_llm_client() # Optionally re-initialize immediately
        else:
            print(f"Provider is already set to {provider_name}")


    def get_llm_client(self):
        """
        Returns an initialized LLM client for the current provider.
        Initializes the client if it hasn't been already.
        This is a placeholder and will need actual SDK integration.
        """
        if self.llm_client:
            return self.llm_client

        provider_name = self.get_current_provider_name().lower()

        service_name_for_key = provider_name
        if provider_name == "claude":
            service_name_for_key = "anthropic" # Claude uses ANTHROPIC_API_KEY

        api_key = self.config_manager.get_api_key(service_name_for_key)

        if not api_key:
            print(f"Error: API key for {service_name_for_key.upper()} (provider: {provider_name}) not found. Cannot initialize client.")
            self.llm_client = None
            return None

        print(f"Attempting to initialize LLM client for: {provider_name.upper()}")

        # Actual client initialization would happen here
        if provider_name == "gemini":
            # Placeholder: Replace with actual Gemini client initialization
            # Example using google-generativeai SDK:
            # try:
            #     genai.configure(api_key=api_key)
            #     model = genai.GenerativeModel('gemini-pro') # Or other specific model
            #     self.llm_client = model
            #     print(f"Gemini client initialized successfully (placeholder).")
            # except Exception as e:
            #     print(f"Error initializing Gemini client: {e}")
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                # Model name can be made configurable in settings.yaml later
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                self.llm_client = model
                print(f"Gemini client ('gemini-1.5-flash-latest') initialized successfully.")
            except ImportError:
                print("Error: google.generativeai library not found. Please install it.")
                self.llm_client = None
            except Exception as e: # Catch other potential errors from genai.configure or GenerativeModel
                print(f"Error initializing Gemini client: {e}")
                self.llm_client = None
            # No return None here, just set self.llm_client

        elif provider_name == "claude": # Anthropic uses "claude" but API key might be ANTHROPIC_API_KEY
            # Placeholder: Replace with actual Claude client initialization
            # For now, it will use the mock client string if API key for Anthropic is found.
            # Example using anthropic SDK:
            # try:
            #     self.llm_client = anthropic.Anthropic(api_key=api_key)
            #     print(f"Claude (Anthropic) client initialized successfully (placeholder).")
            # except Exception as e:
            #     print(f"Error initializing Claude client: {e}")
            #     self.llm_client = None
            #     return None
            print(f"Claude (Anthropic) client initialized (placeholder with API key: ...{api_key[-4:] if api_key else 'N/A'}).")
            self.llm_client = f"MockClaudeClient(api_key_ending_with={api_key[-4:] if api_key else 'N/A'})" # Mock object

        # Example for OpenAI (if added later)
        # elif provider_name == "openai":
        #     print(f"OpenAI client initialized (placeholder with API key: ...{api_key[-4:] if api_key else 'N/A'}).")
        #     self.llm_client = f"MockOpenAIClient(api_key_ending_with={api_key[-4:] if api_key else 'N/A'})"

        else:
            print(f"Error: LLM provider '{provider_name}' is not supported.")
            self.llm_client = None
            return None

        return self.llm_client

    def generate_text(self, prompt: str, provider: str = None) -> str:
        """
        Generates text using the specified or current LLM provider.
        This is a high-level placeholder.
        """
        if provider and provider.lower() != self.current_provider_name.lower():
            # This is a simplified way; actual provider switching might be more complex
            # or might require getting a temporary client for that provider.
            print(f"Note: generate_text called for '{provider}', but current is '{self.current_provider_name}'.")
            print("For this placeholder, we'll use the current provider's client.")
            # In a real app, you might temporarily switch or get a specific client.

        client = self.get_llm_client() # Ensures client is initialized for current_provider_name

        if not client:
            return f"Error: LLM client for {self.current_provider_name} not available."

        # Actual generation call
        print(f"LLMManager: Sending prompt to {self.current_provider_name} (via mock client: {client}): '{prompt[:50]}...'")

        # This method will now attempt to use a live client if available.
        # The mock client strings like "MockGeminiClient..." will be replaced by actual client objects.

        if not client: # Could not initialize or not set
             return f"Error: LLM client for {self.current_provider_name} not available or not initialized."

        provider_name = self.get_current_provider_name().lower()

        try:
            if provider_name == "gemini":
                # Assuming client is an initialized genai.GenerativeModel instance
                if hasattr(client, 'generate_content'):
                    response = client.generate_content(prompt)
                    return response.text
                else:
                    return f"Error: Gemini client for {self.current_provider_name} is not a valid model instance."
            # Add elif for "claude" and other providers when their live integration is added
            # elif provider_name == "claude":
            #     return f"Claude live generation not yet implemented. Prompt: '{prompt}'"
            else:
                # Fallback for mock clients or unhandled live clients
                if "MockClaudeClient" in str(client): # Check if it's one of our known mock strings
                     return f"Claude (mock) response to: '{prompt}'"
                return f"Generic mock response or unhandled live client for {self.current_provider_name} to: '{prompt}' (Client type: {type(client)})"

        except Exception as e:
            # Catch broad exceptions from API calls (network, API errors, content filtering etc.)
            error_message = f"LLM API Error ({provider_name}): {str(e)}"
            print(error_message)
            # Potentially log more details: traceback.format_exc()
            return error_message # Return the error message itself for GameManager to handle


if __name__ == '__main__':
    print("--- Testing LLMManager ---")

    # This test expects 'cursor_clone_app/config/settings.yaml' and 'cursor_clone_app/.env'
    # to be present and configured by the user for a live test.
    # 'settings.yaml' should set 'default_llm_provider: "gemini"'
    # '.env' should contain a valid 'GEMINI_API_KEY'.

    _core_dir = os.path.dirname(os.path.abspath(__file__))
    _app_dir = os.path.dirname(_core_dir)
    _project_root = os.path.dirname(_app_dir)

    settings_file_path = os.path.join(_project_root, "config", "settings.yaml")
    env_file_path = os.path.join(_project_root, ".env")

    print(f"LLMManager Test: Expecting settings.yaml at: {settings_file_path}")
    print(f"LLMManager Test: Expecting .env at: {env_file_path} (with valid GEMINI_API_KEY for live test)")

    if not os.path.exists(settings_file_path):
        print(f"WARNING: {settings_file_path} not found. Creating a dummy one with Gemini as default.")
        os.makedirs(os.path.dirname(settings_file_path), exist_ok=True)
        with open(settings_file_path, "w") as f:
            yaml.dump({"default_llm_provider": "gemini"}, f)
        created_dummy_settings = True
    else:
        created_dummy_settings = False

    if not os.path.exists(env_file_path):
        print(f"WARNING: {env_file_path} not found. Live Gemini test cannot proceed without API key.")
        print("Please create it and add your GEMINI_API_KEY.")
        # Optionally create a template .env if it's missing entirely
        # with open(env_file_path, "w") as f:
        #     f.write("GEMINI_API_KEY=YOUR_KEY_HERE\n")
        # print(f"Created a template {env_file_path}. Please fill it.")

    config_manager = ConfigManager() # Uses actual files

    gemini_api_key = config_manager.get_api_key("GEMINI")
    if not gemini_api_key:
        print("GEMINI_API_KEY not found by ConfigManager. Cannot perform live Gemini test.")
    else:
        print(f"GEMINI_API_KEY found (ends with ...{gemini_api_key[-4:] if len(gemini_api_key) > 4 else '****'}). Initializing LLMManager...")
        llm_manager = LLMManager(config_manager=config_manager)

        # Ensure Gemini is selected if settings.yaml wasn't 'gemini' or was missing
        current_provider = llm_manager.get_current_provider_name()
        if current_provider.lower() != "gemini":
            print(f"Default provider is '{current_provider}', switching to 'gemini' for this test.")
            llm_manager.set_provider("gemini")

        # Attempt to get client, which initializes it
        client = llm_manager.get_llm_client() # This will print initialization status

        if client and not isinstance(client, str): # Check if it's a real client object, not a mock string
            print("\nAttempting live Gemini call...")
            prompt = "In one short sentence, what is a language model?"
            response = llm_manager.generate_text(prompt)
            print(f"\nResponse from Live Gemini for '{prompt}':")
            print(f">>> {response}")
            if "LLM API Error" in response:
                print("ERROR during live call. Check API key, quotas, and network.")
            elif not response or response.strip() == "":
                 print("WARN: Live call returned empty response.")
            else:
                print("Live Gemini call appears successful.")
        else:
            print("\nGemini client not initialized or is a mock/placeholder. Skipping live call.")
            print("Ensure your GEMINI_API_KEY in cursor_clone_app/.env is valid and active.")

    if created_dummy_settings and os.path.exists(settings_file_path):
        print(f"Cleaning up dummy {settings_file_path}")
        os.remove(settings_file_path)
        # Try to remove config dir if empty
        try:
            if not os.listdir(os.path.dirname(settings_file_path)):
                os.rmdir(os.path.dirname(settings_file_path))
        except OSError:
            pass # Ignore if not empty or other issues

    print("\n--- LLMManager test complete ---")
