"""
MinerU Linux Desktop Client

A desktop application for interacting with the MinerU API on Linux systems.
This app allows users to upload documents, monitor processing status,
and download processed results.
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QListWidget, QFileDialog,
    QMessageBox, QGroupBox, QListWidgetItem, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QUrl
from PySide6.QtGui import QAction, QDesktopServices
from settings_dialog import SettingsDialog
from mineru_client import MineruClient


class UploadWorker(QThread):
    """Worker thread for uploading files to MinerU API."""

    progress_updated = Signal(int)
    upload_completed = Signal(dict)
    upload_failed = Signal(str)

    def __init__(self, mineru_client, file_paths):
        super().__init__()
        self.mineru_client = mineru_client
        self.file_paths = file_paths

    def run(self):
        """Execute the upload in a separate thread."""
        try:
            def progress_callback(progress):
                self.progress_updated.emit(progress)

            result = self.mineru_client.upload_batch(self.file_paths, progress_callback)
            self.upload_completed.emit(result)
        except Exception as e:
            self.upload_failed.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for MinerU Desktop Client."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.selected_files = []
        self.current_batch_id = None
        self.mineru_client = MineruClient()
        self.upload_worker = None
        self.polling_timer = None
        self.file_status_map = {}  # Maps filename to status
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("MinerU Desktop Client")
        self.setMinimumSize(800, 650)

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
        self.add_files_button = QPushButton("Adicionar Arquivos...")
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

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Processing section
        process_group = QGroupBox("Processing")
        process_layout = QVBoxLayout()

        # Buttons row
        buttons_row = QHBoxLayout()

        # Start processing button
        self.process_button = QPushButton("Iniciar Processamento")
        self.process_button.clicked.connect(self.start_processing)
        self.process_button.setEnabled(False)
        buttons_row.addWidget(self.process_button)

        # Open folder button
        self.open_folder_button = QPushButton("Abrir Pasta de Saída")
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.open_folder_button.setEnabled(False)
        buttons_row.addWidget(self.open_folder_button)

        buttons_row.addStretch()
        process_layout.addLayout(buttons_row)

        process_group.setLayout(process_layout)
        main_layout.addWidget(process_group)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&Arquivo")

        # Settings action
        settings_action = QAction("&Configurações", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        # Exit action
        file_menu.addSeparator()
        exit_action = QAction("&Sair", self)
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
            "Documentos (*.pdf *.docx *.pptx);;Imagens (*.jpg *.png);;Todos os Arquivos (*)"
        )

        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            for file_path in files:
                # Avoid duplicates
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    filename = os.path.basename(file_path)
                    item = QListWidgetItem(f"[Pronto] {filename}")
                    item.setData(Qt.UserRole, file_path)
                    self.file_list.addItem(item)
                    self.file_status_map[filename] = "ready"

            # Enable process button if files are selected
            self.process_button.setEnabled(len(self.selected_files) > 0)

    def remove_selected_files(self):
        """Remove selected files from the list."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            filename = os.path.basename(file_path)
            if file_path in self.selected_files:
                self.selected_files.remove(file_path)
            if filename in self.file_status_map:
                del self.file_status_map[filename]
            self.file_list.takeItem(self.file_list.row(item))

        # Disable process button if no files remain
        self.process_button.setEnabled(len(self.selected_files) > 0)

    def start_processing(self):
        """Start processing the selected files."""
        if not self.selected_files:
            QMessageBox.warning(
                self,
                "Nenhum Arquivo",
                "Por favor, adicione arquivos antes de iniciar o processamento."
            )
            return

        # Disable buttons during processing
        self.process_button.setEnabled(False)
        self.add_files_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create and start upload worker thread
        self.upload_worker = UploadWorker(self.mineru_client, self.selected_files)
        self.upload_worker.progress_updated.connect(self.on_upload_progress)
        self.upload_worker.upload_completed.connect(self.on_upload_completed)
        self.upload_worker.upload_failed.connect(self.on_upload_failed)
        self.upload_worker.start()

    def on_upload_progress(self, progress):
        """Update progress bar during upload."""
        self.progress_bar.setValue(progress)

    def on_upload_completed(self, result):
        """Handle successful upload completion."""
        # Store batch ID
        self.current_batch_id = result.get("batch_id")

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
                    item.setText(f"[Enviado - Processando...] {filename}")
                    self.file_status_map[filename] = "processing"
                else:
                    error = upload_result.get("error", "Unknown error")
                    item.setText(f"[Falhou] {filename} - {error}")
                    self.file_status_map[filename] = "failed"

        # Show success message
        success_count = sum(1 for u in uploads if u["status"] == "success")
        failed_count = len(uploads) - success_count

        if success_count > 0:
            QMessageBox.information(
                self,
                "Upload Concluído",
                f"Upload concluído!\n\nSucesso: {success_count}\nFalhas: {failed_count}\n\n"
                f"Batch ID: {self.current_batch_id}\n\n"
                f"Verificando status automaticamente..."
            )

            # Start automatic polling
            self.start_polling()
        else:
            QMessageBox.critical(
                self,
                "Erro no Upload",
                f"Todos os uploads falharam.\n\nFalhas: {failed_count}"
            )

        # Re-enable buttons
        self.add_files_button.setEnabled(True)
        self.progress_bar.setVisible(False)

    def on_upload_failed(self, error_message):
        """Handle upload failure."""
        QMessageBox.critical(
            self,
            "Erro no Upload",
            f"Falha ao enviar arquivos:\n\n{error_message}"
        )

        # Re-enable buttons
        self.add_files_button.setEnabled(True)
        self.process_button.setEnabled(len(self.selected_files) > 0)
        self.progress_bar.setVisible(False)

    def start_polling(self):
        """Start automatic polling for batch status."""
        if not self.current_batch_id:
            return

        # Create and start timer (poll every 10 seconds)
        self.polling_timer = QTimer(self)
        self.polling_timer.timeout.connect(self.check_batch_status)
        self.polling_timer.start(10000)  # 10 seconds

        # Check status immediately
        self.check_batch_status()

    def check_batch_status(self):
        """Check the status of the current batch and download completed files."""
        if not self.current_batch_id:
            return

        try:
            status_data = self.mineru_client.get_batch_status(self.current_batch_id)

            # Extract data from response structure
            data = status_data.get("data", {})
            files_info = data.get("extract_result", [])

            all_done = True
            has_completed = False

            for file_info in files_info:
                filename = file_info.get("file_name")
                state = file_info.get("state")

                if state == "done":
                    # Download the result if not already downloaded
                    if self.file_status_map.get(filename) != "completed":
                        zip_url = file_info.get("full_zip_url")
                        if zip_url:
                            try:
                                # Download file
                                output_filename = f"{os.path.splitext(filename)[0]}_result.zip"
                                self.mineru_client.download_result(zip_url, output_filename)

                                # Update UI
                                self.update_file_status(filename, "Concluído")
                                self.file_status_map[filename] = "completed"
                                has_completed = True
                            except Exception as e:
                                self.update_file_status(filename, f"Erro no Download - {str(e)}")
                                self.file_status_map[filename] = "download_failed"

                elif state == "failed":
                    err_msg = file_info.get("err_msg", "Unknown error")
                    self.update_file_status(filename, f"Falha - {err_msg}")
                    self.file_status_map[filename] = "failed"

                elif state in ["processing", "pending"]:
                    all_done = False

            # Enable open folder button if any file completed
            if has_completed:
                self.open_folder_button.setEnabled(True)

            # Stop polling if all files are done
            if all_done:
                if self.polling_timer:
                    self.polling_timer.stop()
                QMessageBox.information(
                    self,
                    "Processamento Concluído",
                    "Todos os arquivos foram processados!\n\n"
                    "Clique em 'Abrir Pasta de Saída' para ver os resultados."
                )

        except Exception as e:
            print(f"Error checking batch status: {e}")
            # Continue polling even if there's an error

    def update_file_status(self, filename, status):
        """Update the status of a file in the list."""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.data(Qt.UserRole)
            if os.path.basename(file_path) == filename:
                item.setText(f"[{status}] {filename}")
                break

    def open_output_folder(self):
        """Open the output directory in the file manager."""
        output_dir = self.mineru_client.output_directory
        if os.path.exists(output_dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))
        else:
            QMessageBox.warning(
                self,
                "Pasta não encontrada",
                f"A pasta de saída não existe:\n{output_dir}"
            )

    def closeEvent(self, event):
        """Handle application close event."""
        # Stop polling timer if running
        if self.polling_timer and self.polling_timer.isActive():
            self.polling_timer.stop()

        # Wait for upload worker to finish
        if self.upload_worker and self.upload_worker.isRunning():
            self.upload_worker.wait()

        event.accept()


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
