#!/bin/bash
echo "Building Cellular TTL Utility for macOS/Linux..."
pip install pyinstaller
pyinstaller --windowed --onefile --name "CellularTTL" ttl_utility.py
echo "Build complete! Check the 'dist' folder."
