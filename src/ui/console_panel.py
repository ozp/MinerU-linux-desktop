"""
Console Panel for MinerU Desktop Client.

This module provides a console panel for displaying application logs
with filtering, exporting, and auto-scroll capabilities.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QPlainTextEdit, QComboBox, QFileDialog, QLabel
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QTextCursor

from ..utils.logging_config import get_logger


logger = get_logger(__name__)


class LogLevel:
    """Log level constants for filtering."""
    ALL = "Todos"
    DEBUG = "Debug"
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"


class ConsolePanel(QWidget):
    """
    Console panel widget for displaying application logs.

    Features:
    - Display logs with auto-scroll
    - Filter logs by level
    - Clear console
    - Export logs to file
    - Configurable size
    """

    # Signal emitted when panel visibility changes
    visibility_changed = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the console panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._auto_scroll = True
        self._log_buffer = []  # Store all logs for filtering
        self._current_filter = LogLevel.ALL

        self._setup_ui()
        logger.debug("ConsolePanel initialized")

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header with controls
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("Console")
        title_label.setObjectName("consolePanelTitle")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Filter by level
        filter_label = QLabel("Nível:")
        header_layout.addWidget(filter_label)

        self.level_filter = QComboBox()
        self.level_filter.addItems([
            LogLevel.ALL,
            LogLevel.DEBUG,
            LogLevel.INFO,
            LogLevel.WARNING,
            LogLevel.ERROR
        ])
        self.level_filter.currentTextChanged.connect(self._on_filter_changed)
        self.level_filter.setObjectName("consoleLevelFilter")
        header_layout.addWidget(self.level_filter)

        # Clear button
        self.clear_button = QPushButton("🗑️ Limpar")
        self.clear_button.setObjectName("consoleButton")
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setToolTip("Limpar todos os logs")
        header_layout.addWidget(self.clear_button)

        # Export button
        self.export_button = QPushButton("💾 Exportar")
        self.export_button.setObjectName("consoleButton")
        self.export_button.clicked.connect(self.export_logs)
        self.export_button.setToolTip("Exportar logs para arquivo")
        header_layout.addWidget(self.export_button)

        layout.addLayout(header_layout)

        # Console text area
        self.console_text = QPlainTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setObjectName("consoleTextEdit")
        self.console_text.setMaximumBlockCount(1000)  # Limit to 1000 lines
        self.console_text.setPlaceholderText("Logs aparecerão aqui...")
        layout.addWidget(self.console_text)

        # Footer with status
        footer_layout = QHBoxLayout()

        self.status_label = QLabel("0 mensagens")
        self.status_label.setObjectName("consoleStatus")
        footer_layout.addWidget(self.status_label)

        footer_layout.addStretch()

        # Auto-scroll toggle (implicit - always on for now)
        layout.addLayout(footer_layout)

        self.setLayout(layout)

        # Set minimum height
        self.setMinimumHeight(150)

    def append_log(self, message: str, level: str = LogLevel.INFO) -> None:
        """
        Append a log message to the console.

        Args:
            message: Log message to display
            level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}"

        # Store in buffer with metadata
        self._log_buffer.append({
            "message": formatted_message,
            "level": level,
            "raw_message": message
        })

        # Apply filter and update display
        if self._should_display_log(level):
            self._append_to_display(formatted_message)

        # Update status
        self._update_status()

        logger.debug(f"Log appended: {level} - {message}")

    def _should_display_log(self, level: str) -> bool:
        """
        Check if a log should be displayed based on current filter.

        Args:
            level: Log level to check

        Returns:
            True if log should be displayed
        """
        if self._current_filter == LogLevel.ALL:
            return True
        return level == self._current_filter

    def _append_to_display(self, formatted_message: str) -> None:
        """
        Append formatted message to the display.

        Args:
            formatted_message: Formatted log message
        """
        self.console_text.appendPlainText(formatted_message)

        # Auto-scroll to bottom
        if self._auto_scroll:
            self.console_text.verticalScrollBar().setValue(
                self.console_text.verticalScrollBar().maximum()
            )

    def _on_filter_changed(self, filter_level: str) -> None:
        """
        Handle filter level change.

        Args:
            filter_level: New filter level
        """
        self._current_filter = filter_level
        self._apply_filter()
        logger.debug(f"Console filter changed to: {filter_level}")

    def _apply_filter(self) -> None:
        """Apply current filter to log buffer and refresh display."""
        self.console_text.clear()

        for log_entry in self._log_buffer:
            if self._should_display_log(log_entry["level"]):
                # Don't use append_to_display to avoid scrolling on each line
                self.console_text.appendPlainText(log_entry["message"])

        # Scroll to bottom after all messages added
        if self._auto_scroll:
            self.console_text.verticalScrollBar().setValue(
                self.console_text.verticalScrollBar().maximum()
            )

    def clear_logs(self) -> None:
        """Clear all logs from console and buffer."""
        self.console_text.clear()
        self._log_buffer.clear()
        self._update_status()
        logger.info("Console logs cleared")

    def export_logs(self) -> None:
        """Export logs to a text file."""
        if not self._log_buffer:
            logger.warning("No logs to export")
            return

        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Logs",
            f"mineru_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"MinerU Desktop Client - Log Export\n")
                    f.write(f"Exported at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 80 + "\n\n")

                    for log_entry in self._log_buffer:
                        f.write(log_entry["message"] + "\n")

                logger.info(f"Logs exported to: {file_path}")

                # Show success message (could be a toast notification)
                from .toast_notification import ToastNotification, ToastType
                ToastNotification.show_success(
                    self,
                    f"Logs exportados com sucesso!",
                    2000
                )

            except Exception as e:
                logger.error(f"Failed to export logs: {e}")
                from .toast_notification import ToastNotification, ToastType
                ToastNotification.show_error(
                    self,
                    f"Erro ao exportar logs: {str(e)}",
                    3000
                )

    def _update_status(self) -> None:
        """Update status label with current log count."""
        total_logs = len(self._log_buffer)

        if self._current_filter == LogLevel.ALL:
            self.status_label.setText(f"{total_logs} mensagens")
        else:
            filtered_count = len([
                log for log in self._log_buffer
                if log["level"] == self._current_filter
            ])
            self.status_label.setText(
                f"{filtered_count} de {total_logs} mensagens (filtrado por {self._current_filter})"
            )

    def set_auto_scroll(self, enabled: bool) -> None:
        """
        Enable or disable auto-scroll.

        Args:
            enabled: True to enable auto-scroll
        """
        self._auto_scroll = enabled
        logger.debug(f"Auto-scroll set to: {enabled}")

    def get_log_count(self) -> int:
        """
        Get the total number of logs.

        Returns:
            Total log count
        """
        return len(self._log_buffer)
