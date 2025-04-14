@echo off
echo ===== KITPASS INSTALLER =====
echo.
echo Qua trinh nay se giup ban tao file .exe va shortcut cho KITPass
echo.

echo === Buoc 1/3: Cai dat cac goi can thiet ===
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Loi khi cai dat cac goi can thiet!
    pause
    exit /b
)
echo.

echo === Kiem tra thu muc data ===
if not exist "data\" (
    echo Tao thu muc data...
    mkdir data
)
echo.

echo === Buoc 2/3: Tao file .exe ===
python tools\build_exe.py
if %ERRORLEVEL% NEQ 0 (
    echo Loi khi tao file .exe!
    pause
    exit /b
)
echo.

echo === Buoc 3/3: Tao shortcut tren Desktop ===
python tools\create_shortcut.py
if %ERRORLEVEL% NEQ 0 (
    echo Loi khi tao shortcut!
    pause
    exit /b
)
echo.

echo ===== QUA TRINH HOAN TAT =====
echo.
echo Ban co the chay KITPass bang cach:
echo 1. Click vao shortcut tren Desktop
echo 2. Truc tiep chay file KITPass.exe trong thu muc goc
echo.
echo Cam on ban da su dung KITPass!
echo.
pause 