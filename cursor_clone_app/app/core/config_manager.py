import yaml
import os
from dotenv import load_dotenv
from ..utils.api_utils import load_api_key_from_env # Relative import for utils

class ConfigManager:
    def __init__(self, settings_filename="settings.yaml", env_filename=".env"):
        """
        Manages application settings from a YAML file and API keys from a .env file.

        Args:
            settings_filename (str): Name of the YAML settings file. Expected in 'config/' directory relative to project root.
            env_filename (str): Name of the .env file. Expected in project root.
        """
        self.settings = {}

        # Determine project root dynamically - assumes this file is in app/core/
        # cursor_clone_app/app/core/config_manager.py
        current_script_path = os.path.abspath(__file__)
        # .../cursor_clone_app/app/core/
        core_dir = os.path.dirname(current_script_path)
        # .../cursor_clone_app/app/
        app_dir = os.path.dirname(core_dir)
        # .../cursor_clone_app/
        self.project_root = os.path.dirname(app_dir)

        self.settings_path = os.path.join(self.project_root, "config", settings_filename)
        self.env_path = os.path.join(self.project_root, env_filename) # .env in project root

        self._load_settings()
        self._load_env_vars()

    def _load_settings(self):
        try:
            with open(self.settings_path, 'r') as f:
                self.settings = yaml.safe_load(f)
            if self.settings is None: # Handle empty YAML file
                self.settings = {}
                print(f"Warning: Settings file '{self.settings_path}' is empty or invalid.")
        except FileNotFoundError:
            print(f"Warning: Settings file '{self.settings_path}' not found. Using default settings.")
            self.settings = {} # Default to empty dict if file not found
        except yaml.YAMLError as e:
            print(f"Error parsing YAML settings file '{self.settings_path}': {e}")
            self.settings = {}

    def _load_env_vars(self):
        """Loads environment variables from the .env file."""
        if os.path.exists(self.env_path):
            load_dotenv(dotenv_path=self.env_path, override=True)
            # print(f"Loaded environment variables from: {self.env_path}")
        else:
            print(f"Warning: Environment file '{self.env_path}' not found. API keys might be missing.")

    def get_setting(self, key_path: str, default=None):
        """
        Retrieves a setting using a dot-separated key path (e.g., "editor.font_size").

        Args:
            key_path (str): Dot-separated path to the setting.
            default: Value to return if the key is not found.

        Returns:
            The setting value or the default.
        """
        try:
            value = self.settings
            for key in key_path.split('.'):
                if not isinstance(value, dict) or key not in value: # Check if value is a dict before access
                    return default
                value = value[key]
            return value
        except TypeError: # Handles cases where an intermediate key is not a dictionary
            return default
        except Exception: # Catch any other unexpected errors during lookup
            return default

    def get_api_key(self, service_name: str) -> str | None:
        """
        Retrieves an API key for the given service name.
        This method now directly uses os.getenv, assuming _load_env_vars has been called.

        Args:
            service_name (str): The name of the service (e.g., "GEMINI").

        Returns:
            str | None: The API key if found, otherwise None.
        """
        # The actual loading of .env is handled by _load_env_vars() during __init__
        # api_utils.load_api_key_from_env is still useful if someone wants to call it directly,
        # but ConfigManager ensures .env is loaded once.

        key_variable_name = f"{service_name.upper()}_API_KEY"
        api_key = os.getenv(key_variable_name)

        if not api_key:
            key_variable_name_alt = f"{service_name.upper()}_KEY"
            api_key = os.getenv(key_variable_name_alt)

        return api_key

# Test block
if __name__ == '__main__':
    # To test ConfigManager, we need a dummy project structure or to run it from project root.
    # Let's assume we are running this test from the project root `cursor_clone_app/`
    # and the structure is:
    # cursor_clone_app/
    #   config/
    #     settings.yaml
    #   .env
    #   app/
    #     core/
    #       config_manager.py (this file)
    #     utils/
    #       api_utils.py

    print("Testing ConfigManager...")

    # Create dummy config/settings.yaml and .env at expected relative locations for testing
    # This assumes the script is run from .../cursor_clone_app/app/core
    # So, project_root will be .../cursor_clone_app

    # Determine where this test is being run from to create dummy files correctly
    _current_script_path = os.path.abspath(__file__)
    _core_dir = os.path.dirname(_current_script_path)
    _app_dir = os.path.dirname(_core_dir)
    _project_root = os.path.dirname(_app_dir)

    dummy_config_dir = os.path.join(_project_root, "config")
    dummy_settings_file = os.path.join(dummy_config_dir, "settings.yaml")
    dummy_env_file = os.path.join(_project_root, ".env")

    os.makedirs(dummy_config_dir, exist_ok=True)
    with open(dummy_settings_file, "w") as f:
        yaml.dump({
            "default_llm_provider": "gemini_test",
            "editor": {
                "font_size": 14,
                "theme": "dark_test"
            },
            "user_context_directories": ["/test/path1", "test/path2"]
        }, f)

    with open(dummy_env_file, "w") as f:
        f.write("GEMINI_TEST_API_KEY=dummy_gemini_key_from_config_test\n")
        f.write("CLAUDE_API_KEY=dummy_claude_key_from_config_test\n")

    print(f"Dummy settings file created at: {dummy_settings_file}")
    print(f"Dummy .env file created at: {dummy_env_file}")

    # Instantiate ConfigManager - it should find these dummy files
    config_manager = ConfigManager(settings_filename="settings.yaml", env_filename=".env")

    print("\n--- Settings ---")
    print(f"Default LLM Provider: {config_manager.get_setting('default_llm_provider', 'default_val')}")
    print(f"Editor Font Size: {config_manager.get_setting('editor.font_size', 'default_val')}")
    print(f"Editor Theme: {config_manager.get_setting('editor.theme', 'default_val')}")
    print(f"Non-existent setting: {config_manager.get_setting('non.existent.key', 'default_val_for_non_existent')}")
    print(f"User context dirs: {config_manager.get_setting('user_context_directories', [])}")

    print("\n--- API Keys ---")
    print(f"GEMINI_TEST API Key: {config_manager.get_api_key('GEMINI_TEST')}")
    print(f"CLAUDE API Key: {config_manager.get_api_key('CLAUDE')}")
    print(f"OPENAI API Key (should be None): {config_manager.get_api_key('OPENAI')}")

    # Clean up dummy files
    os.remove(dummy_settings_file)
    if not os.listdir(dummy_config_dir): # Remove config dir if empty
        os.rmdir(dummy_config_dir)
    os.remove(dummy_env_file)
    print("\nCleaned up dummy files.")

    # Test with actual project files (if they exist) by creating another instance
    print("\n--- Testing with actual project files (if they exist) ---")
    # This will look for cursor_clone_app/config/settings.yaml and cursor_clone_app/.env
    # The paths in __init__ are relative to project root, which is fine.
    # The `settings_filename` and `env_filename` are just names, not paths.
    # The `ConfigManager` constructs the full path.

    # No, the constructor expects just the filenames, it constructs the path.
    # So, this is how it would be instantiated in main.py
    # This assumes main.py is in cursor_clone_app/
    # and ConfigManager is in cursor_clone_app/app/core/
    # The relative path calculation in __init__ should correctly find project_root.

    # The issue might be if this test script itself is not located at cursor_clone_app/app/core/config_manager.py
    # For the test, the explicit path building for dummy files is good.
    # When used by the app, its location within the structure defines `self.project_root`.

    # Let's simulate how it would be called from within the app structure:
    # ConfigManager() will use default filenames "settings.yaml" and ".env"
    # and its internal logic to find project_root from its own location.

    # This means the dummy files created earlier are what it *should* find if the test is run
    # from its own directory within the structure.
    # The cleanup should have removed them. Let's try re-creating them as they would be in the project.

    # Re-create dummy files in the *actual* project structure for this second test part
    actual_project_config_dir = os.path.join(_project_root, "config")
    actual_project_settings_file = os.path.join(actual_project_config_dir, "settings.yaml")
    actual_project_env_file = os.path.join(_project_root, ".env")

    # Use the settings content from the plan
    os.makedirs(actual_project_config_dir, exist_ok=True)
    with open(actual_project_settings_file, "w") as f:
        yaml.dump({
            "default_llm_provider": "gemini",
            "user_context_directories": [],
            "max_chat_history_tokens": 4000,
            "editor": {"font_size": 12, "tab_width": 4},
            "log_level": "INFO",
            "log_file": "app.log"
        }, f)

    # Create a dummy .env in project root if it doesn't exist for test purposes
    # It's okay if it's empty or has other keys.
    if not os.path.exists(actual_project_env_file):
        with open(actual_project_env_file, "w") as f:
            f.write("GEMINI_API_KEY=key_for_second_test_gemini\n")
            f.write("ANTHROPIC_API_KEY=key_for_second_test_anthropic\n")
            f.write("TAVILY_API_KEY=key_for_second_test_tavily\n")
        env_created_for_test = True
    else:
        env_created_for_test = False
        print(f"Using existing project .env file at {actual_project_env_file} for second test part.")


    print("Instantiating ConfigManager for 'actual' files test...")
    # This instantiation relies on the ConfigManager's internal path logic
    actual_config_manager = ConfigManager()
    print(f"Actual settings path used: {actual_config_manager.settings_path}")
    print(f"Actual .env path used: {actual_config_manager.env_path}")

    print(f"Default LLM (actual): {actual_config_manager.get_setting('default_llm_provider', 'N/A')}")
    print(f"Editor Font (actual): {actual_config_manager.get_setting('editor.font_size', 'N/A')}")
    print(f"GEMINI Key (actual): {actual_config_manager.get_api_key('GEMINI')}")
    print(f"ANTHROPIC Key (actual): {actual_config_manager.get_api_key('ANTHROPIC')}")
    print(f"TAVILY Key (actual): {actual_config_manager.get_api_key('TAVILY')}")

    # Clean up files created for the "actual" test part
    os.remove(actual_project_settings_file)
    if not os.listdir(actual_project_config_dir):
        os.rmdir(actual_project_config_dir)
    if env_created_for_test and os.path.exists(actual_project_env_file):
        os.remove(actual_project_env_file)

    print("Done with ConfigManager tests.")
