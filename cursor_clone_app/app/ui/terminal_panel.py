from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextBrowser, QLineEdit,
                               QPushButton, QHBoxLayout, QApplication, QLabel)
from PySide6.QtCore import Qt

class TerminalPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0) # Small top margin
        self.setLayout(self.layout)

        self.output_view = QTextBrowser()
        self.output_view.setReadOnly(True)
        self.output_view.setPlaceholderText("Terminal output will appear here...")
        # Monospaced font is typical for terminals
        font = self.output_view.font()
        font.setFamily("Monospace") # Or Courier, etc.
        font.setPointSize(9) # Terminals often use slightly smaller fonts
        self.output_view.setFont(font)
        self.output_view.setStyleSheet("QTextBrowser { background-color: #2B2B2B; color: #D0D0D0; border: 1px solid #444; }")


        self.input_area_layout = QHBoxLayout()
        self.prompt_label = QLabel(">$") # Simple prompt
        self.prompt_label.setFont(font) # Match font
        self.prompt_label.setStyleSheet("QLabel { color: #77DD77; background-color: #2B2B2B; padding-left: 3px; }")


        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command (currently non-functional)...")
        self.command_input.returnPressed.connect(self.handle_command_entered)
        self.command_input.setFont(font) # Match font
        self.command_input.setStyleSheet("QLineEdit { background-color: #2B2B2B; color: #D0D0D0; border: none; }")


        self.input_area_layout.addWidget(self.prompt_label)
        self.input_area_layout.addWidget(self.command_input, 1) # Command input takes available space

        self.layout.addWidget(self.output_view, 1) # Output view takes most space
        self.layout.addLayout(self.input_area_layout)

        self.append_output("Pseudo-Terminal Initialized. Type 'help' for a mock command list.")
        self.mock_commands = {
            "help": "Available mock commands: help, date, status, clear",
            "date": lambda: f"Current mock date: {QApplication.instance().applicationName()} internal clock (not real date).", # Placeholder
            "status": "System status: All mock systems nominal.",
            "clear": self.clear_output
        }

    def handle_command_entered(self):
        command = self.command_input.text().strip()
        if not command:
            return

        self.append_output(f"<font color='#66B2FF'>&gt;$ {command}</font>") # Echo command with different color

        if command in self.mock_commands:
            if callable(self.mock_commands[command]):
                if command == "clear":
                    self.mock_commands[command]()
                else:
                    self.append_output(self.mock_commands[command]())
            else:
                self.append_output(self.mock_commands[command])
        elif command:
            self.append_output(f"Mock command not found: {command}")

        self.command_input.clear()
        self.command_input.setFocus()

    def append_output(self, text):
        self.output_view.append(text)
        self.output_view.verticalScrollBar().setValue(self.output_view.verticalScrollBar().maximum())

    def clear_output(self):
        self.output_view.clear()
        # self.append_output("Pseudo-Terminal Initialized. Type 'help' for a mock command list.")


# Simple test
if __name__ == '__main__':
    import sys
    import qdarkstyle

    app = QApplication(sys.argv)
    # Don't apply qdarkstyle here if the component has its own specific dark theme
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))

    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)

    terminal_panel = TerminalPanel()
    main_layout.addWidget(terminal_panel)

    main_widget.setWindowTitle("Terminal Panel Test")
    main_widget.setGeometry(300, 300, 700, 300)
    main_widget.show()

    sys.exit(app.exec())
