import os
import sys
import subprocess
import platform
import shutil

# Đường dẫn tới thư mục gốc của dự án
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Đường dẫn tới thư mục src
src_dir = os.path.join(project_root, 'src')

# Thêm thư mục src vào sys.path
sys.path.insert(0, src_dir)

# Đường dẫn tới thư mục data
data_dir = os.path.join(project_root, 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    print(f"Đã tạo thư mục data tại: {data_dir}")

# Kiểm tra hệ điều hành để xác định cú pháp cho --add-data
separator = ';' if platform.system() == 'Windows' else ':'

# Đường dẫn tới thư mục dist
dist_dir = os.path.join(project_root, 'dist')

# Tạo lệnh PyInstaller
pyinstaller_cmd = [
    'pyinstaller',
    f'--name=KITPass',  # Tên của file .exe
    '--onefile',  # Đóng gói thành một file .exe duy nhất
    '--windowed',  # Không hiển thị cửa sổ console
    '--clean',  # Xóa các file tạm trước khi build
    f'--add-data={data_dir}{separator}data',  # Thêm thư mục data vào file .exe
    '--hidden-import=pyperclip',  # Import ẩn
    '--distpath', dist_dir,  # Đường dẫn output
    '--workpath', os.path.join(project_root, 'build'),  # Thư mục build
    '--specpath', project_root,  # Thư mục spec
    os.path.join(src_dir, 'main.py')  # Tệp chính để biên dịch
]

# Thực thi lệnh PyInstaller
try:
    subprocess.run(pyinstaller_cmd, check=True)
    print("Build hoàn thành! File .exe có trong thư mục dist/")
    
    # Di chuyển file .exe ra thư mục gốc
    exe_path = os.path.join(dist_dir, 'KITPass.exe')
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, project_root)
        print(f"Đã sao chép file KITPass.exe vào thư mục gốc: {project_root}")
except subprocess.CalledProcessError as e:
    print(f"Lỗi trong quá trình build: {e}")
    sys.exit(1) 