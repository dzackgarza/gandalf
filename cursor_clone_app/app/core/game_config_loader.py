import yaml
import os
from typing import Dict, Any, List

class GameConfigLoader:
    """
    Loads and validates game configuration files from YAML.
    """

    REQUIRED_TOP_LEVEL_KEYS = ["game_name", "handshake", "initial_state", "states"]
    REQUIRED_HANDSHAKE_KEYS = ["initial_prompt_template", "llm_confirmation_response", "max_attempts"]
    REQUIRED_STATE_KEYS = ["prompt_template", "choices"] # Not all states need on_enter_actions or default_next_state
    # 'description' and 'action' are optional for a choice.
    REQUIRED_CHOICE_KEYS = ["id", "next_state"]

    def _validate_game_config(self, config_data: Dict[str, Any], filepath: str) -> bool:
        """
        Performs basic validation on a single game's parsed YAML data.
        Returns True if valid, False otherwise (with error messages printed).
        """
        for key in self.REQUIRED_TOP_LEVEL_KEYS:
            if key not in config_data:
                print(f"Validation Error: Missing required top-level key '{key}' in {filepath}")
                return False

        # Validate handshake section
        handshake_data = config_data.get("handshake", {})
        for key in self.REQUIRED_HANDSHAKE_KEYS:
            if key not in handshake_data:
                print(f"Validation Error: Missing key '{key}' in 'handshake' section of {filepath}")
                return False

        if not isinstance(config_data.get("states"), dict) or not config_data.get("states"):
            print(f"Validation Error: 'states' must be a non-empty dictionary in {filepath}")
            return False

        # Validate each state
        for state_name, state_data in config_data.get("states", {}).items():
            if not isinstance(state_data, dict):
                print(f"Validation Error: State '{state_name}' must be a dictionary in {filepath}")
                return False
            for key in self.REQUIRED_STATE_KEYS:
                if key not in state_data:
                    # Special case: _data_input_ states might not have typical "choices" list for LLM selection
                    if key == "choices" and any(c.get("id") == "_data_input_" for c in state_data.get("choices", [])):
                        # If it's a data input state, check if it has at least one choice (the _data_input_ one)
                        if not state_data.get("choices"):
                             print(f"Validation Error: Missing required key '{key}' in state '{state_name}' of {filepath}")
                             return False
                    else:
                        print(f"Validation Error: Missing required key '{key}' in state '{state_name}' of {filepath}")
                        return False

            # Validate choices within the state
            choices = state_data.get("choices", [])
            if not isinstance(choices, list):
                print(f"Validation Error: 'choices' must be a list in state '{state_name}' of {filepath}")
                return False

            for choice in choices:
                if not isinstance(choice, dict):
                    print(f"Validation Error: Each choice must be a dictionary in state '{state_name}' of {filepath}")
                    return False
                for key in self.REQUIRED_CHOICE_KEYS:
                    if key not in choice:
                        print(f"Validation Error: Missing key '{key}' in a choice within state '{state_name}' of {filepath}")
                        return False

        # Check if initial_state exists in states
        initial_state = config_data.get("initial_state")
        if initial_state not in config_data.get("states", {}):
            print(f"Validation Error: 'initial_state' ('{initial_state}') not found in 'states' definition in {filepath}")
            return False

        return True

    def load_game_config(self, filepath: str) -> Dict[str, Any] | None:
        """
        Loads a single YAML game file.
        Performs validation after loading.
        """
        if not os.path.exists(filepath):
            print(f"Error: Game config file not found: {filepath}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {filepath}: {e}")
            return None
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None

        if not isinstance(data, dict):
            print(f"Error: Game config file {filepath} does not contain a valid YAML dictionary.")
            return None

        if self._validate_game_config(data, filepath):
            return data
        else:
            print(f"Game config file {filepath} failed validation.")
            return None

    def load_all_games(self, games_directory: str) -> Dict[str, Dict[str, Any]]:
        """
        Scans the given directory for YAML files (*.yaml or *.yml),
        loads them, and returns a dictionary mapping game_name to its config data.
        """
        loaded_games: Dict[str, Dict[str, Any]] = {}
        if not os.path.isdir(games_directory):
            print(f"Error: Games directory not found: {games_directory}")
            return loaded_games

        for filename in os.listdir(games_directory):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                filepath = os.path.join(games_directory, filename)
                print(f"Attempting to load game config: {filepath}")
                game_data = self.load_game_config(filepath)
                if game_data:
                    game_name = game_data.get("game_name")
                    if game_name:
                        if game_name in loaded_games:
                            print(f"Warning: Duplicate game_name '{game_name}' found. Overwriting with config from {filepath}.")
                        loaded_games[game_name] = game_data
                        print(f"Successfully loaded game: '{game_name}' from {filepath}")
                    else:
                        # This should have been caught by validation, but as a safeguard:
                        print(f"Warning: Game config from {filepath} loaded but has no 'game_name'. Skipping.")

        if not loaded_games:
            print(f"No game configurations were successfully loaded from {games_directory}.")
        return loaded_games


if __name__ == '__main__':
    print("--- Testing GameConfigLoader ---")

    # Determine project root to find config/games relative to this script's location
    # This assumes this script (game_config_loader.py) is in app/core/
    current_script_path = os.path.abspath(__file__)
    core_dir = os.path.dirname(current_script_path)
    app_dir = os.path.dirname(core_dir)
    project_root = os.path.dirname(app_dir) # Should be 'cursor_clone_app'

    # Path to the actual games directory within the project structure
    actual_games_dir = os.path.join(project_root, "config", "games")
    print(f"Using actual games directory for testing: {actual_games_dir}")

    # Ensure div_editor_game.yaml exists from the previous step
    div_editor_path = os.path.join(actual_games_dir, "div_editor_game.yaml")
    if not os.path.exists(div_editor_path):
        print(f"ERROR: Required test file {div_editor_path} not found. Please run previous step.")
    else:
        loader = GameConfigLoader()

        # Test loading a single valid file (div_editor_game.yaml)
        print(f"\n--- Test 1: Loading single valid game '{div_editor_path}' ---")
        div_editor_config = loader.load_game_config(div_editor_path)
        if div_editor_config:
            print(f"Loaded '{div_editor_config.get('game_name')}': Successfully.")
            # print(f"Config data (sample): initial_state = {div_editor_config.get('initial_state')}")
        else:
            print(f"Failed to load '{div_editor_path}'. Check validation errors above.")

        # Test loading all games from the directory
        print(f"\n--- Test 2: Loading all games from '{actual_games_dir}' ---")
        all_games = loader.load_all_games(actual_games_dir)
        if all_games:
            print(f"Total games loaded: {len(all_games)}")
            for name, conf in all_games.items():
                print(f"  - Game: {name}, Initial State: {conf.get('initial_state')}")
        else:
            print("No games were loaded by load_all_games.")

        # Test with a non-existent file
        print("\n--- Test 3: Loading non-existent game file ---")
        non_existent_config = loader.load_game_config(os.path.join(actual_games_dir, "non_existent_game.yaml"))
        if non_existent_config is None:
            print("Correctly handled non-existent file (returned None).")
        else:
            print("Error: Should have returned None for non-existent file.")

        # Create a dummy invalid game file for testing validation
        dummy_invalid_path = os.path.join(actual_games_dir, "_temp_invalid_game.yaml")
        print(f"\n--- Test 4: Loading invalid game file '{dummy_invalid_path}' ---")
        with open(dummy_invalid_path, "w", encoding="utf-8") as f:
            yaml.dump({"game_name": "Invalid Game", "handshake": {}}, f) # Missing many keys

        invalid_config = loader.load_game_config(dummy_invalid_path)
        if invalid_config is None:
            print("Correctly handled invalid game file (returned None due to validation failure).")
        else:
            print("Error: Should have returned None for invalid game file.")

        if os.path.exists(dummy_invalid_path):
            os.remove(dummy_invalid_path)

        print("\n--- GameConfigLoader tests complete ---")
