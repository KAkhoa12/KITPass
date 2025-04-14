@echo off
echo ===== Dang tao file thuc thi KITPass.exe =====
echo.

cd /d %~dp0\..

echo Installing required packages...
pip install -r requirements.txt
echo.

echo Kiem tra thu muc data...
if not exist "data\" (
    echo Tao thu muc data...
    mkdir data
)

echo.
echo Building executable...
python tools\build_exe.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Co loi xay ra khi tao file .exe
    echo Vui long thu lai sau hoac lien he ho tro
    pause
    exit /b
)

echo.
echo ===== BUILD HOAN THANH =====
echo File .exe da duoc tao trong thu muc goc
echo.
pause 