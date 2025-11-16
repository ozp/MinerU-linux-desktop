#!/bin/bash
# Installation script for MinerU Linux Desktop system dependencies
# This script installs the required system libraries for Qt/PySide6 on Ubuntu/Debian

set -e  # Exit on error

echo "==================================="
echo "MinerU Desktop - System Dependencies Installer"
echo "==================================="
echo ""

# Check if running on Ubuntu/Debian
if ! command -v apt-get &> /dev/null; then
    echo "Error: This script is designed for Ubuntu/Debian systems."
    echo "Please install the dependencies manually for your distribution."
    exit 1
fi

echo "Installing Qt/PySide6 system dependencies..."
echo ""

# List of required packages
PACKAGES=(
    libxcb-cursor0
    libxcb-icccm4
    libxcb-keysyms1
    libxcb-shape0
    libxcb-xkb1
    libxkbcommon-x11-0
    libegl1
)

# Update package list
echo "Updating package list..."
apt-get update

# Install packages
echo "Installing packages:"
for pkg in "${PACKAGES[@]}"; do
    echo "  - $pkg"
done
echo ""

apt-get install -y "${PACKAGES[@]}"

echo ""
echo "==================================="
echo "✓ System dependencies installed successfully!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Run the application: python main.py"
echo ""
