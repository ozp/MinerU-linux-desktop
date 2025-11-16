"""
MinerU Linux Desktop Client

A desktop application for interacting with the MinerU API on Linux systems.
This app allows users to upload documents, monitor processing status,
and download processed results.
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QListWidget, QFileDialog,
    QMessageBox, QGroupBox, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction
from settings_dialog import SettingsDialog
from mineru_client import MineruClient


class MainWindow(QMainWindow):
    """Main application window for MinerU Desktop Client."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.selected_files = []
        self.current_batch_id = None
        self.mineru_client = MineruClient()
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("MinerU Desktop Client")
        self.setMinimumSize(800, 600)

        # Create menu bar
        self.create_menu_bar()

        # Create central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # File selection section
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()

        # Add files button
        button_layout = QHBoxLayout()
        self.add_files_button = QPushButton("Adicionar Arquivos")
        self.add_files_button.clicked.connect(self.add_files)
        button_layout.addWidget(self.add_files_button)
        button_layout.addStretch()

        file_layout.addLayout(button_layout)

        # File list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        file_layout.addWidget(self.file_list)

        # Remove selected files button
        remove_button = QPushButton("Remover Selecionados")
        remove_button.clicked.connect(self.remove_selected_files)
        file_layout.addWidget(remove_button)

        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # Processing section
        process_group = QGroupBox("Processing")
        process_layout = QVBoxLayout()

        # Start processing button
        self.process_button = QPushButton("Iniciar Processamento")
        self.process_button.clicked.connect(self.start_processing)
        self.process_button.setEnabled(False)
        process_layout.addWidget(self.process_button)

        # Batch ID display
        self.batch_id_label = QLabel("Batch ID: Nenhum")
        self.batch_id_label.setWordWrap(True)
        process_layout.addWidget(self.batch_id_label)

        process_group.setLayout(process_layout)
        main_layout.addWidget(process_group)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Settings action
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        # Exit action
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Reload client config after settings change
            self.mineru_client.load_config()

    def add_files(self):
        """Open file dialog to select files for processing."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(
            "Documents (*.pdf *.docx *.pptx *.png *.jpg *.jpeg);;All Files (*)"
        )

        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            for file_path in files:
                # Avoid duplicates
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    item = QListWidgetItem(f"[Pronto] {os.path.basename(file_path)}")
                    item.setData(Qt.UserRole, file_path)
                    self.file_list.addItem(item)

            # Enable process button if files are selected
            self.process_button.setEnabled(len(self.selected_files) > 0)

    def remove_selected_files(self):
        """Remove selected files from the list."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            if file_path in self.selected_files:
                self.selected_files.remove(file_path)
            self.file_list.takeItem(self.file_list.row(item))

        # Disable process button if no files remain
        self.process_button.setEnabled(len(self.selected_files) > 0)

    def start_processing(self):
        """Start processing the selected files."""
        if not self.selected_files:
            QMessageBox.warning(
                self,
                "No Files",
                "Please add files before starting processing."
            )
            return

        # Disable buttons during processing
        self.process_button.setEnabled(False)
        self.add_files_button.setEnabled(False)

        try:
            # Upload files
            result = self.mineru_client.upload_batch(self.selected_files)

            # Store batch ID
            self.current_batch_id = result.get("batch_id")
            self.batch_id_label.setText(f"Batch ID: {self.current_batch_id}")

            # Update file statuses
            uploads = result.get("uploads", [])
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                file_path = item.data(Qt.UserRole)
                filename = os.path.basename(file_path)

                # Find corresponding upload result
                upload_result = next(
                    (u for u in uploads if u["file"] == filename),
                    None
                )

                if upload_result:
                    if upload_result["status"] == "success":
                        item.setText(f"[Enviado] {filename}")
                    else:
                        error = upload_result.get("error", "Unknown error")
                        item.setText(f"[Falhou] {filename} - {error}")

            # Show success message
            success_count = sum(1 for u in uploads if u["status"] == "success")
            failed_count = len(uploads) - success_count

            msg = f"Upload concluído!\n\n"
            msg += f"Sucesso: {success_count}\n"
            msg += f"Falhas: {failed_count}\n"
            msg += f"Batch ID: {self.current_batch_id}"

            QMessageBox.information(self, "Upload Concluído", msg)

        except ValueError as e:
            QMessageBox.critical(
                self,
                "Configuration Error",
                f"Please configure your API settings first:\n\n{str(e)}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Upload Error",
                f"Failed to upload files:\n\n{str(e)}"
            )

        finally:
            # Re-enable buttons
            self.add_files_button.setEnabled(True)
            self.process_button.setEnabled(len(self.selected_files) > 0)


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
