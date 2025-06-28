import os
from dotenv import load_dotenv

def load_api_key_from_env(service_name: str) -> str | None:
    """
    Loads an API key for a given service from environment variables.
    It assumes environment variables are named like SERVICE_NAME_API_KEY (e.g., GEMINI_API_KEY).

    Args:
        service_name (str): The name of the service (e.g., "GEMINI", "ANTHROPIC").
                            The function will convert it to uppercase.

    Returns:
        str | None: The API key if found, otherwise None.
    """
    # Ensure .env is loaded. If called multiple times, load_dotenv is safe (doesn't overwrite).
    # It's better to call load_dotenv once at application startup, but this makes the util self-contained.
    # Consider where the .env file is located. If this util is deep, it might not find it.
    # For now, assume .env is in the root of the project or detectable by python-dotenv.
    # A more robust approach is to pass the .env path or ensure it's loaded globally.

    # Try to find .env relative to this file or common project structures
    # This is a bit heuristic. A global config for .env path is better.
    # current_dir = os.path.dirname(os.path.abspath(__file__)) # .../app/utils
    # app_dir = os.path.dirname(current_dir) # .../app
    # project_root = os.path.dirname(app_dir) # .../cursor_clone_app
    # dotenv_path_project_root = os.path.join(project_root, ".env")

    # Simpler: let python-dotenv try to find it, or it should be loaded by ConfigManager
    # load_dotenv() # This might be redundant if ConfigManager also calls it.

    key_variable_name = f"{service_name.upper()}_API_KEY"
    api_key = os.getenv(key_variable_name)

    if not api_key:
        # Try a common alternative pattern if the above is not found (e.g. SERVICE_KEY)
        key_variable_name_alt = f"{service_name.upper()}_KEY"
        api_key = os.getenv(key_variable_name_alt)

    return api_key

if __name__ == '__main__':
    # To test this function, you would need a .env file in the expected location
    # with keys like GEMINI_API_KEY="test_gemini_key"

    # Create a dummy .env for testing if it doesn't exist
    dummy_env_path = ".env_test_api_utils" # Create in current dir for test
    if not os.path.exists(dummy_env_path):
        with open(dummy_env_path, "w") as f:
            f.write("GEMINI_API_KEY=actual_gemini_key_from_test_env\n")
            f.write("ANTHROPIC_KEY=actual_anthropic_key_from_test_env_alt_name\n")
            f.write("OPENAI_API_KEY=\n") # Test empty key
            f.write("#SOME_OTHER_KEY=some_value\n")

    # Explicitly load the dummy .env for this test
    load_dotenv(dotenv_path=dummy_env_path)

    print(f"Attempting to load GEMINI_API_KEY...")
    gemini_key = load_api_key_from_env("GEMINI")
    print(f"GEMINI Key: {gemini_key}")

    print(f"\nAttempting to load ANTHROPIC_KEY (alternative name)...")
    anthropic_key = load_api_key_from_env("ANTHROPIC") # Should find ANTHROPIC_KEY
    print(f"ANTHROPIC Key: {anthropic_key}")

    print(f"\nAttempting to load OPENAI_API_KEY (empty)...")
    openai_key = load_api_key_from_env("OPENAI")
    print(f"OPENAI Key: '{openai_key}' (should be empty string if set, or None if not set)")

    print(f"\nAttempting to load NONEXISTENT_SERVICE_API_KEY...")
    non_existent_key = load_api_key_from_env("NONEXISTENT_SERVICE")
    print(f"NONEXISTENT_SERVICE Key: {non_existent_key}")

    # Clean up dummy .env
    if os.path.exists(dummy_env_path):
        os.remove(dummy_env_path)
