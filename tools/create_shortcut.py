import os
import sys
import winshell
from win32com.client import Dispatch

def create_shortcut(exe_path, shortcut_path, icon_path=None):
    """Tạo shortcut cho file .exe"""
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = exe_path
    shortcut.WorkingDirectory = os.path.dirname(exe_path)
    
    if icon_path:
        shortcut.IconLocation = icon_path
    
    shortcut.save()
    print(f"Đã tạo shortcut tại: {shortcut_path}")

if __name__ == "__main__":
    # Đường dẫn tới thư mục gốc của dự án
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Đường dẫn tới file .exe trong thư mục gốc
    exe_path = os.path.join(project_root, "KITPass.exe")
    
    # Kiểm tra nếu không tìm thấy file .exe ở thư mục gốc, thử tìm trong thư mục dist
    if not os.path.exists(exe_path):
        exe_path = os.path.join(project_root, "dist", "KITPass.exe")
        
    if not os.path.exists(exe_path):
        print("Không tìm thấy file KITPass.exe!")
        print("Vui lòng chạy build_exe.bat trước để tạo file .exe")
        sys.exit(1)
    
    # Tạo shortcut trên Desktop
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, "KITPass.lnk")
    
    # Tạo shortcut
    create_shortcut(exe_path, shortcut_path)
    
    print("\nQuá trình hoàn tất!")
    print(f"Bạn có thể chạy KITPass từ Desktop hoặc trực tiếp từ file: {exe_path}") 