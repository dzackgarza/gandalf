import os
import re # Import the 're' module
from typing import Dict, Any, List, Tuple, Optional

from .llm_manager import LLMManager
from .game_config_loader import GameConfigLoader
# Need to import ChatPanel and TextEditorArea for type hinting if used directly,
# but it's better to use a more generic approach or callbacks if possible
# For now, assume we have references to the UI elements for direct interaction.
# from ..ui.chat_panel import ChatPanel
# from ..ui.text_editor import TextEditorArea # Not directly imported for type hint to avoid circularity if TextEditorArea needs GameManager
from ..utils.markdown_utils import extract_fenced_divs # Import the new utility

class GameState:
    """Holds the runtime state of an active game."""
    def __init__(self, game_config: Dict[str, Any]):
        self.game_config: Dict[str, Any] = game_config
        self.game_name: str = game_config.get("game_name", "Unknown Game")
        self.current_state_name: str = game_config.get("initial_state", "")
        self.game_history: List[Dict[str, str]] = [] # List of {"sender": "...", "message": "..."}

        # For game-specific data, e.g., list of divs, current div index
        self.game_data: Dict[str, Any] = {}

        self.invalid_choices_current_turn: int = 0
        self.total_invalid_choices: int = 0

        self.handshake_attempts: int = 0
        self.is_handshake_complete: bool = False

        # Stores data LLM might be in the process of providing (e.g. a revision)
        self.pending_llm_data_for_action: Optional[Any] = None
        self.current_error_message: Optional[str] = None
        self.structured_response_attempts: int = 0 # For retrying data input like revisions


class GameManager:
    def __init__(self, llm_manager: LLMManager, chat_panel_ref: Any, text_editor_ref: Any, config_manager_ref: Any):
        """
        Manages game loading, state, and interaction between the LLM and the application.

        Args:
            llm_manager: Instance of LLMManager.
            chat_panel_ref: Reference to the ChatPanel UI element.
            text_editor_ref: Reference to the TextEditorArea UI element.
            config_manager_ref: Instance of ConfigManager (to find project root for games dir).
        """
        self.llm_manager = llm_manager
        self.chat_panel_ref = chat_panel_ref # Expected to have a method like display_message(sender, message)
        self.text_editor_ref = text_editor_ref # Expected to have method like get_current_document_content()
        self.config_manager_ref = config_manager_ref # Used to get project_root

        self.game_config_loader = GameConfigLoader()
        self.game_configs: Dict[str, Dict[str, Any]] = {}
        self.active_game_state: Optional[GameState] = None

        self._load_games_on_init() # Load games when GameManager is created

    def _get_project_root(self) -> str:
        # Similar logic to ConfigManager to find project root
        # Assumes this file is in app/core/
        current_script_path = os.path.abspath(__file__)
        core_dir = os.path.dirname(current_script_path)
        app_dir = os.path.dirname(core_dir)
        return os.path.dirname(app_dir)

    def _load_games_on_init(self):
        """Loads game configurations upon initialization."""
        project_root = self._get_project_root()
        # Default games directory path relative to project root
        default_games_dir = os.path.join(project_root, "config", "games")

        # Allow overriding games directory via settings.yaml if needed in the future
        # games_directory_setting = self.config_manager_ref.get_setting("games.directory", "config/games")
        # games_path = os.path.join(project_root, games_directory_setting)

        self.load_games(games_directory=default_games_dir)

    def load_games(self, games_directory: str):
        """
        Loads all game configurations from the specified directory.
        """
        print(f"GameManager: Attempting to load games from directory: {games_directory}")
        self.game_configs = self.game_config_loader.load_all_games(games_directory)
        if self.game_configs:
            print(f"GameManager: Successfully loaded {len(self.game_configs)} game(s).")
            for name in self.game_configs.keys():
                print(f"  - Available game: {name}")
        else:
            print("GameManager: No games were loaded.")

    def list_available_games(self) -> List[Tuple[str, str]]:
        """
        Returns a list of (game_name, description) for all loaded games.
        """
        if not self.game_configs:
            return []
        return [(data.get("game_name", "Unnamed Game"), data.get("description", "No description."))
                for data in self.game_configs.values()]

    def _display_in_chat(self, message: str, sender: str = "System"):
        """
        Helper method to display messages in the chat panel.
        Relies on chat_panel_ref having a method like `display_llm_response` or a generic one.
        For now, let's assume a method `add_message(sender: str, message: str)` on chat_panel_ref.
        """
        if hasattr(self.chat_panel_ref, 'add_message_from_game'): # Preferred method
            self.chat_panel_ref.add_message_from_game(sender, message)
        elif sender.lower() == "llm":
            if hasattr(self.chat_panel_ref, 'display_llm_response'):
                 self.chat_panel_ref.display_llm_response(message) # Assumes message is just the text part
            else: print(f"ChatPanel missing display_llm_response: LLM: {message}")
        elif sender.lower() == "user": # Should not happen if input is disabled
            if hasattr(self.chat_panel_ref, 'display_user_message'):
                self.chat_panel_ref.display_user_message(message)
            else: print(f"ChatPanel missing display_user_message: User: {message}")
        else: # System, Game, Error messages
            # Use a generic display method or adapt display_llm_response
            if hasattr(self.chat_panel_ref, 'display_system_message'):
                self.chat_panel_ref.display_system_message(message)
            elif hasattr(self.chat_panel_ref, 'history_view'): # Fallback to append
                 self.chat_panel_ref.history_view.append(f"<b>{sender}:</b> {message}\n")
            else:
                print(f"Game Log ({sender}): {message}")


    # --- Stubs for methods to be implemented in later steps ---
    def start_game(self, game_name: str) -> bool:
        """
        Starts a new game. Performs handshake with LLM.
        Returns True if game started successfully (handshake complete), False otherwise.
        """
        if self.active_game_state:
            self._display_in_chat("Another game is already active. Please end it first.", "Error")
            return False

        if game_name not in self.game_configs:
            self._display_in_chat(f"Game '{game_name}' not found.", "Error")
            return False

        self._display_in_chat(f"Starting game: {game_name}...", "Game")
        # Full implementation in Phase 2 (Handshake)
        self.active_game_state = GameState(self.game_configs[game_name])

        handshake_successful = self._perform_llm_handshake()

        if handshake_successful:
            self.active_game_state.is_handshake_complete = True
            self._display_in_chat(f"Handshake successful with LLM for game '{game_name}'. Starting game...", "Game")

            # Execute on_enter_actions for the initial state
            self._execute_actions_for_current_state()

            # The initial state might auto-transition (e.g. InitializeGame -> CheckNextDiv)
            # The present_current_state_to_llm will be called after these initial transitions if any.
            # If the initial state itself is one that prompts the LLM, present_current_state_to_llm will handle it.
            # For now, let's assume initial_state's on_enter might modify current_state_name.
            # If initial state logic (like InitializeGame) doesn't immediately prompt,
            # it should transition to a state that does, and that state's on_enter or prompt logic will take over.
            # The call to present_current_state_to_llm is made at the end of a turn or after state setup.
            # If on_enter_actions changed the state, present_current_state_to_llm will use the new state.
            self.present_current_state_to_llm()
            return True
        else:
            self._display_in_chat(f"LLM handshake failed for game '{game_name}'. Game aborted.", "Error")
            self.end_game("handshake_failed") # end_game now handles re-enabling input
            return False

    def _perform_llm_handshake(self) -> bool:
        """Performs the handshake protocol with the LLM."""
        if not self.active_game_state:
            return False

        game_cfg = self.active_game_state.game_config
        handshake_cfg = game_cfg.get("handshake", {})

        initial_prompt_template = handshake_cfg.get("initial_prompt_template", "")
        expected_response = handshake_cfg.get("llm_confirmation_response", "")
        max_attempts = handshake_cfg.get("max_attempts", 1)

        if not initial_prompt_template or not expected_response:
            self._display_in_chat("Handshake configuration missing in game YAML.", "Error")
            return False

        # Format the initial prompt (e.g., replace {{GAME_NAME}})
        formatted_prompt = initial_prompt_template.replace("{{GAME_NAME}}", self.active_game_state.game_name)

        for attempt in range(max_attempts):
            self.active_game_state.handshake_attempts = attempt + 1
            self._display_in_chat(f"--- Starting Handshake (Attempt {attempt + 1}/{max_attempts}) ---", "Game")
            self._display_in_chat(formatted_prompt, "Game")

            # Assume generate_text is synchronous for handshake
            llm_response = self.llm_manager.generate_text(prompt=formatted_prompt)

            if llm_response is None or llm_response.startswith("LLM API Error"):
                error_detail = llm_response if llm_response else "No response from LLM."
                self._display_in_chat(f"LLM communication error during handshake: {error_detail}", "Error")
                # This counts as a failed attempt, loop will continue or exit.
                # To ensure it's treated as a non-matching response for the check below:
                llm_response = f"HANDSHAKE_LLM_ERROR: {error_detail}" # Internal marker, won't match expected_response
            else:
                # Only display non-error LLM responses directly as "LLM"
                self._display_in_chat(llm_response.strip(), "LLM")

            if llm_response.strip() == expected_response.strip():
                return True
            else:
                self._display_in_chat(f"Handshake response incorrect. Expected: '{expected_response}'. Got: '{llm_response.strip()}'.", "Error")
                if attempt < max_attempts - 1:
                    self._display_in_chat("Retrying handshake...", "Game")
                # Optional: Add a small delay here if needed

        return False

    def _execute_actions_for_current_state(self):
        """Executes on_enter_actions for the current game state."""
        if not self.active_game_state or not self.active_game_state.is_handshake_complete:
            return

        state_name = self.active_game_state.current_state_name
        current_game_config = self.active_game_state.game_config
        state_def = current_game_config.get("states", {}).get(state_name, {})

        actions_to_execute = state_def.get("on_enter_actions", [])
        if not isinstance(actions_to_execute, list):
            self._display_in_chat(f"Warning: 'on_enter_actions' for state '{state_name}' is not a list. Skipping.", "System")
            return

        for action_name in actions_to_execute:
            action_method = getattr(self, action_name, self._unknown_action)
            try:
                # Pass action_name in case _unknown_action needs it, or if actions need their own name.
                # More complex actions might need specific parameters from game_state or state_def.
                action_method(action_name_param_if_needed=action_name)
            except Exception as e:
                self._display_in_chat(f"Error executing action '{action_name}' for state '{state_name}': {e}", "Error")
                # Optionally, end the game or transition to an error state here.

    def _unknown_action(self, action_name_param_if_needed: str, **kwargs):
        """Handles undefined game actions specified in YAML."""
        action_name = action_name_param_if_needed
        self._display_in_chat(f"Warning: Unknown action '{action_name}' defined in game config. Action not executed.", "System")

    def _extract_fenced_divs_from_editor(self) -> List[Dict[str, str]]:
        """
        Retrieves content from the current text editor tab and extracts fenced divs.
        """
        if not self.text_editor_ref or not hasattr(self.text_editor_ref, 'get_current_document_content'):
            self._display_in_chat("Error: TextEditorArea reference is invalid or missing 'get_current_document_content' method.", "System")
            if self.active_game_state: self.active_game_state.current_state_name = "END_GAME_FAILURE"
            return []

        document_content = self.text_editor_ref.get_current_document_content()
        if document_content is None:
            self._display_in_chat("Warning: No document open or content available in the current editor tab for div extraction.", "System")
            return [] # Handled by calling action

        return extract_fenced_divs(document_content)

    # --- Game Actions for 'div_editor_game.yaml' ---
    def action_initialize_div_editor_game(self, **kwargs):
        if not self.active_game_state: return
        self._display_in_chat("Action: Initializing Div Editor Game...", "GameDebug")

        game_config = self.active_game_state.game_config
        data_extraction_config = game_config.get("data_extraction")

        div_list_for_game = []
        raw_extracted_divs = []

        if data_extraction_config and data_extraction_config.get("extractor_action") == "extract_fenced_divs":
            raw_extracted_divs = self._extract_fenced_divs_from_editor()
            if self.active_game_state.current_state_name == "END_GAME_FAILURE": # Check if error occurred in _extract...
                return
        else:
            self._display_in_chat(f"Warning: 'data_extraction' config for 'extract_fenced_divs' not found in game YAML for {self.active_game_state.game_name}. Cannot extract divs.", "System")
            # Game cannot proceed without divs for this specific game.
            self.active_game_state.current_state_name = "END_GAME_FAILURE"
            return

        for i, raw_div in enumerate(raw_extracted_divs):
            div_list_for_game.append({
                'identifier': raw_div.get('name', f"Div {i+1}"),
                'original_content': raw_div.get('content', ''),
                'current_content': raw_div.get('content', ''),
                'status': 'pending',
                'full_original_block': raw_div.get('original_text', '')
            })

        if not div_list_for_game:
            self._display_in_chat("No divs found in the current document using 'extract_fenced_divs' method. Ending game.", "Game")
            self.active_game_state.current_state_name = "END_GAME_CANCELLED"
            return

        self.active_game_state.game_data['div_list'] = div_list_for_game
        self.active_game_state.game_data['current_div_index'] = -1
        self.active_game_state.game_data['num_divs'] = len(div_list_for_game)

        self._display_in_chat(f"Initialized with {len(div_list_for_game)} divs to process.", "GameDebug")

        self.active_game_state.current_state_name = "CheckNextDiv"
        self._execute_actions_for_current_state() # Chain to CheckNextDiv's actions


    def action_check_next_div(self, **kwargs):
        if not self.active_game_state: return
        self._display_in_chat("Action: Checking Next Div...", "GameDebug")

        current_idx = self.active_game_state.game_data.get('current_div_index', -1)
        num_divs = self.active_game_state.game_data.get('num_divs', 0)

        current_idx += 1
        self.active_game_state.game_data['current_div_index'] = current_idx

        if current_idx < num_divs:
            self._display_in_chat(f"Transitioning to next div (index {current_idx}).", "GameDebug")
            self.active_game_state.current_state_name = "SyntaxReviewStage_Prompt"
            self._execute_actions_for_current_state() # Execute on_enter for SyntaxReviewStage_Prompt
        else:
            self._display_in_chat("No more divs to process.", "GameDebug")
            self.active_game_state.current_state_name = "END_GAME_SUCCESS"
            # For END_GAME states, present_current_state_to_llm will call end_game. No further actions needed here.

    def action_load_current_div_for_syntax_review(self, **kwargs):
        if not self.active_game_state: return
        self._display_in_chat("Action: Loading Div for Syntax Review...", "GameDebug")
        div_idx = self.active_game_state.game_data.get('current_div_index', -1)
        div_list = self.active_game_state.game_data.get('div_list', [])
        if 0 <= div_idx < len(div_list):
            current_div = div_list[div_idx]
            self.active_game_state.game_data['current_div_content'] = current_div.get('current_content', "Error: Content not found.")
            self.active_game_state.game_data['current_div_identifier'] = current_div.get('identifier', f"Div {div_idx + 1}")
            self.active_game_state.game_data['current_div_index_display'] = div_idx + 1
            self.active_game_state.game_data['total_divs'] = len(div_list)
        else:
            self._display_in_chat(f"Error: Invalid div index {div_idx} for syntax review.", "Error")
            self.active_game_state.game_data['current_div_content'] = "Error: Could not load div."
            self.active_game_state.game_data['current_div_identifier'] = "Unknown Div"
            self.active_game_state.current_state_name = "END_GAME_FAILURE" # Critical if div cannot be loaded when expected

    def action_load_current_div_for_semantic_review(self, **kwargs):
        if not self.active_game_state: return
        self._display_in_chat("Action: Loading Div for Semantic Review...", "GameDebug")
        # This action is identical to syntax review load for now, just populates same game_data fields
        div_idx = self.active_game_state.game_data.get('current_div_index', -1)
        div_list = self.active_game_state.game_data.get('div_list', [])
        if 0 <= div_idx < len(div_list):
            current_div = div_list[div_idx]
            self.active_game_state.game_data['current_div_content'] = current_div.get('current_content', "Error: Content not found.")
            self.active_game_state.game_data['current_div_identifier'] = current_div.get('identifier', f"Div {div_idx + 1}")
            self.active_game_state.game_data['current_div_index_display'] = div_idx + 1 # For display
            self.active_game_state.game_data['total_divs'] = len(div_list) # For display
            # Update status if needed, e.g., div.status = "semantic_review_pending" (optional)
        else:
            self._display_in_chat(f"Error: Invalid div index {div_idx} for semantic review.", "Error")
            self.active_game_state.game_data['current_div_content'] = "Error: Could not load div."
            self.active_game_state.game_data['current_div_identifier'] = "Unknown Div"
            self.active_game_state.current_state_name = "END_GAME_FAILURE"

    def _process_revision(self, revised_content: str, review_type: str):
        """Helper to process revised content for syntax or semantics."""
        if not self.active_game_state: return False
        self._display_in_chat(f"Action: Processing {review_type} revision...", "GameDebug")

        div_idx = self.active_game_state.game_data.get('current_div_index', -1)
        div_list = self.active_game_state.game_data.get('div_list', [])

        if 0 <= div_idx < len(div_list):
            self.active_game_state.game_data['div_list'][div_idx]['current_content'] = revised_content
            # Optionally update status, e.g., 'syntax_revised', 'semantics_revised'
            self._display_in_chat(f"Div '{div_list[div_idx]['identifier']}' content updated after {review_type} revision.", "GameDebug")
            return True
        else:
            self._display_in_chat(f"Error: Invalid div index {div_idx} while processing {review_type} revision.", "Error")
            self.active_game_state.current_state_name = "END_GAME_FAILURE"
            return False

    def action_process_syntax_revision(self, revised_content: Optional[str] = None, **kwargs):
        # 'revised_content' will be passed by process_llm_response if parsing is successful
        if revised_content is None: # Should not happen if called correctly
             self._display_in_chat("Error: No revised content provided for syntax revision action.", "Error")
             self.active_game_state.current_state_name = "SyntaxReviewStage_Prompt" # Go back to prompt
             self.active_game_state.current_error_message = "Internal error: Revision content missing."
             return
        self._process_revision(revised_content, "syntax")
        # Next state (back to SyntaxReviewStage_Prompt) is handled by YAML definition of _data_input_ choice

    def action_process_semantic_revision(self, revised_content: Optional[str] = None, **kwargs):
        if revised_content is None:
             self._display_in_chat("Error: No revised content provided for semantic revision action.", "Error")
             self.active_game_state.current_state_name = "SemanticReviewStage_Prompt" # Go back to prompt
             self.active_game_state.current_error_message = "Internal error: Revision content missing."
             return
        self._process_revision(revised_content, "semantic")
        # Next state (back to SemanticReviewStage_Prompt) is handled by YAML

    def action_finalize_div_and_increment_index(self, **kwargs):
        if not self.active_game_state: return
        self._display_in_chat("Action: Finalizing Div and Preparing for Next...", "GameDebug")

        div_idx = self.active_game_state.game_data.get('current_div_index', -1)
        div_list = self.active_game_state.game_data.get('div_list', [])

        if 0 <= div_idx < len(div_list):
            self.active_game_state.game_data['div_list'][div_idx]['status'] = 'completed'
            self._display_in_chat(f"Div '{div_list[div_idx]['identifier']}' marked as completed.", "GameDebug")
        else:
            self._display_in_chat(f"Error: Invalid div index {div_idx} during finalization.", "Error")
            self.active_game_state.current_state_name = "END_GAME_FAILURE"
            return # Stop processing if error

        # Transition to CheckNextDiv is handled by the 'next_state' in the YAML choice definition.
        # This action's main job is to update the status of the div.

    def action_increment_div_index(self, **kwargs): # For "skip div" choice
        if not self.active_game_state: return
        self._display_in_chat("Action: User chose to skip current div.", "GameDebug")
        # The actual index increment and state transition to CheckNextDiv is handled by YAML.
        # This action could mark the div as 'skipped' if needed.
        div_idx = self.active_game_state.game_data.get('current_div_index', -1)
        div_list = self.active_game_state.game_data.get('div_list', [])
        if 0 <= div_idx < len(div_list):
            self.active_game_state.game_data['div_list'][div_idx]['status'] = 'skipped'
        pass


    def process_llm_response(self, llm_response_text: str):
        """
        Processes the LLM's response based on the current game state and choices.
        This is the core of the game turn logic.
        """
        if not self.active_game_state or not self.active_game_state.is_handshake_complete:
            self._display_in_chat("No active game or handshake not complete to process response.", "System")
            return

        self._display_in_chat(llm_response_text, "LLM")

        if not self.active_game_state: # Should not happen if called correctly
            print("Error: process_llm_response called with no active game.")
            return

        current_game_cfg = self.active_game_state.game_config
        current_state_name = self.active_game_state.current_state_name
        state_def = current_game_cfg.get("states", {}).get(current_state_name, {})

        if not state_def:
            self._display_in_chat(f"Error: State definition for '{current_state_name}' not found. Ending game.", "Error")
            self.end_game("state_definition_error_in_process_response")
            return

        # Determine if this state expects a choice ID or structured data (_data_input_)
        is_data_input_state = any(c.get("id") == "_data_input_" for c in state_def.get("choices", []))
        llm_choice_id = llm_response_text.strip().lower()

        next_major_state_name = None # This will hold the name of the state to transition to

        if is_data_input_state:
            # --- Handle Data Input State (e.g., for revisions) ---
            data_choice_def = next((c for c in state_def.get("choices", []) if c.get("id") == "_data_input_"), None)
            if not data_choice_def: # Should not happen if is_data_input_state is true
                self.end_game("internal_error_data_input_choice_missing")
                return

            parsed_data = None
            parsing_successful = False

            # Example parsing for "<revision>...</revision>"
            # This should be more flexible based on 'expected_response_structure' in YAML later.
            if "<revision>" in llm_response_text and "</revision>" in llm_response_text:
                match = re.search(r"<revision>(.*?)</revision>", llm_response_text, re.DOTALL)
                if match:
                    parsed_data = match.group(1).strip()
                    parsing_successful = True
                else: # Tags present but malformed, or empty
                    self.active_game_state.current_error_message = "Revision tags found, but content could not be extracted. Ensure content is between <revision> and </revision>."
            else:
                self.active_game_state.current_error_message = "Revision not provided in the expected <revision>...</revision> format."

            if parsing_successful:
                self.active_game_state.structured_response_attempts = 0 # Reset on success
                self.active_game_state.current_error_message = None

                action_name = data_choice_def.get("action")
                if action_name:
                    action_method = getattr(self, action_name, self._unknown_action)
                    # Pass the parsed data to the action method
                    action_method(revised_content=parsed_data)

                next_major_state_name = data_choice_def.get("next_state")
            else: # Parsing failed
                self.active_game_state.structured_response_attempts += 1
                max_retries = state_def.get("max_retries_for_structured_response", 1) # Default to 1 retry if not specified

                if self.active_game_state.structured_response_attempts >= max_retries:
                    self._display_in_chat(f"Maximum ({max_retries}) retries for structured response exceeded.", "Error")
                    self.active_game_state.current_error_message = f"Failed to get data in correct format after {max_retries} attempts. Please choose an option again."
                    next_major_state_name = state_def.get("default_next_state_on_invalid_choice", current_state_name) # Fallback
                    self.active_game_state.structured_response_attempts = 0 # Reset for the fallback state
                else:
                    # Re-prompt current data input state with error message already set
                    self._display_in_chat(f"Attempt {self.active_game_state.structured_response_attempts}/{max_retries}. Please try again.", "System")
                    next_major_state_name = current_state_name # Stay in current state to re-prompt

        else:
            # --- Handle Choice ID State ---
            selected_choice_def = None
            for choice in state_def.get("choices", []):
                if choice.get("id").lower() == llm_choice_id:
                    selected_choice_def = choice
                    break

            if selected_choice_def:
                self.active_game_state.invalid_choices_current_turn = 0 # Reset on valid choice
                self.active_game_state.current_error_message = None

                action_name = selected_choice_def.get("action")
                if action_name:
                    action_method = getattr(self, action_name, self._unknown_action)
                    action_method() # Call action, no specific data from LLM choice itself typically

                next_major_state_name = selected_choice_def.get("next_state")
            else: # Invalid choice ID
                self.active_game_state.invalid_choices_current_turn += 1
                self.active_game_state.total_invalid_choices += 1

                game_rules = current_game_cfg.get("game_rules", {})
                max_turn_errors = game_rules.get("max_invalid_choices_per_turn", 2)
                max_total_errors = game_rules.get("max_total_invalid_choices", 5)

                if self.active_game_state.invalid_choices_current_turn >= max_turn_errors or \
                   self.active_game_state.total_invalid_choices >= max_total_errors:
                    self._display_in_chat("Too many invalid choices. Ending game.", "Error")
                    self.end_game("too_many_invalid_choices")
                    return # Game ended

                self.active_game_state.current_error_message = f"Invalid choice: '{llm_response_text}'. Please select a valid option."
                next_major_state_name = state_def.get("default_next_state_on_invalid_choice", current_state_name)
                if next_major_state_name == "CURRENT_STATE": # Explicit YAML value
                    next_major_state_name = current_state_name


        # --- State Transition and Next Step ---
        if next_major_state_name:
            if next_major_state_name.startswith("END_GAME_"):
                self.end_game(reason=next_major_state_name)
            else:
                self.active_game_state.current_state_name = next_major_state_name
                self._execute_actions_for_current_state() # For the new state
                # If actions changed state again (e.g. auto-transitions), present_current_state_to_llm will handle it
                self.present_current_state_to_llm()
        else:
            # Should not happen if states are well-defined (always a next_state or END_GAME)
            self._display_in_chat(f"Error: No next state defined after processing response in state '{current_state_name}'. Ending game.", "Error")
            self.end_game("undefined_next_state_error")


    def present_current_state_to_llm(self):
        """
        Formats the prompt for the current game state and sends it to the LLM.
        Also displays the prompt in the chat panel.
        """
        if not self.active_game_state: # Game might have ended due to an action in _execute_actions_for_current_state
            return
        if not self.active_game_state.is_handshake_complete:
            # This should ideally not be reached if start_game handles handshake failure properly.
            self._display_in_chat("Cannot present state: Handshake not complete.", "Error")
            return

        current_config = self.active_game_state.game_config
        state_name = self.active_game_state.current_state_name

        # Handle terminal states first
        if state_name.startswith("END_GAME_"):
            self.end_game(reason=state_name)
            return

        state_def = current_config.get("states", {}).get(state_name)

        if not state_def:
            self._display_in_chat(f"Error: Current state '{state_name}' not defined in game config. Ending game.", "Error")
            self.end_game("state_definition_error")
            return

        # Populate placeholders in prompt_template
        prompt_template = state_def.get("prompt_template", "No prompt defined for this state.")

        # Populate placeholders in prompt_template
        formatted_prompt = prompt_template

        # 1. Populate data placeholders from game_data
        if self.active_game_state and self.active_game_state.game_data:
            for key, value in self.active_game_state.game_data.items():
                placeholder = f"{{{{{key}}}}}" # e.g. {{current_div_content}}
                # Ensure value is string for replacement, handle None gracefully
                str_value = str(value) if value is not None else ""
                formatted_prompt = formatted_prompt.replace(placeholder, str_value)

        # 2. Populate error message placeholder
        error_message_placeholder = "{{error_message_block_if_any}}"
        if self.active_game_state and self.active_game_state.current_error_message:
            # Format the error message (e.g., with HTML for color)
            # Assuming _display_in_chat handles HTML correctly if the message contains it.
            # Or, the template itself in YAML could have HTML around the placeholder.
            # For direct replacement, let's make it simple HTML.
            error_html_block = f"<div style='color: red; margin-bottom: 10px;'><b>Error:</b> {self.active_game_state.current_error_message}</div>"
            formatted_prompt = formatted_prompt.replace(error_message_placeholder, error_html_block)
            self.active_game_state.current_error_message = None # Clear after incorporating
        else:
            # If no error, remove the placeholder or replace with empty string
            formatted_prompt = formatted_prompt.replace(error_message_placeholder, "")

        # Ensure any other missed placeholders are removed or noted (e.g. {{EXAMPLE_UNDEFINED_PLACEHOLDER}})
        # This simple loop handles explicitly defined keys in game_data.
        # A more complex template engine could be used for advanced features like conditionals, loops if needed.
        # For now, remove any remaining {{...}} that weren't filled.
        formatted_prompt = re.sub(r"\{\{.*?\}\}", "[undefined_placeholder]", formatted_prompt)


        choices_text_parts = []
        is_data_input_state = False
        for choice in state_def.get("choices", []):
            if choice.get("id") == "_data_input_":
                is_data_input_state = True
                # Optionally add expected_response_structure to prompt if not already in template
                if choice.get("expected_response_structure") and choice.get("expected_response_structure") not in formatted_prompt:
                    formatted_prompt += f"\n\nFormat instructions: {choice.get('expected_response_structure')}"
                break # No other choices needed for data input state
            choices_text_parts.append(f"({choice.get('id')}) {choice.get('description')}")

        full_prompt_for_llm = formatted_prompt
        if not is_data_input_state and choices_text_parts:
             full_prompt_for_llm += "\n\nYour choices:\n" + "\n".join(choices_text_parts)
             full_prompt_for_llm += "\nPlease respond with the ID of your choice (e.g., 'a', '1')."
        elif not is_data_input_state and not choices_text_parts: # State has no choices and is not data input
            self._display_in_chat(f"Warning: State '{state_name}' has no actionable choices or data input defined. Check YAML.", "System")
            # This might be a dead-end state or an auto-transition state that didn't transition.
            # For now, we'll still display its prompt. It might be purely informational.


        self._display_in_chat(full_prompt_for_llm, "Game")

        # Only send to LLM if it's not a purely internal/informational state
        # (e.g., if there are choices for LLM or it's a data input state)
        if is_data_input_state or choices_text_parts:
            print(f"GameManager: Sending to LLM for state '{state_name}': {full_prompt_for_llm[:100]}...")
            # This is where the async nature will matter.
            # For now, assume generate_text is called, and the response is routed to process_llm_response
            # For synchronous test:
            # llm_response = self.llm_manager.generate_text(full_prompt_for_llm)
            # self.process_llm_response(llm_response)
            # This immediate call would make it hard for user to see the prompt.
            # In a real UI, this call is made, and we wait for LLM response.
            # The mock test in __main__ simulates this separation.
        else:
            print(f"GameManager: State '{state_name}' presented. No direct LLM interaction expected from this prompt.")
            # This could be a state that auto-transitions via on_enter_actions setting a new state
            # and then present_current_state_to_llm is called again.
            # Example: InitializeGame -> CheckNextDiv (if CheckNextDiv auto-runs and sets a new state)
            # Need to ensure _execute_actions_for_current_state can trigger state changes
            # and then re-call present_current_state_to_llm if needed.
            # For now, actions can change self.active_game_state.current_state_name.
            # The main game loop (not yet built) would call present_current_state_to_llm after actions.
            # In this step, we are just setting up.
            # If an action changes state, then `present_current_state_to_llm` should be called again *after* that action.
            # So, _execute_actions_for_current_state should probably return a flag if state changed,
            # or the main game loop handles this.
            # For now, if an action changes state, it should call present_current_state_to_llm itself. (Simpler for now)
            # Let's modify action_check_next_div to call present_current_state_to_llm if it transitions.

    def end_game(self, reason: str = "ended"):
        """
        Ends the current game, cleans up state, and re-enables chat input.
        """
        if not self.active_game_state:
            return

        self._display_in_chat(f"Game '{self.active_game_state.game_name}' ended. Reason: {reason}", "Game")
        # print(f"STUB: GameManager.end_game({reason}) called.") # Already printed by caller in test
        self.active_game_state = None
        if hasattr(self.chat_panel_ref, 'set_input_enabled'):
            self.chat_panel_ref.set_input_enabled(True)
        else:
            print("Warning: ChatPanel_ref missing set_input_enabled method.")


if __name__ == '__main__':
    from .config_manager import ConfigManager # Import for test block
    print("--- Testing GameManager (Initial Setup) ---")

    # Mock LLMManager for game_manager tests
    class MockLLMManagerForGameTest:
        def __init__(self):
            self.simulate_handshake_failure = False
            self.handshake_responses = 0
            self.expected_handshake_confirmation = "Understood. Ready to process divs." # From YAML

        def generate_text(self, prompt: str, provider: Optional[str] = None) -> str:
            print(f"MockLLMManagerForGameTest: Received prompt: '{prompt[:100]}...'")

            # Check for handshake prompt
            handshake_trigger_phrase = "To confirm you understand these rules" # From YAML
            if handshake_trigger_phrase in prompt:
                self.handshake_responses += 1
                if self.simulate_handshake_failure:
                    print("MockLLMManagerForGameTest: Simulating INCORRECT handshake response.")
                    return "I do not understand the rules."
                else:
                    print(f"MockLLMManagerForGameTest: Simulating CORRECT handshake response: '{self.expected_handshake_confirmation}'")
                    return self.expected_handshake_confirmation

            # Default response for other prompts (e.g., game turns)
            print("MockLLMManagerForGameTest: Simulating generic game turn response (e.g., 'a').")
            return "a" # Placeholder for game choices

    # Mock ChatPanel
    class MockChatPanel:
        def __init__(self):
            self.history: List[str] = []
            self.input_enabled: bool = True
            self.messages_from_game: List[Tuple[str, str, bool]] = []

        def add_message_from_game(self, sender: str, message: str, is_html: bool = False):
            log_message = f"MockChatPanel (from game): [{sender}] {message}"
            print(log_message)
            self.history.append(log_message)
            self.messages_from_game.append((sender, message, is_html))

        def display_llm_response(self, message: str): # Used by _display_in_chat fallback
            self.add_message_from_game("LLM", message)

        def display_user_message(self, message: str): # Fallback
             self.add_message_from_game("User", message)

        def display_system_message(self, message: str): # Fallback
             self.add_message_from_game("System", message)

        def set_input_enabled(self, enabled: bool):
            print(f"MockChatPanel: Input enabled set to: {enabled}")
            self.input_enabled = enabled

        def clear_history(self):
            self.history = []
            self.messages_from_game = []

    # Mock TextEditorArea
    class MockTextEditorArea:
        def __init__(self, initial_content=""):
            self.content = initial_content
        def get_current_document_content(self):
            print(f"MockTextEditorArea: Providing content: '{self.content[:50]}...'")
            return self.content
        def set_content(self, new_content: str):
            self.content = new_content

    # Mock ConfigManager (for project root finding, actual game configs loaded by GameConfigLoader)
    class MockConfigManager:
        def get_setting(self, key, default=None): return default # Not used by GameManager directly for games path yet
        def get_api_key(self, service_name): return "dummy_key"


    print("\n--- Test Scenario 1: Successful Handshake and Game Start ---")
    mock_llm_manager = MockLLMManagerForGameTest()
    mock_llm_manager.simulate_handshake_failure = False # Ensure success for this test
    mock_chat_panel = MockChatPanel()
    mock_text_editor = MockTextEditorArea()
    mock_config_manager = MockConfigManager() # For project root context

    # GameManager will try to load games from "cursor_clone_app/config/games"
    # For Scenario 1, set up editor content *before* creating GameManager or starting game
    # Ensure newlines are exactly as the regex expects.
    editor_content_s1 = (
        "::: div1 \n"  # Opening fence, name, space, newline
        "Content for div1.\n"
        "More content for div1.\n"
        ":::\n"          # Closing fence on its own line, followed by newline
        "\n"             # Blank line separator (optional, good for readability)
        "::: div2 \n"
        "Content for div2.\n"
        ":::\n"
    )
    mock_text_editor = MockTextEditorArea(initial_content=editor_content_s1)
    game_manager = GameManager(mock_llm_manager, mock_chat_panel, mock_text_editor, mock_config_manager)

    print("Listing available games...")
    available_games = game_manager.list_available_games()
    assert len(available_games) > 0, "No games loaded. Check GameConfigLoader and YAML paths."
    print(f"Available games: {[g[0] for g in available_games]}")

    game_to_test = "Markdown Div Editor"
    assert any(g[0] == game_to_test for g in available_games), f"Test game '{game_to_test}' not found."

    print(f"\nAttempting to start game '{game_to_test}' (expecting handshake success)...")
    # Chat input should be enabled before starting
    mock_chat_panel.set_input_enabled(True)
    start_success = game_manager.start_game(game_to_test)

    assert start_success is True, "GameManager.start_game() should return True on successful handshake."
    assert game_manager.active_game_state is not None, "Active game state should be set."
    assert game_manager.active_game_state.is_handshake_complete is True, "Handshake should be marked complete."
    # Input should be disabled by MainWindow normally, but GameManager doesn't do it directly.
    # MainWindow calls chat_panel.set_input_enabled(False) *before* calling start_game if game found.
    # For this direct test, we assume it would have been called.
    # Let's check if end_game re-enables it.
    print(f"Game started. Current state: {game_manager.active_game_state.current_state_name}")
    # Expected flow: InitializeGame -> (action) -> CheckNextDiv -> (action) -> SyntaxReviewStage_Prompt
    assert game_manager.active_game_state.current_state_name == "SyntaxReviewStage_Prompt", \
        f"Game did not reach 'SyntaxReviewStage_Prompt'. Current: {game_manager.active_game_state.current_state_name}"

    # Check if initial div data was loaded by action_initialize_div_editor_game (stubbed data)
    assert 'div_list' in game_manager.active_game_state.game_data, "Div list not found in game data."
    assert len(game_manager.active_game_state.game_data['div_list']) == 2, "Incorrect number of stubbed divs."
    assert game_manager.active_game_state.game_data['current_div_index'] == 0, "Incorrect current_div_index after init and first check."

    print("Successful handshake and game start test PASSED.")
    # Manually end game to reset for next test
    game_manager.end_game("test_scenario_1_complete")
    assert mock_chat_panel.input_enabled is True, "Chat input not re-enabled after game end."

    # --- Test Scenario 2: Failed Handshake (Testing with potentially live LLMManager if API key is bad/missing) ---
    print("\n--- Test Scenario 2: Failed Handshake (using actual LLMManager) ---")
    mock_chat_panel.clear_history()

    # Use the REAL LLMManager for this test to see how it handles API key issues or actual LLM non-confirmation
    # ConfigManager is already set up from Scenario 1 (mock_config_manager is fine as it points to correct file paths)
    # The actual .env file (cursor_clone_app/.env) will be read by ConfigManager.
    # If GEMINI_API_KEY is missing or invalid, LLMManager will fail to init/call, leading to handshake failure.
    # If key is valid, but LLM doesn't give exact confirmation, it will also fail.

    # Important: Create a new GameManager with the *actual* LLMManager
    # The config_manager used here (mock_config_manager) is just for pathing,
    # the actual LLMManager it instantiates will use ConfigManager() internally if not passed one,
    # or rather, LLMManager gets its ConfigManager from GameManager's constructor.
    # So, we need a ConfigManager that points to the real .env.

    real_config_manager_for_s2 = ConfigManager() # Reads actual cursor_clone_app/.env
    live_llm_manager_for_s2 = LLMManager(config_manager=real_config_manager_for_s2)

    # We need a new GameManager instance that uses this live_llm_manager
    game_manager_s2 = GameManager(live_llm_manager_for_s2, mock_chat_panel, mock_text_editor, real_config_manager_for_s2)
    # Ensure games are loaded for this new instance
    # Note: GameManager loads games in its __init__. If config/games path is standard, it's fine.

    print(f"Attempting to start game '{game_to_test}' with actual LLMManager (expecting handshake failure if key invalid or LLM non-compliant)...")
    mock_chat_panel.set_input_enabled(True)
    # For this test to check non-compliant LLM, temporarily change expected response in YAML if key IS valid
    # For now, assume key is missing/invalid, so LLMManager itself will cause failure.
    start_success_fail_scenario = game_manager_s2.start_game(game_to_test)

    assert start_success_fail_scenario is False, "GameManager.start_game() with actual LLMManager should return False on handshake failure (due to API key or non-compliance)."
    # When game_manager_s2 is used, its active_game_state will be None after failure.
    assert game_manager_s2.active_game_state is None, "Active game state for game_manager_s2 should be None after failed handshake."
    assert mock_chat_panel.input_enabled is True, "Chat input not re-enabled after failed handshake."

    # The number of attempts is visible in the logs from _perform_llm_handshake.
    # Verifying it programmatically here is tricky as live_llm_manager_for_s2 doesn't have a counter.
    # The key is that the handshake failed after trying.

    # Check chat history for failure messages
    recent_history_for_handshake_fail = mock_chat_panel.history[-3:] # Get messages around the failure point
    handshake_failed_msg_found = any("Handshake response incorrect" in msg for msg in recent_history_for_handshake_fail)
    assert handshake_failed_msg_found, "Handshake incorrect response message not found in recent chat history for failure test."

    recent_history_for_abort = mock_chat_panel.history[-2:] # Messages around game abort
    game_aborted_msg_found = any("Game aborted" in msg for msg in recent_history_for_abort)
    assert game_aborted_msg_found, "Game aborted message not found in recent chat history for failure test."

    print("Failed handshake test PASSED.")

    # --- Test Scenario 3: Partial Playthrough with valid choices and revisions ---
    print("\n--- Test Scenario 3: Partial Playthrough (Syntax Approve, Semantic Revise & Approve) ---")
    mock_chat_panel.clear_history()
    mock_llm_manager.simulate_handshake_failure = False # Successful handshake
    mock_llm_manager.handshake_responses = 0

    # Setup editor content for this test
    editor_content_div_editor = """
::: intro
This is the intro div.
It needs some work.
:::

::: body_paragraph
This is the body. It is quite good.
:::
    """
    mock_text_editor.set_content(editor_content_div_editor)

    game_manager = GameManager(mock_llm_manager, mock_chat_panel, mock_text_editor, mock_config_manager) # Re-init for fresh game state

    print(f"Attempting to start game '{game_to_test}' for playthrough...")
    start_success = game_manager.start_game(game_to_test)
    assert start_success, "Game start failed for playthrough test."
    assert game_manager.active_game_state.current_state_name == "SyntaxReviewStage_Prompt", "Not at SyntaxReviewStage_Prompt."
    assert game_manager.active_game_state.game_data['current_div_identifier'] == "intro", "Not processing 'intro' div first."

    # 1. Div 1: Approve Syntax
    print("\nPlaythrough: Div 1 - Approving Syntax...")
    mock_llm_manager.generate_text = lambda prompt: "b" # LLM chooses 'b' (approve syntax)
    game_manager.process_llm_response("b")
    assert game_manager.active_game_state.current_state_name == "SemanticReviewStage_Prompt", "Failed to reach SemanticReviewStage_Prompt for Div 1."
    assert "Semantic Review for Div 'intro'" in mock_chat_panel.history[-1], "Prompt for semantic review of intro not shown."

    # 2. Div 1: Choose to Revise Semantics
    print("\nPlaythrough: Div 1 - Choosing to Revise Semantics...")
    mock_llm_manager.generate_text = lambda prompt: "a" # LLM chooses 'a' (revise semantics)
    game_manager.process_llm_response("a")
    assert game_manager.active_game_state.current_state_name == "SemanticReviewStage_WaitForRevision", "Failed to reach SemanticReviewStage_WaitForRevision for Div 1."
    assert "provide the complete revised content" in mock_chat_panel.history[-1], "Prompt for semantic revision not shown."

    # 3. Div 1: Provide Semantic Revision (Correct Format)
    print("\nPlaythrough: Div 1 - Providing Semantic Revision...")
    revised_div1_content = "This is the revised intro. It is now much better."
    mock_llm_manager.generate_text = lambda prompt: f"<revision>{revised_div1_content}</revision>"
    game_manager.process_llm_response(f"<revision>{revised_div1_content}</revision>")
    assert game_manager.active_game_state.current_state_name == "SemanticReviewStage_Prompt", "Failed to return to SemanticReviewStage_Prompt after revision for Div 1."
    assert revised_div1_content in game_manager.active_game_state.game_data['div_list'][0]['current_content'], "Div 1 content not updated with revision."
    assert revised_div1_content in mock_chat_panel.history[-1], "Revised content not shown in prompt after revision."

    # 4. Div 1: Approve Semantics
    print("\nPlaythrough: Div 1 - Approving Semantics...")
    mock_llm_manager.generate_text = lambda prompt: "b" # LLM chooses 'b' (approve div)
    game_manager.process_llm_response("b")
    assert game_manager.active_game_state.game_data['div_list'][0]['status'] == 'completed', "Div 1 status not 'completed'."
    # Should now be at SyntaxReviewStage_Prompt for Div 2 ('body_paragraph')
    assert game_manager.active_game_state.current_state_name == "SyntaxReviewStage_Prompt", "Failed to reach SyntaxReviewStage_Prompt for Div 2."
    assert game_manager.active_game_state.game_data['current_div_identifier'] == "body_paragraph", "Not processing 'body_paragraph' div after first div."
    assert "Syntax Review for Div 'body_paragraph'" in mock_chat_panel.history[-1], "Prompt for syntax review of body_paragraph not shown."

    print("Partial playthrough test (Div 1 syntax approve, semantic revise & approve) PASSED.")
    game_manager.end_game("test_scenario_3_complete")


    # --- Test Scenario 4: Invalid Choice and Max Rule Breaks ---
    print("\n--- Test Scenario 4: Invalid Choice & Max Rule Breaks ---")
    mock_chat_panel.clear_history()
    # Reset LLM manager for a clean state and default handshake behavior
    mock_llm_manager = MockLLMManagerForGameTest()
    mock_llm_manager.simulate_handshake_failure = False

    mock_text_editor.set_content("::: only_div\nContent here.\n:::") # Simple content for this test
    # Re-init game_manager to use the fresh mock_llm_manager
    game_manager = GameManager(mock_llm_manager, mock_chat_panel, mock_text_editor, mock_config_manager)

    print("Starting game for invalid choice test...")
    start_success_s4 = game_manager.start_game(game_to_test)
    assert start_success_s4, "Game failed to start for Scenario 4"
    assert game_manager.active_game_state is not None, "Game state is None after starting for Scenario 4"
    assert game_manager.active_game_state.current_state_name == "SyntaxReviewStage_Prompt", \
        f"Scenario 4 did not reach SyntaxReviewStage_Prompt. Current: {game_manager.active_game_state.current_state_name}"

    # Max total invalid choices is 5 (from YAML)
    print("Testing invalid choices leading to game end...")
    mock_llm_manager.generate_text = lambda prompt: "x" # Invalid choice
    for i in range(5):
        print(f"Submitting invalid choice attempt {i+1}")
        game_manager.process_llm_response("x")
        if game_manager.active_game_state is None: # Game ended
            break

    assert game_manager.active_game_state is None, "Game should have ended due to max_total_invalid_choices."
    assert any("Too many invalid choices. Ending game." in msg for msg in mock_chat_panel.history), "Game end message for invalid choices not found."
    assert mock_chat_panel.input_enabled is True, "Chat input not re-enabled after game end due to rule breaks."
    print("Invalid choice and max rule breaks test PASSED.")

    # --- Test Scenario 5: Incorrect Revision Format and Max Retries ---
    print("\n--- Test Scenario 5: Incorrect Revision Format & Max Retries ---")
    mock_chat_panel.clear_history()
    mock_llm_manager = MockLLMManagerForGameTest() # Fresh mock
    mock_llm_manager.simulate_handshake_failure = False

    mock_text_editor.set_content("::: another_div\nRevise me.\n:::")
    game_manager = GameManager(mock_llm_manager, mock_chat_panel, mock_text_editor, mock_config_manager) # Re-init

    print("Starting game for incorrect revision format test...")
    start_success_s5 = game_manager.start_game(game_to_test)
    assert start_success_s5, "Game failed to start for Scenario 5"
    assert game_manager.active_game_state is not None, "Game state is None after starting for Scenario 5"
    assert game_manager.active_game_state.current_state_name == "SyntaxReviewStage_Prompt", \
        f"Scenario 5 did not reach SyntaxReviewStage_Prompt. Current: {game_manager.active_game_state.current_state_name}"

    # Choose to revise ('a')
    print("Choosing to revise...")
    # For this turn, LLM should respond 'a'. generate_text default is 'a', so it's fine.
    # Or be explicit: mock_llm_manager.generate_text = lambda prompt: "a"
    original_generate_text_method = mock_llm_manager.generate_text # Save default
    mock_llm_manager.generate_text = lambda p: "a" if "SyntaxReviewStage_Prompt" in p else original_generate_text_method(p)

    game_manager.process_llm_response("a") # LLM chooses 'a'
    assert game_manager.active_game_state.current_state_name == "SyntaxReviewStage_WaitForRevision", \
        f"Not in WaitForRevision. Current: {game_manager.active_game_state.current_state_name}"

    # Max retries for structured response is 2 (from YAML for SyntaxReviewStage_WaitForRevision)
    print("Testing incorrect revision format leading to fallback...")
    mock_llm_manager.generate_text = lambda prompt: "this is not in tags"
    for i in range(2): # max_retries_for_structured_response: 2
        print(f"Submitting incorrect revision format attempt {i+1}")
        game_manager.process_llm_response("this is not in tags")
        if game_manager.active_game_state.current_state_name != "SyntaxReviewStage_WaitForRevision":
            break # No longer in wait state, means fallback occurred or game ended

    assert game_manager.active_game_state.current_state_name == "SyntaxReviewStage_Prompt", \
        f"Should have fallen back to SyntaxReviewStage_Prompt. Is: {game_manager.active_game_state.current_state_name}"
    assert any("Failed to get data in correct format after 2 attempts" in msg for msg in mock_chat_panel.history), \
        "Fallback message after max revision retries not found."
    print("Incorrect revision format and max retries test PASSED.")

    print("\n--- GameManager Core Logic tests complete ---")
