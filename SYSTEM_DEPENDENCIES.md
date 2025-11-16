# System Dependencies for MinerU Linux Desktop

This document lists the system-level dependencies required to run the MinerU Desktop Client on Linux.

## Required System Packages

The application uses PySide6 (Qt 6) which requires several system libraries to function properly.

### Ubuntu/Debian

Install the following packages using apt:

```bash
# Core Qt dependencies
apt-get install -y \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-keysyms1 \
    libxcb-shape0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libegl1
```

### Why These Are Needed

- **libxcb-cursor0**: Required by Qt 6.5.0+ for the xcb platform plugin
- **libxcb-icccm4**: X11 Inter-Client Communication Conventions Manual library
- **libxcb-keysyms1**: Keyboard symbol handling for X11
- **libxcb-shape0**: X11 Shape extension library
- **libxcb-xkb1**: X11 keyboard extension library
- **libxkbcommon-x11-0**: X11 keyboard handling library
- **libegl1**: OpenGL ES rendering library required by Qt

## Installation Instructions

### Quick Install

Run the installation script:

```bash
./install_system_deps.sh
```

### Manual Installation

If you prefer to install manually:

```bash
# Update package list
apt-get update

# Install all required dependencies
apt-get install -y libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 \
    libxcb-shape0 libxcb-xkb1 libxkbcommon-x11-0 libegl1
```

## Troubleshooting

### Error: "Could not load the Qt platform plugin 'xcb'"

This error occurs when one or more of the above system libraries is missing. Run:

```bash
# Check which libraries are missing
ldd /path/to/PySide6/Qt/plugins/platforms/libqxcb.so | grep "not found"
```

Then install the missing packages as shown above.

### Error: "could not connect to display"

This is expected if you're running in a headless environment (no X server). To run without a display:

```bash
QT_QPA_PLATFORM=offscreen python main.py
```

## Tested On

- Ubuntu 24.04.3 LTS (Noble Numbat)
- PySide6 6.10.0
