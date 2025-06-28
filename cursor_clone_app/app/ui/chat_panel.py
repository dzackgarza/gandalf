from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextBrowser, QPlainTextEdit,
                               QPushButton, QHBoxLayout, QApplication, QLabel, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QTextCursor

class ChatInputTextEdit(QPlainTextEdit):
    """Custom QPlainTextEdit to handle Shift+Enter for newline and Enter for send."""
    send_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(self.fontMetrics().height() * 4) # Approx 3 lines + padding

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if event.modifiers() == Qt.ShiftModifier:
                # Shift + Enter: insert newline
                super().keyPressEvent(event)
            else:
                # Enter: emit send signal and don't insert newline
                self.send_signal.emit()
                event.accept() # Consume the event
                return
        else:
            super().keyPressEvent(event)


class ChatPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.history_view = QTextBrowser()
        self.history_view.setReadOnly(True)
        self.history_view.setOpenExternalLinks(True) # For markdown links if rendered as HTML
        # self.history_view.setStyleSheet("QTextBrowser { font-size: 10pt; }")

        self.input_text = ChatInputTextEdit()
        self.input_text.setPlaceholderText("Type your message...")
        self.input_text.send_signal.connect(self.handle_send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.handle_send_message)

        self.start_game_button = QPushButton("Start Game")
        # self.start_game_button.clicked.connect(self.handle_start_game_request) # Will be connected by MainWindow

        input_controls_layout = QHBoxLayout()
        input_controls_layout.addWidget(self.start_game_button)
        input_controls_layout.addStretch() # Pushes send button to the right if desired, or remove for compact

        # Layout for input text and send button
        text_send_layout = QHBoxLayout()
        text_send_layout.addWidget(self.input_text, 1) # Input text takes most space
        text_send_layout.addWidget(self.send_button)

        main_v_layout = QVBoxLayout()
        main_v_layout.addLayout(input_controls_layout) # Game button and other controls
        main_v_layout.addLayout(text_send_layout)    # Input text and send button

        self.layout.addWidget(self.history_view, 1) # History view takes stretch factor 1
        self.layout.addLayout(main_v_layout) # Add the combined input area layout

    def set_input_enabled(self, enabled: bool):
        """Enables or disables the chat input field and send button."""
        self.input_text.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        if enabled:
            self.input_text.setPlaceholderText("Type your message...")
            self.input_text.setFocus()
        else:
            self.input_text.setPlaceholderText("Chat input disabled during game.")

    def add_message_from_game(self, sender: str, message: str, is_html: bool = False):
        """Appends a message from the game system or LLM to the history view."""
        # Simple HTML escaping for non-HTML messages to prevent accidental rendering
        if not is_html:
            message = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        formatted_message = f"<b>{sender}:</b> {message}"

        # Use different colors for different senders for clarity
        if sender.lower() == "game":
            formatted_message = f"<font color='#DAA520'><b>{sender}:</b></font><br>{message}" # Goldenrod for Game
        elif sender.lower() == "system" or sender.lower() == "error":
            formatted_message = f"<font color='#FF6347'><b>{sender}:</b></font><br>{message}" # Tomato for System/Error
        elif sender.lower() == "llm":
             formatted_message = f"<font color='#77DD77'><b>{sender}:</b></font><br>{message}" # Already used for LLM

        self.history_view.append(formatted_message + "<br>") # Add extra space after message
        self.history_view.moveCursor(QTextCursor.End)


    def handle_send_message(self):
        user_message = self.input_text.toPlainText().strip()
        if not user_message:
            return

        # Append user message to history (basic formatting)
        # For markdown support, one might use:
        # self.history_view.append(f"<div style='color: #A0A0FF;'><b>You:</b></div>\n{user_message_html_escaped}")
        # Or convert markdown to HTML before appending. For now, plain text.
        self.history_view.append(f"<b>You:</b> {user_message}\n")

        # TODO: Send message to LLM and display response
        self.display_llm_response(f"LLM: Echoing '{user_message}' (placeholder response).")

        self.input_text.clear()
        self.input_text.setFocus()

    def display_user_message(self, message):
        # Could be used if message is added externally
        self.history_view.append(f"<b>You:</b> {message}\n")

    def display_llm_response(self, message):
        # For now, LLM responses are also just appended.
        # Markdown could be handled here.
        self.history_view.append(f"<font color='#77DD77'><b>LLM:</b></font> {message}\n")
        # Scroll to the bottom
        self.history_view.verticalScrollBar().setValue(self.history_view.verticalScrollBar().maximum())


# Simple test
if __name__ == '__main__':
    import sys
    import qdarkstyle

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))

    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)

    chat_panel = ChatPanel()
    main_layout.addWidget(chat_panel)

    main_widget.setWindowTitle("Chat Panel Test")
    main_widget.setGeometry(300, 300, 400, 600)
    main_widget.show()

    chat_panel.display_user_message("Hello LLM, how are you?")
    chat_panel.display_llm_response("I am a placeholder LLM, doing great! Thanks for asking.")

    sys.exit(app.exec())
