"""
Toast notification widget.

Provides non-intrusive popup notifications for user feedback.
"""

from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QFont
from enum import Enum


class ToastType(Enum):
    """Types of toast notifications."""

    INFO = "toast"
    SUCCESS = "toastSuccess"
    ERROR = "toastError"
    WARNING = "toastWarning"


class ToastNotification(QLabel):
    """
    Toast notification widget.

    Displays temporary notification messages at the bottom of the window.
    """

    def __init__(self, parent=None):
        """
        Initialize toast notification.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setMinimumWidth(250)
        self.setMaximumWidth(500)

        # Set font
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)

        # Initially hidden
        self.hide()

        # Opacity effect for fade animation
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        # Animation
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Auto-hide timer
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)

    def show_message(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration: int = 3000
    ) -> None:
        """
        Show a toast notification.

        Args:
            message: Message to display
            toast_type: Type of notification (info, success, error, warning)
            duration: Duration in milliseconds (default: 3000)
        """
        # Set message
        self.setText(message)

        # Set object name for styling
        self.setObjectName(toast_type.value)

        # Force style update
        self.style().unpolish(self)
        self.style().polish(self)

        # Position at bottom center of parent
        if self.parent():
            parent_rect = self.parent().rect()
            self.adjustSize()
            x = (parent_rect.width() - self.width()) // 2
            y = parent_rect.height() - self.height() - 50
            self.move(x, y)

        # Fade in
        self.show()
        self.raise_()

        self.fade_animation.stop()
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

        # Schedule hide
        self.hide_timer.stop()
        self.hide_timer.setInterval(duration)
        self.hide_timer.start()

    def fade_out(self) -> None:
        """Fade out and hide the toast."""
        self.fade_animation.stop()
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()

    @staticmethod
    def show_info(parent, message: str, duration: int = 3000) -> None:
        """
        Show an info toast notification.

        Args:
            parent: Parent widget
            message: Message to display
            duration: Duration in milliseconds
        """
        toast = ToastNotification(parent)
        toast.show_message(message, ToastType.INFO, duration)

    @staticmethod
    def show_success(parent, message: str, duration: int = 3000) -> None:
        """
        Show a success toast notification.

        Args:
            parent: Parent widget
            message: Message to display
            duration: Duration in milliseconds
        """
        toast = ToastNotification(parent)
        toast.show_message(message, ToastType.SUCCESS, duration)

    @staticmethod
    def show_error(parent, message: str, duration: int = 4000) -> None:
        """
        Show an error toast notification.

        Args:
            parent: Parent widget
            message: Message to display
            duration: Duration in milliseconds
        """
        toast = ToastNotification(parent)
        toast.show_message(message, ToastType.ERROR, duration)

    @staticmethod
    def show_warning(parent, message: str, duration: int = 3500) -> None:
        """
        Show a warning toast notification.

        Args:
            parent: Parent widget
            message: Message to display
            duration: Duration in milliseconds
        """
        toast = ToastNotification(parent)
        toast.show_message(message, ToastType.WARNING, duration)
