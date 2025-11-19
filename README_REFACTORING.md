# MinerU Desktop Client - Refactoring Documentation

## 🎯 Overview

This document describes the comprehensive refactoring performed on the MinerU Desktop Client, transforming it from a monolithic application into a modern, maintainable, and user-friendly desktop application.

## 📋 What Was Changed

### Architecture Improvements

#### Before
- Single `main.py` file with 520+ lines mixing UI and business logic
- No separation of concerns
- Direct API calls from UI code
- Print statements for debugging
- No structured logging

#### After
```
mineru_desktop/
├── core/           # Core functionality
│   ├── client.py   # API client (refactored with type hints)
│   └── config.py   # Configuration management
├── models/         # Data models
│   └── batch.py    # Batch, FileStatus, ProcessingOptions
├── services/       # Business logic layer
│   ├── upload_service.py
│   ├── download_service.py
│   └── batch_service.py
├── workers/        # Background threads
│   └── upload_worker.py
├── ui/             # User interface
│   ├── main_window.py
│   ├── settings_dialog.py
│   ├── toast_notification.py
│   └── styles/
│       ├── light_theme.qss
│       └── dark_theme.qss
└── utils/          # Utilities
    └── logging_config.py
```

### Code Quality Improvements

1. **Type Hints**: All functions now have complete type annotations
2. **Logging**: Structured logging with file output to `~/.local/share/MinerU/mineru_desktop.log`
3. **Docstrings**: Google-style docstrings for all classes and methods
4. **SOLID Principles**: Proper separation of concerns
5. **DRY**: Eliminated code duplication

### New Features

#### 1. Drag & Drop Support
- Files can now be dragged directly into the application
- Visual feedback during drag operations
- Automatic file validation

#### 2. Toast Notifications
- Non-intrusive popup notifications
- Four types: Info, Success, Error, Warning
- Auto-fade animations
- Better user feedback

#### 3. Dark/Light Theme Support
- Modern, professionally designed themes
- Smooth theme switching
- Theme preference persistence
- Menu option: "View → Toggle Theme"

#### 4. Enhanced UI/UX
- Material Design inspired interface
- Improved button styling with icons
- Better visual feedback
- Rounded corners and modern aesthetics
- Consistent spacing and padding

#### 5. Better Error Handling
- Structured exception handling
- User-friendly error messages
- Detailed logging for debugging
- Graceful degradation

## 🔧 Technical Details

### Models

**ProcessingOptions**
```python
@dataclass
class ProcessingOptions:
    is_ocr: bool = True
    enable_formula: bool = False
    enable_table: bool = True
    language: Language = Language.PORTUGUESE
    model_version: ModelVersion = ModelVersion.PIPELINE
```

**FileStatus**
```python
@dataclass
class FileStatus:
    filename: str
    file_path: str
    state: FileState = FileState.READY
    error_message: Optional[str] = None
    # ... more fields
```

**Batch**
```python
@dataclass
class Batch:
    batch_id: Optional[str] = None
    files: List[FileStatus] = field(default_factory=list)
    processing_options: ProcessingOptions = field(default_factory=ProcessingOptions)
    # ... more fields
```

### Services Layer

**UploadService**: Handles file uploads
- Manages batch uploads
- Updates file states
- Progress callbacks

**BatchService**: Manages batch status
- Polls API for status
- Downloads completed files
- Extracts ZIP results

**DownloadService**: Handles downloads
- Downloads result files
- Manages output directory

### Configuration Management

**ConfigManager**: Centralized configuration
- API token (stored in system keyring)
- Processing options (config.ini)
- Output directory
- Theme preference

### Logging

Structured logging with:
- Console output
- File output (`~/.local/share/MinerU/mineru_desktop.log`)
- Automatic log rotation
- Different log levels per module

## 🎨 UI Improvements

### Light Theme
- Clean, modern appearance
- Blue accent color (#3498db)
- White backgrounds
- Good contrast for readability

### Dark Theme
- Eye-friendly dark colors
- Teal accent color (#0d7377)
- Neon highlights (#14ffec)
- Perfect for low-light environments

### Responsive Design
- Adapts to different window sizes
- Minimum size constraints
- Proper spacing and margins

## 🚀 Running the Refactored Application

### Development Mode
```bash
python run.py
```

### Checking Logs
```bash
tail -f ~/.local/share/MinerU/mineru_desktop.log
```

## 📦 Building

The existing build process remains the same:
```bash
./build_appimage.sh
```

## 🔄 Migration Guide

### For Developers

The old files (`main.py`, `mineru_client.py`, `settings_dialog.py`) are preserved for reference but are no longer used. The new entry point is `run.py`.

### For Users

No changes needed! The application works exactly the same way, but with:
- Better performance
- More features
- Better error handling
- Modern UI

## 📝 Future Improvements

Potential enhancements:
1. Unit tests for services and models
2. Integration tests for API client
3. i18n/l10n for multiple languages
4. History/recent files feature
5. Batch processing history
6. Export processing reports
7. Keyboard shortcuts
8. Custom themes

## 🐛 Debugging

Enable debug logging:
```python
setup_logging(level=logging.DEBUG)
```

Check logs at: `~/.local/share/MinerU/mineru_desktop.log`

## 📚 Code Examples

### Adding a new service
```python
from mineru_desktop.services.base_service import BaseService

class MyService(BaseService):
    def __init__(self, client: MineruClient):
        self.client = client
        self.logger = get_logger(__name__)

    def do_something(self):
        self.logger.info("Doing something")
        # Implementation
```

### Using toast notifications
```python
from mineru_desktop.ui.toast_notification import ToastNotification

# Show success
ToastNotification.show_success(self, "Operation completed!")

# Show error
ToastNotification.show_error(self, "Something went wrong")
```

### Loading configuration
```python
from mineru_desktop.core.config import ConfigManager

config = ConfigManager()
token = config.load_api_token()
options = config.load_processing_options()
```

## 🎯 Design Principles Applied

1. **SOLID**
   - Single Responsibility: Each class has one job
   - Open/Closed: Easy to extend without modifying
   - Liskov Substitution: Proper inheritance
   - Interface Segregation: Focused interfaces
   - Dependency Inversion: Depend on abstractions

2. **Clean Code**
   - Meaningful names
   - Small functions
   - DRY (Don't Repeat Yourself)
   - Clear comments and docstrings

3. **Separation of Concerns**
   - UI separated from business logic
   - Services handle business operations
   - Models represent data
   - Workers handle background tasks

## 🙏 Acknowledgments

This refactoring was performed following best practices from:
- PEP 8 (Python Style Guide)
- Google Python Style Guide
- Qt Best Practices
- Material Design Guidelines
