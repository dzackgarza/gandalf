import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QPlainTextEdit,
                               QFileDialog, QPushButton, QHBoxLayout, QApplication, QMessageBox)
from PySide6.QtCore import Qt, QFileInfo

class TextEditorArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent # To access main window methods like statusBar
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Store filepaths associated with each tab's editor
        self.tab_filepaths = {} # Maps tab index to filepath string
        # Store modification status
        self.tab_modified_status = {} # Maps tab index to boolean

        self.layout.addWidget(self.tab_widget)

        # Button bar for actions
        button_layout = QHBoxLayout()
        self.new_button = QPushButton("New Tab")
        self.new_button.clicked.connect(lambda: self.add_new_tab(title="Untitled"))
        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open_file_dialog)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_current_file)
        self.save_as_button = QPushButton("Save As")
        self.save_as_button.clicked.connect(self.save_file_as_dialog)

        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.save_as_button)
        button_layout.addStretch()
        self.layout.addLayout(button_layout)

    def _get_editor_for_tab_index(self, index):
        if index < 0 or index >= self.tab_widget.count():
            return None
        widget = self.tab_widget.widget(index)
        if isinstance(widget, QPlainTextEdit):
            return widget
        # If tabs contain a wrapper widget, adjust accordingly
        # For now, assuming direct QPlainTextEdit
        editors = widget.findChildren(QPlainTextEdit)
        if editors:
            return editors[0]
        return None

    def _update_tab_title(self, index, filepath=None):
        editor = self._get_editor_for_tab_index(index)
        if not editor:
            return

        base_title = "Untitled"
        if filepath:
            base_title = QFileInfo(filepath).fileName()

        is_modified = self.tab_modified_status.get(index, False)
        title = base_title + ("*" if is_modified else "")
        self.tab_widget.setTabText(index, title)

    def _mark_tab_as_modified(self, index, modified=True):
        self.tab_modified_status[index] = modified
        filepath = self.tab_filepaths.get(index)
        self._update_tab_title(index, filepath)

    def add_new_tab(self, filepath=None, content="", title="Untitled", set_current=True):
        editor = QPlainTextEdit()
        editor.setPlaceholderText("Start typing or open a file...")
        # editor.setStyleSheet("QPlainTextEdit { font-family: 'Monospace'; font-size: 11pt; }") # Example styling

        current_index = self.tab_widget.addTab(editor, title)
        self.tab_filepaths[current_index] = filepath
        self.tab_modified_status[current_index] = False # New tabs are not modified initially

        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                editor.setPlainText(content)
                self._update_tab_title(current_index, filepath)
                if self.parent_window and hasattr(self.parent_window, 'statusBar'):
                    self.parent_window.statusBar().showMessage(f"Opened: {filepath}", 3000)
            except Exception as e:
                QMessageBox.warning(self, "Error Opening File", f"Could not open file: {filepath}\n{str(e)}")
                # Keep the tab open but untitled and empty if file read fails
                self.tab_filepaths[current_index] = None
                self._update_tab_title(current_index, None)
        else:
            editor.setPlainText(content)
            self._update_tab_title(current_index, None)


        # Connect textChanged signal to mark tab as modified
        # Need to be careful with lambda to capture correct index if tabs are reordered later
        # For now, this works if we get the current index when textChanged fires
        editor.textChanged.connect(lambda: self._mark_tab_as_modified(self.tab_widget.currentIndex()))


        if set_current:
            self.tab_widget.setCurrentWidget(editor)

        return editor

    def open_file_dialog(self):
        # Use current tab's directory if available, otherwise home directory
        current_editor_index = self.tab_widget.currentIndex()
        start_dir = os.path.expanduser("~")
        if current_editor_index != -1:
            current_filepath = self.tab_filepaths.get(current_editor_index)
            if current_filepath:
                start_dir = QFileInfo(current_filepath).absolutePath()

        filepath, _ = QFileDialog.getOpenFileName(self, "Open File", start_dir,
                                                  "Text Files (*.txt *.md *.py *.json *.yaml *.html *.css *.js);;All Files (*)")
        if filepath:
            # Check if file is already open
            for i in range(self.tab_widget.count()):
                if self.tab_filepaths.get(i) == filepath:
                    self.tab_widget.setCurrentIndex(i)
                    return
            self.add_new_tab(filepath=filepath)

    def save_current_file(self):
        current_index = self.tab_widget.currentIndex()
        if current_index == -1:
            return False # No tab open

        editor = self._get_editor_for_tab_index(current_index)
        if not editor:
            return False

        filepath = self.tab_filepaths.get(current_index)
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                self._mark_tab_as_modified(current_index, False) # Reset modified status
                if self.parent_window and hasattr(self.parent_window, 'statusBar'):
                    self.parent_window.statusBar().showMessage(f"Saved: {filepath}", 3000)
                return True
            except Exception as e:
                QMessageBox.warning(self, "Error Saving File", f"Could not save file: {filepath}\n{str(e)}")
                return False
        else:
            return self.save_file_as_dialog() # No filepath associated, so "Save As"

    def save_file_as_dialog(self):
        current_index = self.tab_widget.currentIndex()
        if current_index == -1:
            return False

        editor = self._get_editor_for_tab_index(current_index)
        if not editor:
            return False

        # Suggest current filename if available, otherwise "untitled.txt"
        current_filepath = self.tab_filepaths.get(current_index)
        suggested_name = QFileInfo(current_filepath).fileName() if current_filepath else "untitled.txt"
        start_dir = QFileInfo(current_filepath).absolutePath() if current_filepath else os.path.expanduser("~")

        filepath, _ = QFileDialog.getSaveFileName(self, "Save File As",
                                                  os.path.join(start_dir, suggested_name),
                                                  "Text Files (*.txt *.md *.py *.json *.yaml);;All Files (*)")
        if filepath:
            self.tab_filepaths[current_index] = filepath
            self._update_tab_title(current_index, filepath) # Update title with new name
            return self.save_current_file() # Now call save_current_file which will use the new path
        return False

    def close_tab(self, index):
        editor = self._get_editor_for_tab_index(index)
        if not editor:
            self.tab_widget.removeTab(index)
            self._cleanup_tab_data(index)
            return

        if self.tab_modified_status.get(index, False):
            filepath = self.tab_filepaths.get(index)
            filename = QFileInfo(filepath).fileName() if filepath else "Untitled"

            reply = QMessageBox.question(self, "Save Changes?",
                                         f"'{filename}' has been modified. Save changes?",
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if reply == QMessageBox.Save:
                if not self.save_current_file(): # if save failed (e.g. user cancelled save_as)
                    return # Don't close tab
            elif reply == QMessageBox.Cancel:
                return # Don't close tab
            # If Discard, proceed to close

        self.tab_widget.removeTab(index)
        self._cleanup_tab_data(index)

        # Update status bar
        if self.parent_window and hasattr(self.parent_window, 'statusBar'):
            self.parent_window.statusBar().showMessage(f"Closed tab: {self.tab_widget.tabText(index)}", 3000)


    def _cleanup_tab_data(self, closed_index):
        """Adjust stored filepaths and modification status after a tab is closed."""
        new_filepaths = {}
        new_modified_status = {}

        for i in range(self.tab_widget.count()): # Iterate over remaining tabs
            # The widget at index `i` was originally at some `old_index`
            # This is tricky because QTabWidget doesn't directly give old indices.
            # A simpler, though potentially less robust way if tabs are complex,
            # is to rebuild based on current widgets.
            # For now, let's assume indices shift predictably.
            # This part needs to be more robust if tab reordering is implemented.
            # A safer way: associate data with the editor widget itself, not the index.

            # Simplified approach: if closed_index was not the last one, indices shift.
            # This is not fully robust. A better way is to store data keyed by the editor widget itself.
            # For now, this is a placeholder for a more robust solution.
            # Let's try to re-key based on current widget object if possible, or re-evaluate this.

            # The current implementation stores filepath in self.tab_filepaths[original_index_at_creation]
            # When a tab is closed, tab indices shift. This will break the mapping.
            # A better approach:
            # self.tab_data = {editor_widget: {"filepath": path, "modified": False}}
            # Then iterate self.tab_widget.widget(i) to get editor_widget.

            # For now, let's clear and rebuild, which is inefficient but safer than complex index math.
            # This will be slow if there are many tabs.
            pass # The current implementation of getting editor and its path is via currentIndex.
                 # When a tab is removed, the indices of subsequent tabs change.
                 # The self.tab_filepaths and self.tab_modified_status dictionaries
                 # need to be updated to reflect these new indices.

        # Correct way to handle data after tab removal:
        # Rebuild the dictionaries based on the current state of tab_widget
        temp_filepaths = self.tab_filepaths.copy()
        temp_modified_status = self.tab_modified_status.copy()

        self.tab_filepaths.clear()
        self.tab_modified_status.clear()

        for i in range(self.tab_widget.count()):
            editor_widget = self.tab_widget.widget(i) # This is the QPlainTextEdit
            # We need to find which original_index this editor_widget corresponded to.
            # This is the fundamental problem with index-based storage if not managed carefully.

            # Let's find this editor in the old data (this is inefficient)
            # A better way is to store filepath directly on the editor widget using setProperty
            original_index_found = None
            for old_idx, old_editor in enumerate(temp_filepaths.keys()): # This is wrong, keys are indices
                # This whole _cleanup_tab_data is flawed because self.tab_filepaths keys are indices.
                # Let's simplify: when a tab is closed, its entry is just removed.
                # The real issue is that add_new_tab's textChanged.connect lambda captures currentIndex()
                # at the moment of connection, not at the moment of firing.
                pass # This simplified cleanup is not enough.

        # The textChanged connection MUST be fixed.
        # editor.textChanged.connect(lambda editor=editor: self._handle_text_changed(editor))
        # def _handle_text_changed(self, editor_instance):
        #   index = self.tab_widget.indexOf(editor_instance)
        #   if index != -1: self._mark_tab_as_modified(index)

        # For now, the close_tab will just remove the entry from the dict if found by old index.
        # This is still buggy.
        if closed_index in self.tab_filepaths:
            del self.tab_filepaths[closed_index]
        if closed_index in self.tab_modified_status:
            del self.tab_modified_status[closed_index]

        # The proper fix for data management:
        # 1. When adding a tab, store filepath and modified status as properties of the editor widget itself.
        #    editor.setProperty("filepath", filepath)
        #    editor.setProperty("modified", False)
        # 2. In textChanged, get the sender() which is the editor, then update its "modified" property.
        #    editor = self.sender()
        #    editor.setProperty("modified", True)
        #    index = self.tab_widget.indexOf(editor)
        #    self._update_tab_title(index, editor.property("filepath"))
        # 3. In save/open/close, get current editor, then get/set its properties.
        # This avoids index-based dictionary management hell.
        # I will refactor to this property-based approach.

    def refactor_add_new_tab(self, filepath=None, content="", title="Untitled", set_current=True):
        editor = QPlainTextEdit()
        editor.setPlaceholderText("Start typing or open a file...")
        # editor.setStyleSheet("QPlainTextEdit { font-family: 'Monospace'; font-size: 11pt; }")

        editor.setProperty("filepath", filepath)
        editor.setProperty("modified", False)
        editor.setProperty("original_content_on_load", "") # For checking if modified from disk version

        tab_title = title
        if filepath:
            tab_title = QFileInfo(filepath).fileName()
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                editor.setPlainText(content)
                editor.setProperty("original_content_on_load", content)
                if self.parent_window and hasattr(self.parent_window, 'statusBar'):
                    self.parent_window.statusBar().showMessage(f"Opened: {filepath}", 3000)
            except Exception as e:
                QMessageBox.warning(self, "Error Opening File", f"Could not open file: {filepath}\n{str(e)}")
                editor.setProperty("filepath", None) # Clear filepath if open failed
                tab_title = "Untitled" # Reset title
                content = "" # Ensure content is empty
                editor.setPlainText(content)
                editor.setProperty("original_content_on_load", content)

        else: # No filepath provided, new untitled tab
            editor.setPlainText(content)
            editor.setProperty("original_content_on_load", content)


        current_index = self.tab_widget.addTab(editor, tab_title)
        editor.textChanged.connect(self._handle_text_changed)

        if set_current:
            self.tab_widget.setCurrentWidget(editor)
        return editor

    def _handle_text_changed(self):
        editor = self.sender()
        if not isinstance(editor, QPlainTextEdit):
            return # Should not happen if connected correctly

        index = self.tab_widget.indexOf(editor)
        if index == -1: return

        # A more robust check for modification: compare with original content if file was loaded
        # For now, any textChange marks as modified.
        # original_content = editor.property("original_content_on_load")
        # if editor.toPlainText() != original_content:
        #     editor.setProperty("modified", True)
        # else:
        #     editor.setProperty("modified", False)
        # For simplicity now, any change is "modified" until saved.
        editor.setProperty("modified", True)
        self._update_tab_title_from_editor(editor)

    def _update_tab_title_from_editor(self, editor):
        index = self.tab_widget.indexOf(editor)
        if index == -1: return

        filepath = editor.property("filepath")
        is_modified = editor.property("modified")

        base_title = "Untitled"
        if filepath:
            base_title = QFileInfo(filepath).fileName()

        title = base_title + ("*" if is_modified else "")
        self.tab_widget.setTabText(index, title)

    def refactored_open_file_dialog(self):
        current_editor = self.tab_widget.currentWidget()
        start_dir = os.path.expanduser("~")
        if current_editor and isinstance(current_editor, QPlainTextEdit):
            current_filepath = current_editor.property("filepath")
            if current_filepath:
                start_dir = QFileInfo(current_filepath).absolutePath()

        filepath, _ = QFileDialog.getOpenFileName(self, "Open File", start_dir,
                                                  "Text Files (*.txt *.md *.py *.json *.yaml *.html *.css *.js);;All Files (*)")
        if filepath:
            for i in range(self.tab_widget.count()):
                editor = self.tab_widget.widget(i)
                if isinstance(editor, QPlainTextEdit) and editor.property("filepath") == filepath:
                    self.tab_widget.setCurrentIndex(i)
                    return
            self.refactor_add_new_tab(filepath=filepath) # Use the refactored method

    def refactored_save_current_file(self, force_save_as=False):
        editor = self.tab_widget.currentWidget()
        if not isinstance(editor, QPlainTextEdit):
            return False

        filepath = editor.property("filepath")
        if force_save_as or not filepath:
            return self.refactored_save_file_as_dialog()

        try:
            content = editor.toPlainText()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            editor.setProperty("modified", False)
            editor.setProperty("original_content_on_load", content) # Update original content marker
            self._update_tab_title_from_editor(editor)
            if self.parent_window and hasattr(self.parent_window, 'statusBar'):
                self.parent_window.statusBar().showMessage(f"Saved: {filepath}", 3000)
            return True
        except Exception as e:
            QMessageBox.warning(self, "Error Saving File", f"Could not save file: {filepath}\n{str(e)}")
            return False

    def refactored_save_file_as_dialog(self):
        editor = self.tab_widget.currentWidget()
        if not isinstance(editor, QPlainTextEdit):
            return False

        current_filepath = editor.property("filepath")
        suggested_name = QFileInfo(current_filepath).fileName() if current_filepath else "untitled.txt"
        start_dir = QFileInfo(current_filepath).absolutePath() if current_filepath else os.path.expanduser("~")

        filepath, _ = QFileDialog.getSaveFileName(self, "Save File As",
                                                  os.path.join(start_dir, suggested_name),
                                                  "Text Files (*.txt *.md *.py *.json *.yaml);;All Files (*)")
        if filepath:
            editor.setProperty("filepath", filepath)
            # self._update_tab_title_from_editor(editor) # title will be updated by save_current_file
            return self.refactored_save_current_file()
        return False

    def refactored_close_tab(self, index):
        editor = self.tab_widget.widget(index)
        if not isinstance(editor, QPlainTextEdit): # Should not happen
            self.tab_widget.removeTab(index)
            return

        if editor.property("modified"):
            filepath = editor.property("filepath")
            filename = QFileInfo(filepath).fileName() if filepath else "Untitled"

            reply = QMessageBox.question(self, "Save Changes?",
                                         f"'{filename}' has been modified. Save changes?",
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if reply == QMessageBox.Save:
                if not self.refactored_save_current_file(): # User might cancel Save As dialog
                    return
            elif reply == QMessageBox.Cancel:
                return

        tab_text = self.tab_widget.tabText(index) # Get before removing
        self.tab_widget.removeTab(index)
        if self.parent_window and hasattr(self.parent_window, 'statusBar'):
             self.parent_window.statusBar().showMessage(f"Closed tab: {tab_text.replace('*','')}", 3000)

    def get_current_document_content(self) -> str | None:
        """Returns the plain text content of the currently active tab's editor."""
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, QPlainTextEdit):
            return editor.toPlainText()
        return None

    # Replace old method calls in __init__ with refactored ones
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        # Connect to the refactored close method
        self.tab_widget.tabCloseRequested.connect(self.refactored_close_tab)

        self.layout.addWidget(self.tab_widget)

        button_layout = QHBoxLayout()
        self.new_button = QPushButton("New Tab")
        # Connect to the refactored add method
        self.new_button.clicked.connect(lambda: self.refactor_add_new_tab(title="Untitled"))
        self.open_button = QPushButton("Open File")
        # Connect to the refactored open method
        self.open_button.clicked.connect(self.refactored_open_file_dialog)
        self.save_button = QPushButton("Save")
        # Connect to the refactored save method
        self.save_button.clicked.connect(lambda: self.refactored_save_current_file(force_save_as=False))
        self.save_as_button = QPushButton("Save As")
        # Connect to the refactored save_as method
        self.save_as_button.clicked.connect(lambda: self.refactored_save_current_file(force_save_as=True))

        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.save_as_button)
        button_layout.addStretch()
        self.layout.addLayout(button_layout)

# Simple test
if __name__ == '__main__':
    import sys
    import qdarkstyle

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))

    # Create a dummy main window for status bar access
    class DummyMainWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.layout = QVBoxLayout(self)
            self.editor_area = TextEditorArea(parent=self) # Pass self as parent
            self.layout.addWidget(self.editor_area)
            self._status_bar = QLabel("Status bar ready")
            self.layout.addWidget(self._status_bar)
            self.setWindowTitle("Text Editor Test")

        def statusBar(self): # Mock statusBar
            return self._status_bar

        # Mock showMessage for QLabel
        class StatusBarEmulator:
            def __init__(self, label_widget):
                self.label_widget = label_widget
            def showMessage(self, message, timeout=0):
                self.label_widget.setText(message)
                # QLabel doesn't have timeout, would need QTimer for that

        def statusBar(self):
            return self.StatusBarEmulator(self._status_bar)


    # main_win = QMainWindow() # Using QMainWindow to get a real status bar
    # editor_area = TextEditorArea(parent=main_win)
    # main_win.setCentralWidget(editor_area)
    # main_win.setWindowTitle("Text Editor Test")
    # main_win.statusBar().showMessage("Ready")
    # main_win.show()

    dummy_main = DummyMainWindow()
    dummy_main.editor_area.refactor_add_new_tab(content="Hello World\nThis is a test.", title="Test Tab")
    # To test with a real file, create one, e.g., "test.txt"
    # with open("test.txt", "w") as f:
    #     f.write("Content from test.txt")
    # dummy_main.editor_area.refactor_add_new_tab(filepath="test.txt")

    dummy_main.show()
    sys.exit(app.exec())
