@echo off
echo Building Cellular TTL Utility for Windows...
pip install pyinstaller
pyinstaller --onefile --noconsole --name "CellularTTL" ttl_utility.py
echo Build complete! Check the 'dist' folder.
pause
