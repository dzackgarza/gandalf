import sys
import os

# Pre-UI imports for testing config and LLM manager
from cursor_clone_app.app.core.config_manager import ConfigManager
from cursor_clone_app.app.core.llm_manager import LLMManager # Import LLMManager

# UI Imports
from PySide6.QtWidgets import QApplication # Ensure QApplication is imported
from cursor_clone_app.app.ui.main_window import MainWindow
import qdarkstyle


# It's good practice to set an AppUserModelID for Windows to handle taskbar icon correctly.
try:
    from PySide6.QtWinExtras import QtWin
    myappid = u'mycompany.myproduct.subproduct.version' # Adjust as needed
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass # Not on Windows or QtWinExtras not available

def main():
    # ---- ConfigManager Setup ----
    # ConfigManager will look for 'cursor_clone_app/config/settings.yaml'
    # and 'cursor_clone_app/.env' (relative to project root it calculates)
    config_manager = ConfigManager()

    print("--- ConfigManager Test from main.py (Loaded Values) ---")
    default_provider_setting = config_manager.get_setting("default_llm_provider", "ProviderNotFound")
    print(f"[Config] Default LLM Provider from settings.yaml: {default_provider_setting}")
    gemini_key_env = config_manager.get_api_key("GEMINI")
    print(f"[Config] GEMINI_API_KEY from .env: {'Exists' if gemini_key_env else 'Not Found'}")
    print("--- End ConfigManager Info ---\n")

    # ---- LLMManager Test ----
    print("--- LLMManager Test from main.py ---")
    llm_manager = LLMManager(config_manager=config_manager)

    print(f"[LLM Test] Current LLM Provider: {llm_manager.get_current_provider_name()}")

    # Attempt to get/initialize the client for the default provider
    client = llm_manager.get_llm_client()
    print(f"[LLM Test] Obtained client for default provider: {client}")

    # Test placeholder text generation
    if client:
        prompt = "Tell me a joke about Python."
        response = llm_manager.generate_text(prompt)
        print(f"[LLM Test] Prompt: {prompt}")
        print(f"[LLM Test] Mock Response: {response}")
    else:
        print("[LLM Test] Could not get LLM client, skipping generation test.")

    # Test switching provider (if settings.yaml and .env support another)
    # Example: if ANTHROPIC_API_KEY is in .env
    print("\n[LLM Test] Attempting to switch to Claude...")
    llm_manager.set_provider("claude") # Assumes 'claude' is a potential provider
    claude_client = llm_manager.get_llm_client()
    print(f"[LLM Test] Obtained client for Claude: {claude_client}")
    if claude_client:
        claude_prompt = "Explain recursion simply."
        claude_response = llm_manager.generate_text(claude_prompt) # Will use current provider (Claude)
        print(f"[LLM Test] Prompt (Claude): {claude_prompt}")
        print(f"[LLM Test] Mock Response (Claude): {claude_response}")
    else:
        print("[LLM Test] Could not get Claude client.")
    print("--- End LLMManager Test ---\n")
    # ---- End LLMManager Test ----

    app = QApplication(sys.argv)

    try:
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
    except Exception as e:
        print(f"Error loading QDarkStyle: {e}. Using default style.")

    main_window = MainWindow()
    # Potentially pass config_manager or llm_manager to main_window if needed by UI directly
    # e.g., main_window = MainWindow(llm_manager=llm_manager)
    main_window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
