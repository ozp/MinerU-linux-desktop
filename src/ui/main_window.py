"""
Main Window for MinerU Desktop Client.

This module provides the main application window with a clean,
SOLID-compliant architecture that separates UI from business logic.
"""

import os
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QListWidget, QFileDialog,
    QMessageBox, QGroupBox, QListWidgetItem, QProgressBar
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices

from .settings_dialog import SettingsDialog
from ..services.batch_service import BatchService
from ..workers.upload_worker import UploadWorker
from ..workers.polling_worker import PollingWorker
from ..models.batch import BatchInfo
from ..config.constants import FILE_FILTERS, STATUS_TEXT, FileStatusLocal
from ..config.config_manager import get_config
from ..utils.logging_config import get_logger
from version import VERSION


logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window for MinerU Desktop Client.

    This window provides a clean interface for:
    - Selecting files for processing
    - Uploading files to MinerU API
    - Monitoring processing status
    - Downloading results
    """

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()

        self.config = get_config()
        self.batch_service = BatchService()
        self.current_batch: Optional[BatchInfo] = None
        self.upload_worker: Optional[UploadWorker] = None
        self.polling_worker: Optional[PollingWorker] = None

        self.setup_ui()
        logger.info("Main window initialized")

    def setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle(f"MinerU Desktop Client v{VERSION}")
        self.setMinimumSize(800, 650)

        # Create menu bar
        self._create_menu_bar()

        # Create central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # File selection section
        main_layout.addWidget(self._create_file_section())

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Processing section
        main_layout.addWidget(self._create_processing_section())

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _create_menu_bar(self) -> None:
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&Arquivo")

        # Settings action
        settings_action = QAction("&Configurações", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._open_settings)
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
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_file_section(self) -> QGroupBox:
        """
        Create the file selection section.

        Returns:
            QGroupBox with file list and buttons
        """
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()

        # Add files button
        button_layout = QHBoxLayout()
        self.add_files_button = QPushButton("Adicionar Arquivos...")
        self.add_files_button.clicked.connect(self._add_files)
        button_layout.addWidget(self.add_files_button)
        button_layout.addStretch()

        file_layout.addLayout(button_layout)

        # File list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        file_layout.addWidget(self.file_list)

        # Remove selected files button
        remove_button = QPushButton("Remover Selecionados")
        remove_button.clicked.connect(self._remove_selected_files)
        file_layout.addWidget(remove_button)

        file_group.setLayout(file_layout)
        return file_group

    def _create_processing_section(self) -> QGroupBox:
        """
        Create the processing controls section.

        Returns:
            QGroupBox with processing buttons
        """
        process_group = QGroupBox("Processing")
        process_layout = QVBoxLayout()

        # Buttons row
        buttons_row = QHBoxLayout()

        # Start processing button
        self.process_button = QPushButton("Iniciar Processamento")
        self.process_button.clicked.connect(self._start_processing)
        self.process_button.setEnabled(False)
        buttons_row.addWidget(self.process_button)

        # Open folder button
        self.open_folder_button = QPushButton("Abrir Pasta de Saída")
        self.open_folder_button.clicked.connect(self._open_output_folder)
        self.open_folder_button.setEnabled(False)
        buttons_row.addWidget(self.open_folder_button)

        buttons_row.addStretch()
        process_layout.addLayout(buttons_row)

        process_group.setLayout(process_layout)
        return process_group

    def _open_settings(self) -> None:
        """Open the settings dialog."""
        logger.debug("Opening settings dialog")
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Reload configuration after settings change
            self.config.load()
            logger.info("Configuration reloaded after settings change")

    def _show_about(self) -> None:
        """Show the about dialog with version information."""
        QMessageBox.about(
            self,
            "Sobre o MinerU Desktop Client",
            f"<h2>MinerU Desktop Client v{VERSION}</h2>"
            "<p>Um cliente desktop para a API do MinerU, desenvolvido em Python com PySide6.</p>"
            "<p><b>Funcionalidades:</b></p>"
            "<ul>"
            "<li>Upload de arquivos em lote</li>"
            "<li>Processamento automático</li>"
            "<li>Download e extração de resultados</li>"
            "<li>Interface em Português</li>"
            "<li>Arquitetura refatorada seguindo SOLID</li>"
            "</ul>"
            "<p><b>Repositório:</b> <a href='https://github.com/ozp/MinerU-linux-desktop'>github.com/ozp/MinerU-linux-desktop</a></p>"
        )

    def _add_files(self) -> None:
        """Open file dialog to select files for processing."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(FILE_FILTERS)

        if file_dialog.exec():
            files = file_dialog.selectedFiles()

            if not self.current_batch:
                self.current_batch = self.batch_service.create_batch([])

            for file_path in files:
                # Avoid duplicates
                if not any(f.file_path == file_path for f in self.current_batch.files):
                    file_info = self.current_batch.add_file(file_path)
                    self._add_file_to_list(file_info.filename, file_path)

            # Enable process button if files are selected
            self.process_button.setEnabled(len(self.current_batch.files) > 0)

            logger.info(f"Added {len(files)} files to batch")

    def _add_file_to_list(self, filename: str, file_path: str) -> None:
        """
        Add a file to the UI list.

        Args:
            filename: Display name of the file
            file_path: Full path to the file
        """
        status = STATUS_TEXT[FileStatusLocal.READY]
        item = QListWidgetItem(f"[{status}] {filename}")
        item.setData(Qt.UserRole, file_path)
        self.file_list.addItem(item)

    def _remove_selected_files(self) -> None:
        """Remove selected files from the list."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        if not self.current_batch:
            return

        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            filename = os.path.basename(file_path)

            # Remove from batch
            self.current_batch.files = [
                f for f in self.current_batch.files
                if f.file_path != file_path
            ]

            # Remove from UI
            self.file_list.takeItem(self.file_list.row(item))

        # Disable process button if no files remain
        self.process_button.setEnabled(len(self.current_batch.files) > 0)

        logger.debug(f"Removed {len(selected_items)} files")

    def _start_processing(self) -> None:
        """Start processing the selected files."""
        if not self.current_batch or len(self.current_batch.files) == 0:
            QMessageBox.warning(
                self,
                "Nenhum Arquivo",
                "Por favor, adicione arquivos antes de iniciar o processamento."
            )
            return

        logger.info(f"Starting processing of {len(self.current_batch.files)} files")

        # Disable buttons during processing
        self.process_button.setEnabled(False)
        self.add_files_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create and start upload worker thread
        self.upload_worker = UploadWorker(self.current_batch, self.batch_service)
        self.upload_worker.progress_updated.connect(self._on_upload_progress)
        self.upload_worker.upload_completed.connect(self._on_upload_completed)
        self.upload_worker.upload_failed.connect(self._on_upload_failed)
        self.upload_worker.start()

    def _on_upload_progress(self, progress: int) -> None:
        """
        Handle upload progress updates.

        Args:
            progress: Progress percentage (0-100)
        """
        self.progress_bar.setValue(progress)

    def _on_upload_completed(self, batch: BatchInfo) -> None:
        """
        Handle successful upload completion.

        Args:
            batch: BatchInfo with upload results
        """
        logger.info(f"Upload completed for batch {batch.batch_id}")

        # Update UI with upload results
        self._update_ui_from_batch()

        # Show success message
        summary = self.batch_service.get_batch_summary(batch)
        success_count = len([f for f in batch.files if f.status_local == FileStatusLocal.PROCESSING])
        failed_count = summary["failed"]

        if success_count > 0:
            QMessageBox.information(
                self,
                "Upload Concluído",
                f"Upload concluído!\n\nSucesso: {success_count}\nFalhas: {failed_count}\n\n"
                f"Batch ID: {batch.batch_id}\n\n"
                f"Verificando status automaticamente..."
            )

            # Start automatic polling
            self._start_polling()
        else:
            QMessageBox.critical(
                self,
                "Erro no Upload",
                f"Todos os uploads falharam.\n\nFalhas: {failed_count}"
            )

        # Re-enable buttons
        self.add_files_button.setEnabled(True)
        self.progress_bar.setVisible(False)

    def _on_upload_failed(self, error_message: str) -> None:
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

        # Re-enable buttons
        self.add_files_button.setEnabled(True)
        self.process_button.setEnabled(len(self.current_batch.files) > 0)
        self.progress_bar.setVisible(False)

    def _start_polling(self) -> None:
        """Start automatic polling for batch status."""
        if not self.current_batch or not self.current_batch.batch_id:
            return

        # Clean up existing polling worker if it exists
        if self.polling_worker:
            self.polling_worker.cleanup()
            self.polling_worker.deleteLater()
            self.polling_worker = None

        # Create and start new polling worker
        self.polling_worker = PollingWorker(self.current_batch, self.batch_service)
        self.polling_worker.status_updated.connect(self._on_status_updated)
        self.polling_worker.all_complete.connect(self._on_all_complete)
        self.polling_worker.error_occurred.connect(self._on_polling_error)
        self.polling_worker.start()

        logger.info(f"Started polling for batch {self.current_batch.batch_id}")

    def _on_status_updated(self, batch: BatchInfo) -> None:
        """
        Handle batch status update.

        Args:
            batch: Updated BatchInfo
        """
        self._update_ui_from_batch()

        # Enable open folder button if any file completed
        if any(f.status_local == FileStatusLocal.COMPLETED for f in batch.files):
            self.open_folder_button.setEnabled(True)

    def _on_all_complete(self, batch: BatchInfo) -> None:
        """
        Handle batch completion.

        Args:
            batch: Completed BatchInfo
        """
        summary = self.batch_service.get_batch_summary(batch)

        logger.info(f"Batch {batch.batch_id} completed: "
                   f"{summary['completed']} succeeded, {summary['failed']} failed")

        QMessageBox.information(
            self,
            "Processamento Concluído",
            "Todos os arquivos foram processados!\n\n"
            "Clique em 'Abrir Pasta de Saída' para ver os resultados."
        )

    def _on_polling_error(self, error_message: str) -> None:
        """
        Handle polling error.

        Args:
            error_message: Error description
        """
        logger.warning(f"Polling error: {error_message}")
        # Don't show error to user - continue polling

    def _update_ui_from_batch(self) -> None:
        """Update the file list UI from current batch state."""
        if not self.current_batch:
            return

        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.data(Qt.UserRole)
            filename = os.path.basename(file_path)

            # Find corresponding file info
            file_info = self.current_batch.get_file_by_name(filename)
            if file_info:
                status_text = STATUS_TEXT.get(
                    file_info.status_local,
                    file_info.status_local.value
                )
                item.setText(f"[{status_text}] {filename}")

    def _open_output_folder(self) -> None:
        """Open the output directory in the file manager."""
        output_dir = self.config.output_directory
        if os.path.exists(output_dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))
            logger.debug(f"Opened output folder: {output_dir}")
        else:
            QMessageBox.warning(
                self,
                "Pasta não encontrada",
                f"A pasta de saída não existe:\n{output_dir}"
            )

    def closeEvent(self, event) -> None:
        """
        Handle application close event.

        Args:
            event: Close event
        """
        logger.info("Application closing")

        # Stop and cleanup polling worker
        if self.polling_worker:
            self.polling_worker.cleanup()
            self.polling_worker.deleteLater()

        # Wait for upload worker to finish
        if self.upload_worker and self.upload_worker.isRunning():
            self.upload_worker.wait()

        event.accept()
