import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import os
import random
import string
import sys

# Import từ main module
try:
    from main import db_file_path
except ImportError:
    # Nếu chạy trực tiếp file này
    db_file_path = None

class LoginWindow:
    def __init__(self, master, on_login_success):
        self.master = master
        self.on_login_success = on_login_success
        
        # Tạo frame chính
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Tạo container frame cho đăng nhập ở giữa màn hình
        self.login_container = tk.Frame(self.frame, padx=20, pady=20)
        self.login_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Tiêu đề
        self.title_label = tk.Label(self.login_container, text="KITPass", font=("Arial", 28, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Tạo form đăng nhập
        self.username_label = tk.Label(self.login_container, text="Tên đăng nhập:", font=("Arial", 12))
        self.username_label.grid(row=1, column=0, sticky=tk.W, pady=10)
        
        self.username_entry = tk.Entry(self.login_container, width=30, font=("Arial", 12))
        self.username_entry.grid(row=1, column=1, pady=10)
        
        self.password_label = tk.Label(self.login_container, text="Mật khẩu:", font=("Arial", 12))
        self.password_label.grid(row=2, column=0, sticky=tk.W, pady=10)
        
        self.password_entry = tk.Entry(self.login_container, width=30, show="*", font=("Arial", 12))
        self.password_entry.grid(row=2, column=1, pady=10)
        
        # Frame cho các nút
        self.button_frame = tk.Frame(self.login_container)
        self.button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Nút đăng nhập
        self.login_button = tk.Button(self.button_frame, text="Đăng nhập", width=12, 
                                     command=self.login, font=("Arial", 12))
        self.login_button.pack(side=tk.LEFT, padx=10)
        
        # Nút đăng ký
        self.register_button = tk.Button(self.button_frame, text="Đăng ký", width=12,
                                       command=self.show_register, font=("Arial", 12))
        self.register_button.pack(side=tk.LEFT, padx=10)
        
        # Bind Enter key cho việc đăng nhập
        self.master.bind('<Return>', lambda event: self.login())
    
    def show_alert(self, message, alert_type="info"):
        """Hiển thị thông báo alert với màu sắc tương ứng
        
        Args:
            message: Nội dung thông báo
            alert_type: Loại thông báo ('success', 'error', 'info')
        """
        # Xác định màu sắc dựa trên loại thông báo
        if alert_type == "success":
            bg_color = "#4CAF50"  # Xanh lá
        elif alert_type == "error":
            bg_color = "#F44336"  # Đỏ
        else:  # info
            bg_color = "#4a7abc"  # Xanh dương
            
        # Hiển thị toast alert
        toast = tk.Toplevel(self.master)
        toast.overrideredirect(True)  # Bỏ tiêu đề và viền
        
        # Tính vị trí để hiển thị ở góc dưới bên phải
        toast_width = 300
        toast_height = 50
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_position = screen_width - toast_width - 20
        y_position = screen_height - toast_height - 60
        
        toast.geometry(f"{toast_width}x{toast_height}+{x_position}+{y_position}")
        toast.configure(background=bg_color)
        
        # Thêm nhãn thông báo
        label = tk.Label(toast, text=message, background=bg_color, foreground="white",
                      font=("Arial", 11), wraplength=280, padx=10, pady=10)
        label.pack(fill=tk.BOTH, expand=True)
        
        # Tự động đóng sau 3 giây
        toast.after(3000, toast.destroy)
    
    def get_db_path(self):
        """Lấy đường dẫn đến file database"""
        if db_file_path:
            return db_file_path
            
        # Xác định đường dẫn dựa trên vị trí hiện tại của ứng dụng
        if getattr(sys, 'frozen', False):
            # Nếu đang chạy từ file đã được đóng gói bởi PyInstaller
            app_dir = os.path.dirname(sys.executable)
        else:
            # Nếu đang chạy từ source
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        return os.path.join(app_dir, 'data', 'kitpass.db')
    
    def login(self):
        """Xử lý đăng nhập"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_alert("Vui lòng nhập đầy đủ thông tin!", "error")
            return
        
        # Kiểm tra thông tin đăng nhập
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        
        # Lấy thông tin người dùng
        cursor.execute("SELECT id, password, salt FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user:
            user_id, hashed_password, salt = user
            # Băm mật khẩu với salt
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            if password_hash == hashed_password:
                conn.close()
                self.show_alert(f"Đăng nhập thành công! Xin chào {username}", "success")
                self.master.after(1000, lambda: self.on_login_success(user_id, username))
            else:
                self.show_alert("Mật khẩu không chính xác!", "error")
        else:
            self.show_alert("Tài khoản không tồn tại!", "error")
        
        conn.close()
    
    def show_register(self):
        """Hiển thị cửa sổ đăng ký"""
        register_window = tk.Toplevel(self.master)
        register_window.title("Đăng ký")
        register_window.geometry("500x300")
        register_window.transient(self.master)
        register_window.grab_set()
        register_window.resizable(False, False)  # Không cho phép thay đổi kích thước
        
        # Đặt cửa sổ ở giữa màn hình
        window_width = 500
        window_height = 300
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        position_x = int((screen_width - window_width) / 2)
        position_y = int((screen_height - window_height) / 2)
        register_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        
        # Container
        container = tk.Frame(register_window, padx=30, pady=30)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        title_label = tk.Label(container, text="Đăng ký tài khoản", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 25))
        
        # Tên đăng nhập
        username_label = tk.Label(container, text="Tên đăng nhập:", font=("Arial", 12))
        username_label.grid(row=1, column=0, sticky=tk.W, pady=8)
        
        username_entry = tk.Entry(container, width=30, font=("Arial", 12))
        username_entry.grid(row=1, column=1, pady=8)
        
        # Mật khẩu
        password_label = tk.Label(container, text="Mật khẩu:", font=("Arial", 12))
        password_label.grid(row=2, column=0, sticky=tk.W, pady=8)
        
        password_entry = tk.Entry(container, width=30, show="*", font=("Arial", 12))
        password_entry.grid(row=2, column=1, pady=8)
        
        # Xác nhận mật khẩu
        confirm_label = tk.Label(container, text="Xác nhận mật khẩu:", font=("Arial", 12))
        confirm_label.grid(row=3, column=0, sticky=tk.W, pady=8)
        
        confirm_entry = tk.Entry(container, width=30, show="*", font=("Arial", 12))
        confirm_entry.grid(row=3, column=1, pady=8)
        
        # Nút đăng ký
        def register():
            username = username_entry.get()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            if not username or not password or not confirm:
                self.show_alert("Vui lòng nhập đầy đủ thông tin!", "error")
                return
            
            if password != confirm:
                self.show_alert("Mật khẩu xác nhận không khớp!", "error")
                return
            
            # Kiểm tra xem username đã tồn tại chưa
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                self.show_alert("Tên đăng nhập đã tồn tại!", "error")
                conn.close()
                return
            
            # Tạo salt ngẫu nhiên
            salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
            
            # Băm mật khẩu
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            # Thêm người dùng vào database
            cursor.execute("INSERT INTO users (username, password, salt) VALUES (?, ?, ?)", 
                          (username, password_hash, salt))
            
            # Lấy ID của người dùng vừa tạo
            user_id = cursor.lastrowid
            
            # Tạo tab mặc định cho người dùng mới
            cursor.execute("INSERT INTO tabs (user_id, name) VALUES (?, ?)", 
                          (user_id, "General"))
            
            conn.commit()
            conn.close()
            
            self.show_alert("Đăng ký tài khoản thành công!", "success")
            register_window.destroy()
        
        register_btn = tk.Button(container, text="Đăng ký", width=12, command=register, font=("Arial", 12))
        register_btn.grid(row=4, column=0, columnspan=2, pady=20) 