import sys
import os
from PySide6.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout,
                               QLabel, QSplitter, QSizePolicy, QMessageBox, QInputDialog)
from PySide6.QtCore import Qt
import qdarkstyle

from cursor_clone_app.app.ui.text_editor import TextEditorArea
from cursor_clone_app.app.ui.chat_panel import ChatPanel
from cursor_clone_app.app.ui.terminal_panel import TerminalPanel

# Core components
from cursor_clone_app.app.core.config_manager import ConfigManager
from cursor_clone_app.app.core.llm_manager import LLMManager
from cursor_clone_app.app.core.game_manager import GameManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cursor Clone App")
        self.setGeometry(100, 100, 1200, 800) # x, y, width, height

        # Initialize core managers
        # ConfigManager is needed by LLMManager and GameManager (for project root)
        self.config_manager = ConfigManager()
        self.llm_manager = LLMManager(config_manager=self.config_manager)

        # UI elements are initialized in init_ui, so GameManager needs them passed after.
        # We will instantiate GameManager in init_ui after chat_panel and text_editor_area are created.
        self.game_manager = None

        self.init_ui() # This will also set up self.game_manager
        self.load_initial_file()

    def init_ui(self):
        # Top horizontal splitter for Text Editor and Chat Panel
        self.h_splitter = QSplitter(Qt.Horizontal)

        self.text_editor_area = TextEditorArea(parent=self)
        self.text_editor_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.h_splitter.addWidget(self.text_editor_area)

        self.chat_panel = ChatPanel(parent=self)
        self.chat_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.h_splitter.addWidget(self.chat_panel)

        self.h_splitter.setStretchFactor(0, 7)
        self.h_splitter.setStretchFactor(1, 3)
        # self.h_splitter.setSizes([750, 450]) # Initial sizes for editor and chat

        # Main vertical splitter: top is h_splitter, bottom is terminal_panel
        self.main_v_splitter = QSplitter(Qt.Vertical)

        self.main_v_splitter.addWidget(self.h_splitter) # Add the editor/chat splitter to the top

        # Terminal Panel
        self.terminal_panel = TerminalPanel(parent=self)
        self.terminal_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_v_splitter.addWidget(self.terminal_panel) # Add terminal to the bottom

        # Set initial sizes for the vertical splitter (e.g., 75% for editor/chat, 25% for terminal)
        self.main_v_splitter.setStretchFactor(0, 3) # Editor/Chat area gets 3 parts
        self.main_v_splitter.setStretchFactor(1, 1) # Terminal area gets 1 part
        # self.main_v_splitter.setSizes([600, 200]) # Initial heights for top and bottom areas

        # Set the main vertical splitter as the central widget
        self.setCentralWidget(self.main_v_splitter)

        self.statusBar().showMessage("Ready")

        # Instantiate GameManager now that UI refs are available
        self.game_manager = GameManager(
            llm_manager=self.llm_manager,
            chat_panel_ref=self.chat_panel,
            text_editor_ref=self.text_editor_area,
            config_manager_ref=self.config_manager
        )

        # Connect ChatPanel's "Start Game" button
        if hasattr(self.chat_panel, 'start_game_button'):
            self.chat_panel.start_game_button.clicked.connect(self.handle_start_game_request)
        else:
            print("Warning: ChatPanel does not have 'start_game_button'. Game initiation UI might be missing.")


    def handle_start_game_request(self):
        if not self.game_manager:
            QMessageBox.critical(self, "Error", "GameManager is not initialized.")
            return

        available_games = self.game_manager.list_available_games()

        if not available_games:
            QMessageBox.information(self, "No Games", "No games are currently available.")
            return

        game_to_start = None
        if len(available_games) == 1:
            game_name, game_desc = available_games[0]
            reply = QMessageBox.question(self, "Start Game?",
                                         f"Start '{game_name}'?\n\n{game_desc}",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                game_to_start = game_name
        else:
            game_names = [f"{name} - {desc}" for name, desc in available_games]
            item, ok = QInputDialog.getItem(self, "Select Game",
                                            "Choose a game to start:", game_names, 0, False)
            if ok and item:
                # Extract the actual game name (before " - ")
                game_to_start = item.split(" - ")[0]

        if game_to_start:
            self.statusBar().showMessage(f"Attempting to start game: {game_to_start}...")
            # Disable chat input immediately, game manager will re-enable if handshake fails or game ends.
            self.chat_panel.set_input_enabled(False)

            # GameManager.start_game will handle actual start and further UI updates via ChatPanel
            # It returns True if handshake initiated, False if game not found or already active.
            # The actual success of starting (handshake) is handled asynchronously or internally by GameManager.
            if not self.game_manager.start_game(game_to_start):
                # If start_game itself immediately fails (e.g. game not found, though filtered above)
                self.chat_panel.set_input_enabled(True)
                self.statusBar().showMessage(f"Failed to initiate game: {game_to_start}.", 5000)


    def load_initial_file(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(os.path.dirname(script_dir))

            initial_file_path = os.path.join(base_dir, "corpus", "sample1.txt")

            if os.path.exists(initial_file_path):
                self.text_editor_area.refactor_add_new_tab(filepath=initial_file_path)
            else:
                self.statusBar().showMessage(f"Initial file not found: {initial_file_path}. Creating empty tab.", 5000)
                self.text_editor_area.refactor_add_new_tab(title="Untitled")
        except Exception as e:
            self.statusBar().showMessage(f"Error determining initial file path: {e}", 5000)
            self.text_editor_area.refactor_add_new_tab(title="Untitled (Error)")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        # Apply QDarkStyle globally. TerminalPanel has its own specific styling for its content area.
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
    except Exception as e:
        print(f"Could not load QDarkStyle: {e}. Using default style.")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
