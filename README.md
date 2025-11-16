# MinerU Linux Desktop Client

A desktop client for MinerU on Linux systems.

## Overview

This project provides a user-friendly desktop interface for MinerU, enabling efficient document processing and mining operations on Linux platforms.

## Features

- Desktop GUI built with PySide6
- API token management with secure storage
- Configurable processing options:
  - Force OCR
  - Formula recognition
  - Table recognition
  - Multi-language support (Chinese, English, Portuguese)
- Document processing capabilities
- Linux compatibility

## Installation

### Requirements

- Python 3.8 or higher
- Linux operating system

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ozp/MinerU-linux-desktop.git
cd MinerU-linux-desktop
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Configure your API settings:
   - Go to **File > Settings** (or press `Ctrl+,`)
   - Enter your MinerU API token
   - Configure processing options (OCR, formula recognition, table recognition)
   - Select your preferred OCR language
   - Click **Save**

3. Start processing documents (coming soon)

## Configuration

Settings are stored locally in `config.ini` (automatically created). This file contains:
- API token (stored securely, not versioned in git)
- Processing preferences
- Language settings

## License

To be determined.
