"""MinerU Linux Desktop Client.

A desktop application for interacting with the MinerU API on Linux systems.
This application provides a graphical user interface for uploading documents,
monitoring processing status, and downloading processed results.

The main components include:
    - MainWindow: Primary application window with file selection and processing controls
    - UploadWorker: Background thread worker for non-blocking file uploads

Typical usage example:
    $ python main.py

The application will launch the GUI where users can:
    1. Configure API settings (File > Settings)
    2. Add files for processing
    3. Start batch processing
    4. Monitor progress and download results
"""

import sys
import os
import zipfile
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QListWidget, QFileDialog,
    QMessageBox, QGroupBox, QListWidgetItem, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QUrl
from PySide6.QtGui import QAction, QDesktopServices
from settings_dialog import SettingsDialog
from mineru_client import MineruClient
from version import VERSION, VERSION_STRING


class UploadWorker(QThread):
    """Worker thread for uploading files to MinerU API without blocking the UI.

    This QThread subclass handles file uploads in the background, emitting signals
    to update the main window about progress and completion status.

    Attributes:
        mineru_client (MineruClient): Client instance for API communication
        file_paths (List[str]): List of file paths to upload
        progress_updated (Signal[int]): Emitted when upload progress changes (0-100)
        upload_completed (Signal[dict]): Emitted when upload succeeds with result data
        upload_failed (Signal[str]): Emitted when upload fails with error message
    """

    progress_updated = Signal(int)
    upload_completed = Signal(dict)
    upload_failed = Signal(str)

    def __init__(self, mineru_client, file_paths):
        """Initialize the upload worker.

        Args:
            mineru_client (MineruClient): Client instance for API operations
            file_paths (List[str]): List of local file paths to upload
        """
        super().__init__()
        self.mineru_client = mineru_client
        self.file_paths = file_paths

    def run(self):
        """Execute the upload operation in a separate thread.

        This method runs in the background and communicates with the main thread
        via signals. It handles exceptions and emits appropriate signals based on
        the upload outcome.

        Emits:
            progress_updated: During upload with progress percentage
            upload_completed: On success with result dictionary
            upload_failed: On error with error message string
        """
        try:
            def progress_callback(progress):
                self.progress_updated.emit(progress)

            result = self.mineru_client.upload_batch(self.file_paths, progress_callback)
            self.upload_completed.emit(result)
        except Exception as e:
            self.upload_failed.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for MinerU Desktop Client.

    This class implements the primary user interface for the application, providing
    controls for file selection, batch processing, progress monitoring, and result
    management. It coordinates with the MineruClient for API operations and manages
    background upload workers.

    Attributes:
        selected_files (List[str]): Currently selected file paths for processing
        current_batch_id (Optional[str]): ID of the current processing batch
        mineru_client (MineruClient): API client instance
        upload_worker (Optional[UploadWorker]): Background worker for uploads
        polling_timer (Optional[QTimer]): Timer for automatic status polling
        file_status_map (Dict[str, str]): Maps filenames to their processing status
        file_list (QListWidget): Widget displaying selected files
        process_button (QPushButton): Button to start processing
        add_files_button (QPushButton): Button to add files
        open_folder_button (QPushButton): Button to open output directory
        progress_bar (QProgressBar): Upload progress indicator
    """

    def __init__(self):
        """Initialize the main window and its components.

        Sets up the UI, initializes the API client, and prepares internal state
        for file processing operations.
        """
        super().__init__()
        self.selected_files = []
        self.current_batch_id = None
        self.mineru_client = MineruClient()
        self.upload_worker = None
        self.polling_timer = None
        self.file_status_map = {}  # Maps filename to status
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface components.

        Creates and arranges all UI elements including menu bar, file selection
        controls, progress indicators, and processing buttons. Configures layout
        and connects signals to appropriate handlers.
        """
        self.setWindowTitle(f"MinerU Desktop Client v{VERSION}")
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
        """Create the application menu bar with File and Help menus.

        Sets up menu items for Settings, Exit, and About dialog.
        Includes keyboard shortcuts for common actions.
        """
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

        # Help menu
        help_menu = menubar.addMenu("&Ajuda")

        # About action
        about_action = QAction("&Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def open_settings(self):
        """Open the settings dialog for API and processing configuration.

        Displays the SettingsDialog and reloads the client configuration if
        settings are saved successfully.
        """
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Reload client config after settings change
            self.mineru_client.load_config()

    def show_about(self):
        """Show the about dialog with version and feature information.

        Displays application name, version, key features, and repository link.
        """
        QMessageBox.about(
            self,
            "Sobre o MinerU Desktop Client",
            f"<h2>{VERSION_STRING}</h2>"
            "<p>Um cliente desktop para a API do MinerU, desenvolvido em Python com PySide6.</p>"
            "<p><b>Funcionalidades:</b></p>"
            "<ul>"
            "<li>Upload de arquivos em lote</li>"
            "<li>Processamento automático</li>"
            "<li>Download e extração de resultados</li>"
            "<li>Interface em Português</li>"
            "</ul>"
            "<p><b>Repositório:</b> <a href='https://github.com/ozp/MinerU-linux-desktop'>github.com/ozp/MinerU-linux-desktop</a></p>"
        )

    def add_files(self):
        """Open file dialog to select files for processing.

        Allows multi-file selection with filters for supported document types
        (PDF, DOCX, PPTX) and images (JPG, PNG). Prevents duplicate additions
        and updates the file list widget with selected files.
        """
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
        """Remove selected files from the processing list.

        Removes all currently selected items from the file list widget and
        updates internal tracking structures. Disables the process button
        if no files remain.
        """
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
        """Start processing the selected files via background upload.

        Initiates a background UploadWorker thread to upload files to the API
        without blocking the UI. Displays progress bar and disables controls
        during upload. Shows warning if no files are selected.
        """
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
        """Update progress bar during upload.

        Args:
            progress (int): Upload progress percentage (0-100)
        """
        self.progress_bar.setValue(progress)

    def on_upload_completed(self, result):
        """Handle successful upload completion and initiate status polling.

        Updates file statuses in the UI, displays success/failure counts,
        and starts automatic polling for processing status if any files
        uploaded successfully.

        Args:
            result (dict): Upload result containing 'batch_id' and 'uploads' list
        """
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
        """Handle upload failure with user notification.

        Displays error dialog and re-enables UI controls.

        Args:
            error_message (str): Description of the upload error
        """
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
        """Start automatic polling for batch processing status.

        Creates a QTimer that checks batch status every 10 seconds.
        Performs an immediate status check on start. Properly cleans up
        any existing timer before creating a new one.
        """
        if not self.current_batch_id:
            return

        # Stop and cleanup existing timer if it exists
        if self.polling_timer:
            if self.polling_timer.isActive():
                self.polling_timer.stop()
            try:
                self.polling_timer.timeout.disconnect()
            except:
                pass  # Ignore if no connections exist
            self.polling_timer.deleteLater()
            self.polling_timer = None

        # Create and start timer (poll every 10 seconds)
        self.polling_timer = QTimer(self)
        self.polling_timer.timeout.connect(self.check_batch_status)
        self.polling_timer.start(10000)  # 10 seconds

        # Check status immediately
        self.check_batch_status()

    def check_batch_status(self):
        """Check the status of the current batch and download completed files.

        Queries the API for current batch status, updates file statuses in the UI,
        and automatically downloads and extracts completed results. Continues polling
        until all files reach a final state (completed/failed). Handles various file
        states: pending, processing, done, and failed.

        The method also enables the "Open Folder" button when at least one file
        completes successfully.
        """
        if not self.current_batch_id:
            return

        try:
            status_data = self.mineru_client.get_batch_status(self.current_batch_id)

            # Extract data from response structure
            data = status_data.get("data", {})
            files_info = data.get("extract_result", [])

            print(f"[DEBUG] Checking batch {self.current_batch_id}")
            print(f"[DEBUG] Found {len(files_info)} files in API response")

            # Create a map of files in the API response for easy lookup
            api_files_map = {f.get("file_name"): f for f in files_info}

            all_done = True
            has_completed = False
            files_still_processing = 0

            # Check all files that were uploaded (from file_status_map)
            for filename, current_status in list(self.file_status_map.items()):
                # Skip files that are already in a final state
                if current_status in ["completed", "failed", "download_failed"]:
                    continue

                # Check if this file is in the API response
                if filename not in api_files_map:
                    print(f"[DEBUG] File {filename} not yet in API response")
                    all_done = False
                    files_still_processing += 1
                    continue

                file_info = api_files_map[filename]
                state = file_info.get("state")
                print(f"[DEBUG] File: {filename}, State: {state}")

                if state == "done":
                    # Download the result if not already downloaded
                    if current_status != "completed":
                        zip_url = file_info.get("full_zip_url")
                        if zip_url:
                            try:
                                print(f"[DEBUG] Downloading result for {filename}")
                                # Download ZIP file
                                output_filename = f"{os.path.splitext(filename)[0]}_result.zip"
                                zip_path = self.mineru_client.download_result(zip_url, output_filename)

                                # Extract ZIP to folder
                                extract_folder = os.path.join(
                                    self.mineru_client.output_directory,
                                    os.path.splitext(filename)[0]
                                )
                                os.makedirs(extract_folder, exist_ok=True)

                                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                    zip_ref.extractall(extract_folder)

                                # Remove the ZIP file after extraction
                                os.remove(zip_path)

                                # Update UI
                                self.update_file_status(filename, "Concluído")
                                self.file_status_map[filename] = "completed"
                                has_completed = True
                                print(f"[DEBUG] Successfully downloaded and extracted {filename}")
                            except Exception as e:
                                print(f"[DEBUG] Error downloading {filename}: {e}")
                                self.update_file_status(filename, f"Erro no Download - {str(e)}")
                                self.file_status_map[filename] = "download_failed"
                        else:
                            print(f"[DEBUG] No zip_url for {filename}")
                            self.update_file_status(filename, "Erro - URL não encontrada")
                            self.file_status_map[filename] = "download_failed"

                elif state == "failed":
                    err_msg = file_info.get("err_msg", "Unknown error")
                    print(f"[DEBUG] File {filename} failed: {err_msg}")
                    self.update_file_status(filename, f"Falha - {err_msg}")
                    self.file_status_map[filename] = "failed"

                elif state in ["processing", "pending"]:
                    print(f"[DEBUG] File {filename} still {state}")
                    all_done = False
                    files_still_processing += 1
                    # Update UI to show current state
                    if state == "processing":
                        self.update_file_status(filename, "Processando no servidor...")
                    else:
                        self.update_file_status(filename, "Na fila...")

                else:
                    # Unknown state - don't mark as done
                    print(f"[DEBUG] Unknown state '{state}' for {filename}")
                    all_done = False
                    files_still_processing += 1

            print(f"[DEBUG] Files still processing: {files_still_processing}")
            print(f"[DEBUG] All done: {all_done}")

            # Enable open folder button if any file completed
            if has_completed:
                self.open_folder_button.setEnabled(True)

            # Stop polling if all files are done
            if all_done:
                if self.polling_timer:
                    self.polling_timer.stop()
                    try:
                        self.polling_timer.timeout.disconnect()
                    except:
                        pass  # Ignore if no connections exist
                    self.polling_timer.deleteLater()
                    self.polling_timer = None
                QMessageBox.information(
                    self,
                    "Processamento Concluído",
                    "Todos os arquivos foram processados!\n\n"
                    "Clique em 'Abrir Pasta de Saída' para ver os resultados."
                )

        except Exception as e:
            print(f"[ERROR] Error checking batch status: {e}")
            import traceback
            traceback.print_exc()
            # Continue polling even if there's an error

    def update_file_status(self, filename, status):
        """Update the status of a file in the list widget.

        Args:
            filename (str): Name of the file to update
            status (str): New status text to display
        """
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.data(Qt.UserRole)
            if os.path.basename(file_path) == filename:
                item.setText(f"[{status}] {filename}")
                break

    def open_output_folder(self):
        """Open the output directory in the system file manager.

        Uses QDesktopServices to open the configured output directory.
        Shows a warning if the directory doesn't exist.
        """
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
        """Handle application close event with proper cleanup.

        Stops any active polling timer and waits for the upload worker thread
        to complete before closing.

        Args:
            event (QCloseEvent): The close event to accept or reject
        """
        # Stop polling timer if running
        if self.polling_timer:
            if self.polling_timer.isActive():
                self.polling_timer.stop()
            try:
                self.polling_timer.timeout.disconnect()
            except:
                pass  # Ignore if no connections exist
            self.polling_timer.deleteLater()
            self.polling_timer = None

        # Wait for upload worker to finish
        if self.upload_worker and self.upload_worker.isRunning():
            self.upload_worker.wait()

        event.accept()


def main():
    """Application entry point.

    Creates the QApplication instance, initializes and shows the main window,
    and starts the Qt event loop.

    Returns:
        int: Application exit code
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
