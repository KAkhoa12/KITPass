import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from functools import partial
import os
import random
import string
import sys

# Đảm bảo đường dẫn tới thư mục data là chính xác
# Nếu chạy từ file .exe, data sẽ ở cùng thư mục
# Nếu chạy từ source, data sẽ ở thư mục gốc của dự án
current_dir = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, 'frozen', False):
    # Nếu đang chạy từ file đã được đóng gói bởi PyInstaller
    app_dir = os.path.dirname(sys.executable)
else:
    # Nếu đang chạy từ source
    app_dir = os.path.dirname(current_dir)  # Thư mục cha của src

from login import LoginWindow
from password_manager import PasswordManager

class KITPass:
    def __init__(self, root):
        self.root = root
        self.root.title("KITPass")
        
        # Cố định kích thước cửa sổ
        window_width = 1300
        window_height = 700
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(window_width, window_height)
        self.root.maxsize(window_width, window_height)
        self.root.resizable(False, False)
        
        # Đặt cửa sổ ở giữa màn hình
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_x = int((screen_width - window_width) / 2)
        position_y = int((screen_height - window_height) / 2)
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        
        # Khởi tạo database
        self.init_database()
        
        # Hiển thị màn hình đăng nhập
        self.show_login()
    
    def init_database(self):
        """Khởi tạo cơ sở dữ liệu nếu chưa tồn tại"""
        data_dir = os.path.join(app_dir, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        # Tạo database cho người dùng và mật khẩu
        db_path = os.path.join(data_dir, 'kitpass.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tạo bảng users
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Tạo bảng tabs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tabs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Tạo bảng entries (mật khẩu)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tab_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tab_id) REFERENCES tabs (id) ON DELETE CASCADE
        )
        ''')
        
        # Tạo bảng fields (các trường thông tin trong mỗi entry)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            label TEXT NOT NULL,
            value TEXT NOT NULL,
            is_password BOOLEAN DEFAULT 0,
            FOREIGN KEY (entry_id) REFERENCES entries (id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        conn.close()
        
        # Lưu lại đường dẫn để các module khác sử dụng
        global db_file_path
        db_file_path = db_path
    
    def show_login(self):
        """Hiển thị màn hình đăng nhập"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        login_window = LoginWindow(self.root, self.on_login_success)
    
    def on_login_success(self, user_id, username):
        """Callback khi đăng nhập thành công"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Chuyển sang giao diện quản lý mật khẩu
        self.password_manager = PasswordManager(self.root, user_id, username, self.show_login)

# Biến toàn cục để lưu đường dẫn tới file database
db_file_path = None

if __name__ == "__main__":
    root = tk.Tk()
    app = KITPass(root)
    root.mainloop() 