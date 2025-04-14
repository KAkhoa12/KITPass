@echo off
echo ===== DANG TAO SHORTCUT CHO KITPASS =====
echo.

cd /d %~dp0\..

pip install pywin32 winshell
python tools\create_shortcut.py
echo.
echo ===== HOAN THANH =====
echo.
pause 