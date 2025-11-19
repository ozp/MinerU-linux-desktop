"""
Main Window for MinerU Desktop Client.

Modernized UI with drag & drop, toast notifications, and theme support.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QFileDialog, QMessageBox, QGroupBox, QListWidgetItem,
    QProgressBar
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QAction, QDesktopServices

from mineru_desktop.core.client import MineruClient
from mineru_desktop.core.config import ConfigManager
from mineru_desktop.models.batch import Batch, FileState, ProcessingOptions
from mineru_desktop.services.upload_service import UploadService
from mineru_desktop.services.batch_service import BatchService
from mineru_desktop.workers.upload_worker import UploadWorker
from mineru_desktop.ui.settings_dialog import SettingsDialog
from mineru_desktop.ui.toast_notification import ToastNotification, ToastType
from mineru_desktop.utils.logging_config import get_logger
from version import VERSION

logger = get_logger(__name__)


class DragDropListWidget(QListWidget):
    """List widget with drag and drop support for files."""

    def __init__(self, parent=None):
        """Initialize the drag-drop list widget."""
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DropOnly)
        logger.debug("DragDropListWidget initialized")

    def dragEnterEvent(self, event):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            logger.debug("Drag enter accepted")
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop events."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
            if file_paths:
                logger.info(f"Files dropped: {len(file_paths)}")
                # Emit signal to parent
                if hasattr(self.parent(), 'add_files_from_paths'):
                    self.parent().add_files_from_paths(file_paths)
            event.acceptProposedAction()
        else:
            event.ignore()


class MainWindow(QMainWindow):
    """Main application window for MinerU Desktop Client."""

    POLL_INTERVAL_MS = 10000  # 10 seconds

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        logger.info("MainWindow initialization started")

        # Configuration and state
        self.config_manager = ConfigManager()
        self.current_batch: Optional[Batch] = None
        self.current_theme = "light"

        # Initialize API client and services
        self._initialize_services()

        # Workers and timers
        self.upload_worker: Optional[UploadWorker] = None
        self.polling_timer: Optional[QTimer] = None

        # Setup UI
        self.setup_ui()
        self.apply_theme(self.config_manager.get_theme_preference())

        logger.info("MainWindow initialization completed")

    def _initialize_services(self) -> None:
        """Initialize API client and services."""
        # Load configuration
        api_token = self.config_manager.load_api_token()
        processing_options = self.config_manager.load_processing_options()
        output_directory = self.config_manager.load_output_directory()

        # Create client
        self.client = MineruClient(api_token)

        # Create services
        self.upload_service = UploadService(self.client)
        self.batch_service = BatchService(self.client, output_directory)

        # Store output directory
        self.output_directory = output_directory

        logger.info(f"Services initialized with output_dir: {output_directory}")

    def setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle(f"MinerU Desktop Client v{VERSION}")
        self.setMinimumSize(850, 700)

        # Create menu bar
        self._create_menu_bar()

        # Create central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # File selection section
        file_group = self._create_file_selection_group()
        main_layout.addWidget(file_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        # Processing section
        process_group = self._create_processing_group()
        main_layout.addWidget(process_group)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        logger.debug("UI setup completed")

    def _create_menu_bar(self) -> None:
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&Arquivo")

        # Settings action
        settings_action = QAction("&Configurações", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("&Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&Visualizar")

        # Theme toggle action
        self.theme_action = QAction("🌙 Tema Escuro", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)

        # Help menu
        help_menu = menubar.addMenu("&Ajuda")

        # About action
        about_action = QAction("&Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _create_file_selection_group(self) -> QGroupBox:
        """Create file selection UI group."""
        file_group = QGroupBox("Seleção de Arquivos")
        file_layout = QVBoxLayout()

        # Add files button
        button_layout = QHBoxLayout()
        self.add_files_button = QPushButton("📁 Adicionar Arquivos...")
        self.add_files_button.clicked.connect(self.add_files)
        button_layout.addWidget(self.add_files_button)
        button_layout.addStretch()
        file_layout.addLayout(button_layout)

        # File list with drag & drop
        self.file_list = DragDropListWidget(self)
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        file_layout.addWidget(self.file_list)

        # Remove button
        self.remove_button = QPushButton("🗑️ Remover Selecionados")
        self.remove_button.setObjectName("dangerButton")
        self.remove_button.clicked.connect(self.remove_selected_files)
        file_layout.addWidget(self.remove_button)

        file_group.setLayout(file_layout)
        return file_group

    def _create_processing_group(self) -> QGroupBox:
        """Create processing UI group."""
        process_group = QGroupBox("Processamento")
        process_layout = QVBoxLayout()

        # Buttons row
        buttons_row = QHBoxLayout()

        # Start processing button
        self.process_button = QPushButton("▶️ Iniciar Processamento")
        self.process_button.clicked.connect(self.start_processing)
        self.process_button.setEnabled(False)
        buttons_row.addWidget(self.process_button)

        # Open folder button
        self.open_folder_button = QPushButton("📂 Abrir Pasta de Saída")
        self.open_folder_button.setObjectName("secondaryButton")
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.open_folder_button.setEnabled(False)
        buttons_row.addWidget(self.open_folder_button)

        buttons_row.addStretch()
        process_layout.addLayout(buttons_row)

        process_group.setLayout(process_layout)
        return process_group

    def add_files(self) -> None:
        """Open file dialog to select files for processing."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(
            "Documentos (*.pdf *.docx *.pptx);;Imagens (*.jpg *.png);;Todos os Arquivos (*)"
        )

        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            self.add_files_from_paths(files)
            logger.info(f"Added {len(files)} files via dialog")

    def add_files_from_paths(self, file_paths: list) -> None:
        """
        Add files from a list of paths.

        Args:
            file_paths: List of file paths to add
        """
        if not self.current_batch:
            processing_options = self.config_manager.load_processing_options()
            self.current_batch = Batch(processing_options=processing_options)
            self.current_batch.created_at = datetime.now()

        added_count = 0
        for file_path in file_paths:
            # Check if file already exists
            filename = os.path.basename(file_path)
            if not self.current_batch.get_file_by_name(filename):
                file_status = self.current_batch.add_file(file_path)

                # Add to UI list
                item = QListWidgetItem(f"[Pronto] {filename}")
                item.setData(Qt.UserRole, file_path)
                self.file_list.addItem(item)
                added_count += 1

        # Enable process button if files are selected
        if self.current_batch and self.current_batch.files:
            self.process_button.setEnabled(True)

        if added_count > 0:
            ToastNotification.show_success(
                self,
                f"{added_count} arquivo(s) adicionado(s)",
                2000
            )
            logger.info(f"Added {added_count} files to batch")

    def remove_selected_files(self) -> None:
        """Remove selected files from the list."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            filename = os.path.basename(file_path)

            # Remove from batch
            if self.current_batch:
                file_status = self.current_batch.get_file_by_name(filename)
                if file_status:
                    self.current_batch.files.remove(file_status)

            # Remove from UI
            self.file_list.takeItem(self.file_list.row(item))

        # Update process button state
        if not self.current_batch or not self.current_batch.files:
            self.process_button.setEnabled(False)

        ToastNotification.show_info(
            self,
            f"{len(selected_items)} arquivo(s) removido(s)",
            2000
        )
        logger.info(f"Removed {len(selected_items)} files")

    def start_processing(self) -> None:
        """Start processing the selected files."""
        if not self.current_batch or not self.current_batch.files:
            QMessageBox.warning(
                self,
                "Nenhum Arquivo",
                "Por favor, adicione arquivos antes de iniciar o processamento."
            )
            return

        logger.info("Starting processing")

        # Disable buttons during processing
        self.process_button.setEnabled(False)
        self.add_files_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create and start upload worker
        self.upload_worker = UploadWorker(self.upload_service, self.current_batch)
        self.upload_worker.progress_updated.connect(self.on_upload_progress)
        self.upload_worker.upload_completed.connect(self.on_upload_completed)
        self.upload_worker.upload_failed.connect(self.on_upload_failed)
        self.upload_worker.start()

        ToastNotification.show_info(self, "Iniciando upload...", 2000)

    def on_upload_progress(self, progress: int) -> None:
        """
        Update progress bar during upload.

        Args:
            progress: Progress percentage (0-100)
        """
        self.progress_bar.setValue(progress)

    def on_upload_completed(self, result: dict) -> None:
        """
        Handle successful upload completion.

        Args:
            result: Upload result dictionary
        """
        logger.info(f"Upload completed for batch: {result.get('batch_id')}")

        # Update UI with upload results
        uploads = result.get("uploads", [])
        for upload_result in uploads:
            filename = upload_result["file"]
            file_status = self.current_batch.get_file_by_name(filename)

            if file_status:
                status_text = file_status.get_display_status()
                self._update_list_item(filename, status_text)

        # Show success message
        success_count = sum(1 for u in uploads if u["status"] == "success")
        failed_count = len(uploads) - success_count

        if success_count > 0:
            ToastNotification.show_success(
                self,
                f"Upload concluído! {success_count} sucesso, {failed_count} falhas",
                3000
            )

            # Start automatic polling
            self.start_polling()
        else:
            ToastNotification.show_error(
                self,
                f"Todos os uploads falharam ({failed_count} falhas)",
                4000
            )

        # Re-enable buttons
        self.add_files_button.setEnabled(True)
        self.progress_bar.setVisible(False)

    def on_upload_failed(self, error_message: str) -> None:
        """
        Handle upload failure.

        Args:
            error_message: Error description
        """
        logger.error(f"Upload failed: {error_message}")

        QMessageBox.critical(
            self,
            "Erro no Upload",
            f"Falha ao enviar arquivos:\n\n{error_message}"
        )

        ToastNotification.show_error(
            self,
            "Upload falhou!",
            3000
        )

        # Re-enable buttons
        self.add_files_button.setEnabled(True)
        self.process_button.setEnabled(True)
        self.progress_bar.setVisible(False)

    def start_polling(self) -> None:
        """Start automatic polling for batch status."""
        if not self.current_batch or not self.current_batch.batch_id:
            return

        logger.info(f"Starting polling for batch: {self.current_batch.batch_id}")

        # Stop and cleanup existing timer
        self._stop_polling()

        # Create and start timer
        self.polling_timer = QTimer(self)
        self.polling_timer.timeout.connect(self.check_batch_status)
        self.polling_timer.start(self.POLL_INTERVAL_MS)

        # Check status immediately
        self.check_batch_status()

    def _stop_polling(self) -> None:
        """Stop the polling timer."""
        if self.polling_timer:
            if self.polling_timer.isActive():
                self.polling_timer.stop()
            try:
                self.polling_timer.timeout.disconnect()
            except:
                pass
            self.polling_timer.deleteLater()
            self.polling_timer = None

    def check_batch_status(self) -> None:
        """Check the status of the current batch."""
        if not self.current_batch or not self.current_batch.batch_id:
            return

        try:
            logger.debug(f"Checking batch status: {self.current_batch.batch_id}")

            summary = self.batch_service.check_batch_status(self.current_batch)

            # Update UI for each file
            for file_status in self.current_batch.files:
                status_text = file_status.get_display_status()
                self._update_list_item(file_status.filename, status_text)

            # Enable open folder button if any file completed
            if summary["has_completed"]:
                self.open_folder_button.setEnabled(True)

            # Stop polling if all done
            if summary["all_done"]:
                self._stop_polling()

                completed = summary["completed_count"]
                failed = summary["failed_count"]

                ToastNotification.show_success(
                    self,
                    f"Processamento concluído! {completed} sucesso, {failed} falhas",
                    4000
                )

                QMessageBox.information(
                    self,
                    "Processamento Concluído",
                    f"Todos os arquivos foram processados!\n\n"
                    f"Sucesso: {completed}\n"
                    f"Falhas: {failed}\n\n"
                    f"Clique em 'Abrir Pasta de Saída' para ver os resultados."
                )

                logger.info(f"Batch processing completed: {completed} success, {failed} failed")

        except Exception as e:
            logger.error(f"Error checking batch status: {e}", exc_info=True)
            # Continue polling even if there's an error

    def _update_list_item(self, filename: str, status: str) -> None:
        """
        Update the status of a file in the list.

        Args:
            filename: Name of the file
            status: Status text to display
        """
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.data(Qt.UserRole)
            if os.path.basename(file_path) == filename:
                item.setText(f"[{status}] {filename}")
                break

    def open_output_folder(self) -> None:
        """Open the output directory in the file manager."""
        if os.path.exists(self.output_directory):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_directory))
            logger.info(f"Opened output folder: {self.output_directory}")
        else:
            QMessageBox.warning(
                self,
                "Pasta não encontrada",
                f"A pasta de saída não existe:\n{self.output_directory}"
            )

    def open_settings(self) -> None:
        """Open the settings dialog."""
        logger.debug("Opening settings dialog")
        dialog = SettingsDialog(self, self.config_manager)
        if dialog.exec():
            # Reload configuration
            self._initialize_services()
            ToastNotification.show_success(self, "Configurações atualizadas!", 2000)
            logger.info("Settings updated")

    def toggle_theme(self) -> None:
        """Toggle between light and dark theme."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)
        self.config_manager.save_theme_preference(new_theme)
        logger.info(f"Theme changed to: {new_theme}")

    def apply_theme(self, theme: str) -> None:
        """
        Apply a theme to the application.

        Args:
            theme: Theme name ("light" or "dark")
        """
        self.current_theme = theme

        # Get stylesheet path
        if hasattr(sys, '_MEIPASS'):
            # Running as PyInstaller bundle
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent

        stylesheet_path = base_path / "styles" / f"{theme}_theme.qss"

        # Load and apply stylesheet
        try:
            with open(stylesheet_path, "r") as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)

            # Update theme action text
            if theme == "light":
                self.theme_action.setText("🌙 Tema Escuro")
            else:
                self.theme_action.setText("☀️ Tema Claro")

            logger.info(f"Applied {theme} theme")

        except Exception as e:
            logger.error(f"Failed to load theme '{theme}': {e}")
            # Fallback to default
            self.setStyleSheet("")

    def show_about(self) -> None:
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "Sobre o MinerU Desktop Client",
            f"<h2>MinerU Desktop Client v{VERSION}</h2>"
            "<p>Um cliente desktop moderno para a API do MinerU, desenvolvido em Python com PySide6.</p>"
            "<p><b>Funcionalidades:</b></p>"
            "<ul>"
            "<li>Upload de arquivos em lote com drag & drop</li>"
            "<li>Processamento automático</li>"
            "<li>Download e extração de resultados</li>"
            "<li>Interface em Português com temas claro/escuro</li>"
            "<li>Notificações visuais não-intrusivas</li>"
            "</ul>"
            "<p><b>Repositório:</b> <a href='https://github.com/ozp/MinerU-linux-desktop'>"
            "github.com/ozp/MinerU-linux-desktop</a></p>"
        )

    def closeEvent(self, event) -> None:
        """
        Handle application close event.

        Args:
            event: Close event
        """
        logger.info("Application closing")

        # Stop polling timer
        self._stop_polling()

        # Wait for upload worker to finish
        if self.upload_worker and self.upload_worker.isRunning():
            logger.debug("Waiting for upload worker to finish")
            self.upload_worker.wait()

        event.accept()
