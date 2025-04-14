import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
from functools import partial
import random
import string
import pyperclip
import os
import sys
import json
import datetime
import base64

# Import từ main module
try:
    from main import db_file_path
except ImportError:
    # Nếu chạy trực tiếp file này
    db_file_path = None

class PasswordManager:
    def __init__(self, master, user_id, username, logout_callback):
        self.master = master
        self.user_id = user_id
        self.username = username
        self.logout_callback = logout_callback
        self.current_tab_id = None
        self.current_entry_id = None
        self.tab_buttons = {}  # Lưu trữ các nút tab để có thể thay đổi trạng thái
        
        # Thiết lập style cho các thành phần
        self.setup_styles()
        
        # Thiết lập giao diện chính
        self.setup_ui()
        
        # Load tabs của người dùng
        self.load_tabs()
    
    def setup_styles(self):
        """Thiết lập style cho các thành phần UI"""
        # Tạo style cho Treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        
        # Style cho nút tab được chọn
        self.selected_tab_bg = "#4a7abc"
        self.selected_tab_fg = "white"
        self.normal_tab_bg = "SystemButtonFace"
        self.normal_tab_fg = "black"
    
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
    
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        # Frame chính
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tạo thanh công cụ
        self.toolbar = tk.Frame(self.main_frame, pady=5, padx=5, borderwidth=1, relief=tk.RIDGE)
        self.toolbar.pack(fill=tk.X)
        
        # Thông tin người dùng
        self.user_label = tk.Label(self.toolbar, text=f"Người dùng: {self.username}", font=("Arial", 10))
        self.user_label.pack(side=tk.LEFT, padx=5)
        
        # Thêm nút backup và import
        self.backup_button = tk.Button(self.toolbar, text="Backup Data", command=self.backup_data, 
                                     padx=10, font=("Arial", 10))
        self.backup_button.pack(side=tk.LEFT, padx=10)
        
        self.import_button = tk.Button(self.toolbar, text="Import Data", command=self.import_data, 
                                     padx=10, font=("Arial", 10))
        self.import_button.pack(side=tk.LEFT, padx=10)
        
        # Nút đăng xuất
        self.logout_button = tk.Button(self.toolbar, text="Đăng xuất", command=self.logout, 
                                     padx=10, font=("Arial", 10))
        self.logout_button.pack(side=tk.RIGHT, padx=5)
        
        # Tạo khung nội dung chính với tỷ lệ mới: 3:5:4 (3 cột + 5 cột + 4 cột)
        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo frame cho danh sách tab (3 cột)
        self.tabs_frame = tk.Frame(self.content_frame, width=300, borderwidth=1, relief=tk.RIDGE)
        self.tabs_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.tabs_frame.pack_propagate(False)
        
        # Tiêu đề cho tabs
        tk.Label(self.tabs_frame, text="Danh mục", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5, padx=5)
        
        # Frame cho các nút thao tác với tabs
        self.tabs_button_frame = tk.Frame(self.tabs_frame)
        self.tabs_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Nút thêm tab mới
        self.add_tab_button = tk.Button(self.tabs_button_frame, text="Thêm danh mục", command=self.add_tab,
                                      font=("Arial", 10))
        self.add_tab_button.pack(side=tk.LEFT, padx=2)
        
        # Nút xóa tab
        self.delete_tab_button = tk.Button(self.tabs_button_frame, text="Xóa", command=self.delete_tab, 
                                         state=tk.DISABLED, font=("Arial", 10))
        self.delete_tab_button.pack(side=tk.LEFT, padx=2)
        
        # Nút đổi tên tab
        self.rename_tab_button = tk.Button(self.tabs_button_frame, text="Đổi tên", command=self.rename_tab, 
                                        state=tk.DISABLED, font=("Arial", 10))
        self.rename_tab_button.pack(side=tk.LEFT, padx=2)
        
        # Frame chứa danh sách tab
        self.tabs_list_frame = tk.Frame(self.tabs_frame)
        self.tabs_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tạo frame cho nội dung danh sách mật khẩu (5 cột thay vì 6 cột)
        # Sử dụng weight để điều chỉnh tỷ lệ trọng số
        self.entries_frame = tk.Frame(self.content_frame, borderwidth=1, relief=tk.RIDGE, width=500)
        self.entries_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Hiển thị tiêu đề và nút thao tác với entries
        self.entries_header_frame = tk.Frame(self.entries_frame)
        self.entries_header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Tiêu đề entries
        self.entries_title = tk.Label(self.entries_header_frame, text="Chưa chọn danh mục", 
                                    font=("Arial", 12, "bold"))
        self.entries_title.pack(side=tk.LEFT)
        
        # Frame chứa các nút thao tác entries
        self.entries_button_frame = tk.Frame(self.entries_header_frame)
        self.entries_button_frame.pack(side=tk.RIGHT)
        
        # Nút thêm entry mới
        self.add_entry_button = tk.Button(self.entries_button_frame, text="Thêm mật khẩu", 
                                        command=self.add_entry, state=tk.DISABLED, font=("Arial", 10))
        self.add_entry_button.pack(side=tk.LEFT, padx=2)
        
        # Nút xóa entry
        self.delete_entry_button = tk.Button(self.entries_button_frame, text="Xóa", 
                                          command=self.delete_entry, state=tk.DISABLED, font=("Arial", 10))
        self.delete_entry_button.pack(side=tk.LEFT, padx=2)
        
        # Tạo frame chứa danh sách entries
        self.entries_list_frame = tk.Frame(self.entries_frame)
        self.entries_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tạo Treeview cho entries
        self.entries_tree = ttk.Treeview(self.entries_list_frame, columns=("title", "created_at"), 
                                       show="headings", selectmode="browse")
        self.entries_tree.heading("title", text="Tiêu đề")
        self.entries_tree.heading("created_at", text="Ngày tạo")
        self.entries_tree.column("title", width=250)
        self.entries_tree.column("created_at", width=150)
        self.entries_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Thêm scrollbar cho entries
        entries_scrollbar = ttk.Scrollbar(self.entries_list_frame, orient=tk.VERTICAL, command=self.entries_tree.yview)
        entries_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.entries_tree.configure(yscrollcommand=entries_scrollbar.set)
        
        # Bind sự kiện khi chọn entry
        self.entries_tree.bind("<<TreeviewSelect>>", self.on_entry_selected)
        
        # Tạo frame cho thông tin chi tiết (4 cột thay vì 3 cột)
        # Sử dụng width để điều chỉnh kích thước
        self.details_frame = tk.Frame(self.content_frame, borderwidth=1, relief=tk.RIDGE, width=400)
        self.details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tiêu đề cho frame thông tin chi tiết
        self.details_title = tk.Label(self.details_frame, text="Chi tiết", font=("Arial", 12, "bold"))
        self.details_title.pack(anchor=tk.W, pady=5, padx=10)
        
        # Tạo frame để hiển thị thông tin chi tiết của entry
        self.entry_details_frame = tk.Frame(self.details_frame, padx=10, pady=5)
        self.entry_details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Hiển thị "Chưa có thông tin" khi chưa chọn entry
        self.display_no_info()
    
    def display_no_info(self):
        """Hiển thị thông báo khi chưa có thông tin"""
        # Xóa các widget cũ
        self.clear_entry_details()
        
        # Hiển thị thông báo
        no_info_label = tk.Label(self.entry_details_frame, text="Chưa có thông tin", 
                               font=("Arial", 12), fg="gray")
        no_info_label.pack(expand=True, pady=20)
    
    def load_tabs(self):
        """Load danh sách tabs từ database"""
        # Xóa các tab cũ và reset dictionary
        for widget in self.tabs_list_frame.winfo_children():
            widget.destroy()
        self.tab_buttons = {}
        
        # Lấy danh sách tab từ database
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name FROM tabs WHERE user_id = ? ORDER BY name", (self.user_id,))
        tabs = cursor.fetchall()
        
        conn.close()
        
        if not tabs:
            # Nếu không có tab nào, tạo một tab mặc định
            self.create_default_tab()
            self.load_tabs()  # Tải lại danh sách tabs
            return
        
        # Tạo các nút tab
        for tab_id, tab_name in tabs:
            tab_id_str = str(tab_id)  # Chuyển đổi thành string để làm key
            button = tk.Button(
                self.tabs_list_frame, 
                text=tab_name, 
                anchor=tk.W,
                width=25, 
                padx=5, 
                pady=3,
                font=("Arial", 10),
                command=partial(self.select_tab, tab_id, tab_name)
            )
            button.pack(fill=tk.X, pady=1)
            
            # Lưu button vào dictionary
            self.tab_buttons[tab_id_str] = button

    def select_tab(self, tab_id, tab_name):
        """Chọn tab và hiển thị nội dung"""
        # Reset màu tất cả các tab
        for btn in self.tab_buttons.values():
            btn.config(bg=self.normal_tab_bg, fg=self.normal_tab_fg)
        
        # Làm nổi bật tab được chọn
        tab_id_str = str(tab_id)
        if tab_id_str in self.tab_buttons:
            self.tab_buttons[tab_id_str].config(bg=self.selected_tab_bg, fg=self.selected_tab_fg)
        
        self.current_tab_id = tab_id
        self.entries_title.config(text=tab_name)
        
        # Kích hoạt các nút
        self.add_entry_button.config(state=tk.NORMAL)
        self.delete_tab_button.config(state=tk.NORMAL)
        self.rename_tab_button.config(state=tk.NORMAL)
        
        # Tải danh sách entries
        self.load_entries()
        
        # Xóa thông tin chi tiết nếu có
        self.display_no_info()
    
    def rename_tab(self):
        """Đổi tên tab hiện tại"""
        if not self.current_tab_id:
            return
            
        # Lấy tên tab hiện tại
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM tabs WHERE id = ?", (self.current_tab_id,))
        current_name = cursor.fetchone()[0]
        conn.close()
        
        # Hiển thị dialog để nhập tên mới
        new_name = simpledialog.askstring("Đổi tên danh mục", 
                                        "Nhập tên mới cho danh mục:", 
                                        initialvalue=current_name)
        
        if not new_name or new_name == current_name:
            return
            
        # Kiểm tra trùng tên
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM tabs 
            WHERE user_id = ? AND name = ? AND id != ?
        """, (self.user_id, new_name, self.current_tab_id))
        
        if cursor.fetchone():
            self.show_alert("Tên danh mục đã tồn tại!", "error")
            conn.close()
            return
        
        # Cập nhật tên mới
        cursor.execute("UPDATE tabs SET name = ? WHERE id = ?", (new_name, self.current_tab_id))
        conn.commit()
        conn.close()
        
        # Cập nhật giao diện
        self.entries_title.config(text=new_name)
        self.tab_buttons[str(self.current_tab_id)].config(text=new_name)
        self.show_alert("Đã đổi tên danh mục thành công", "success")
    
    def backup_data(self):
        """Sao lưu dữ liệu"""
        # Mở dialog để chọn vị trí lưu file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".kpbak",
            filetypes=[("KITPass Backup", "*.kpbak"), ("All Files", "*.*")],
            title="Lưu file backup"
        )
        
        if not file_path:
            return
            
        try:
            # Lấy dữ liệu từ database
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            # Lấy tabs của người dùng
            cursor.execute("SELECT id, name FROM tabs WHERE user_id = ?", (self.user_id,))
            tabs = cursor.fetchall()
            
            backup_data = {
                "user_id": self.user_id,
                "username": self.username,
                "backup_date": datetime.datetime.now().isoformat(),
                "tabs": []
            }
            
            # Lấy dữ liệu cho mỗi tab
            for tab_id, tab_name in tabs:
                tab_data = {
                    "id": tab_id,
                    "name": tab_name,
                    "entries": []
                }
                
                # Lấy entries trong tab
                cursor.execute("SELECT id, title, created_at FROM entries WHERE tab_id = ?", (tab_id,))
                entries = cursor.fetchall()
                
                for entry_id, title, created_at in entries:
                    entry_data = {
                        "id": entry_id,
                        "title": title,
                        "created_at": created_at,
                        "fields": []
                    }
                    
                    # Lấy fields trong entry
                    cursor.execute("""
                        SELECT label, value, is_password FROM fields 
                        WHERE entry_id = ? ORDER BY id
                    """, (entry_id,))
                    
                    fields = cursor.fetchall()
                    
                    for label, value, is_password in fields:
                        # Mã hóa mật khẩu để bảo vệ thông tin
                        if is_password:
                            encoded_value = base64.b64encode(value.encode()).decode()
                        else:
                            encoded_value = value
                            
                        field_data = {
                            "label": label,
                            "value": encoded_value,
                            "is_password": is_password
                        }
                        
                        entry_data["fields"].append(field_data)
                    
                    tab_data["entries"].append(entry_data)
                
                backup_data["tabs"].append(tab_data)
            
            conn.close()
            
            # Lưu dữ liệu ra file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=4)
            
            self.show_alert("Đã sao lưu dữ liệu thành công!", "success")
            
        except Exception as e:
            self.show_alert(f"Có lỗi xảy ra khi sao lưu dữ liệu: {str(e)}", "error")
    
    def import_data(self):
        """Nhập dữ liệu từ file backup"""
        # Mở dialog để chọn file
        file_path = filedialog.askopenfilename(
            filetypes=[("KITPass Backup", "*.kpbak"), ("All Files", "*.*")],
            title="Chọn file backup"
        )
        
        if not file_path:
            return
            
        try:
            # Đọc dữ liệu từ file
            with open(file_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Kiểm tra dữ liệu
            if "tabs" not in backup_data:
                self.show_alert("File backup không hợp lệ!", "error")
                return
                
            # Xác nhận từ người dùng
            confirm = messagebox.askyesno(
                "Xác nhận", 
                "Nhập dữ liệu sẽ thêm các danh mục và mật khẩu từ file backup. Tiếp tục?"
            )
            
            if not confirm:
                return
                
            # Bắt đầu nhập dữ liệu
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            # Đếm số lượng các mục đã nhập
            tabs_imported = 0
            entries_imported = 0
            
            # Nhập tabs
            for tab in backup_data["tabs"]:
                tab_name = tab["name"]
                
                # Kiểm tra xem tab đã tồn tại chưa
                cursor.execute("""
                    SELECT id FROM tabs 
                    WHERE user_id = ? AND name = ?
                """, (self.user_id, tab_name))
                
                existing_tab = cursor.fetchone()
                
                if existing_tab:
                    # Nếu tab đã tồn tại, sử dụng tab này
                    tab_id = existing_tab[0]
                else:
                    # Tạo tab mới
                    cursor.execute("""
                        INSERT INTO tabs (user_id, name) VALUES (?, ?)
                    """, (self.user_id, tab_name))
                    tab_id = cursor.lastrowid
                    tabs_imported += 1
                
                # Nhập entries
                for entry in tab["entries"]:
                    title = entry["title"]
                    
                    # Tạo entry mới
                    cursor.execute("""
                        INSERT INTO entries (tab_id, title) VALUES (?, ?)
                    """, (tab_id, title))
                    
                    entry_id = cursor.lastrowid
                    entries_imported += 1
                    
                    # Nhập fields
                    for field in entry["fields"]:
                        label = field["label"]
                        encoded_value = field["value"]
                        is_password = field["is_password"]
                        
                        # Giải mã mật khẩu
                        if is_password:
                            try:
                                value = base64.b64decode(encoded_value.encode()).decode()
                            except:
                                value = encoded_value  # Nếu không giải mã được, sử dụng giá trị gốc
                        else:
                            value = encoded_value
                        
                        # Thêm field
                        cursor.execute("""
                            INSERT INTO fields (entry_id, label, value, is_password)
                            VALUES (?, ?, ?, ?)
                        """, (entry_id, label, value, is_password))
            
            conn.commit()
            conn.close()
            
            # Tải lại danh sách tabs
            self.load_tabs()
            
            # Thông báo thành công
            self.show_alert(f"Đã nhập thành công:\n- {tabs_imported} danh mục mới\n- {entries_imported} mật khẩu", "success")
            
        except Exception as e:
            self.show_alert(f"Có lỗi xảy ra khi nhập dữ liệu: {str(e)}", "error")
    
    def load_entries(self):
        """Tải danh sách entries của tab hiện tại"""
        # Xóa các entries cũ
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)
        
        if not self.current_tab_id:
            return
        
        # Lấy danh sách entries từ database
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, created_at FROM entries 
            WHERE tab_id = ? 
            ORDER BY title
        """, (self.current_tab_id,))
        
        entries = cursor.fetchall()
        conn.close()
        
        # Hiển thị entries trong treeview
        for entry_id, title, created_at in entries:
            self.entries_tree.insert("", tk.END, values=(title, created_at), iid=entry_id)
    
    def on_entry_selected(self, event):
        """Xử lý khi chọn một entry"""
        selected_items = self.entries_tree.selection()
        if not selected_items:
            self.display_no_info()
            self.delete_entry_button.config(state=tk.DISABLED)
            return
        
        # Lấy ID của entry được chọn
        entry_id = selected_items[0]
        self.current_entry_id = entry_id
        
        # Kích hoạt nút xóa entry
        self.delete_entry_button.config(state=tk.NORMAL)
        
        # Tải thông tin chi tiết của entry
        self.load_entry_details(entry_id)
    
    def load_entry_details(self, entry_id):
        """Tải thông tin chi tiết của entry"""
        # Xóa thông tin chi tiết cũ
        self.clear_entry_details()
        
        # Lấy thông tin chi tiết từ database
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("SELECT title FROM entries WHERE id = ?", (entry_id,))
        entry_title = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT id, label, value, is_password FROM fields 
            WHERE entry_id = ? 
            ORDER BY id
        """, (entry_id,))
        
        fields = cursor.fetchall()
        conn.close()
        
        # Hiển thị tiêu đề
        title_frame = tk.Frame(self.entry_details_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(title_frame, text=entry_title, font=("Arial", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Lưu danh sách field_entries để sau này cập nhật
        self.field_entries = []
        
        # Frame chứa danh sách các field
        fields_container = tk.Frame(self.entry_details_frame)
        fields_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Tạo scrollable frame với khả năng cuộn ngang
        # Đầu tiên tạo canvas
        canvas = tk.Canvas(fields_container)
        
        # Tạo scrollbar ngang và dọc
        hscrollbar = ttk.Scrollbar(fields_container, orient=tk.HORIZONTAL, command=canvas.xview)
        vscrollbar = ttk.Scrollbar(fields_container, orient=tk.VERTICAL, command=canvas.yview)
        
        # Đặt scrollbar vào đúng vị trí
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Cấu hình canvas sử dụng scrollbar
        canvas.configure(xscrollcommand=hscrollbar.set, yscrollcommand=vscrollbar.set)
        
        # Tạo frame bên trong canvas để chứa các field
        fields_frame = tk.Frame(canvas)
        
        # Đặt fields_frame vào canvas
        canvas_window = canvas.create_window((0, 0), window=fields_frame, anchor=tk.NW)
        
        # Cập nhật vùng cuộn khi nội dung thay đổi
        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        fields_frame.bind("<Configure>", update_scrollregion)
        
        # Đảm bảo rằng canvas_window luôn có chiều rộng đủ để hiển thị tất cả nội dung
        def on_canvas_configure(event):
            # Thiết lập chiều rộng của frame bên trong canvas để phù hợp với canvas
            # Nhưng đảm bảo nó không nhỏ hơn kích thước tự nhiên của frame
            natural_width = fields_frame.winfo_reqwidth()
            if event.width > natural_width:
                canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Hiển thị các field
        for field_id, label, value, is_password in fields:
            self.create_field_entry(fields_frame, field_id, label, value, is_password)
        
        # Frame chứa các nút
        buttons_frame = tk.Frame(self.entry_details_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Nút thêm field mới
        add_field_btn = tk.Button(buttons_frame, text="Thêm trường mới", 
                              command=lambda: self.add_new_field(fields_frame, entry_id), 
                              font=("Arial", 11))
        add_field_btn.pack(side=tk.LEFT)
        
        # Nút lưu thay đổi
        save_button = tk.Button(buttons_frame, text="Lưu thay đổi", 
                             command=self.save_entry_changes, 
                             font=("Arial", 11), bg="#4a7abc", fg="white")
        save_button.pack(side=tk.RIGHT)
    
    def create_field_entry(self, parent, field_id, label, value, is_password, new_field=False):
        """Tạo một trường nhập liệu cho field"""
        # Tạo frame với chiều rộng và chiều cao cố định
        field_frame = tk.Frame(parent, width=700, height=40)  # Đặt cả chiều rộng và chiều cao
        field_frame.pack(fill=tk.X, pady=5)
        field_frame.pack_propagate(False)  # Ngăn frame co lại theo nội dung
        field_frame.grid_propagate(False)  # Đảm bảo cả grid layout cũng không làm thay đổi kích thước
        
        # Label
        label_var = tk.StringVar(value=label)
        label_entry = tk.Entry(field_frame, textvariable=label_var, width=15, font=("Arial", 11))
        label_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.Y)
        
        # Value
        if is_password:
            # Hiển thị text box với nút hiển thị/ẩn mật khẩu
            value_var = tk.StringVar(value="•" * len(value))
            value_entry = tk.Entry(field_frame, textvariable=value_var, width=25, font=("Arial", 11))
            value_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.Y)
            
            # Cấu hình hiển thị dấu chấm cho mật khẩu
            value_entry.config(show="•")
            
            # Lưu giá trị thật và id
            value_entry.real_value = value
            value_entry.field_id = field_id
            value_entry.is_password = is_password
            value_entry.is_new = new_field
            value_entry.label_entry = label_entry
            
            # Biến theo dõi trạng thái hiển thị
            value_entry.is_visible = False
            
            # Nút hiển thị/ẩn
            def toggle_visibility(entry):
                if entry.is_visible:
                    entry.config(show="•")
                    entry.is_visible = False
                else:
                    entry.config(show="")
                    # Hiển thị giá trị thật khi bỏ dấu •
                    entry.delete(0, tk.END)
                    entry.insert(0, entry.real_value)
                    entry.is_visible = True
            
            toggle_btn = tk.Button(field_frame, text="👁️", 
                                 command=lambda e=value_entry: toggle_visibility(e),
                                 font=("Arial", 11), height=1)
            toggle_btn.pack(side=tk.LEFT, padx=(0, 0), fill=tk.Y)
            
            # Nút copy với giá trị thực của mật khẩu
            copy_btn = tk.Button(field_frame, text="Copy", 
                              command=lambda v=value: self.copy_to_clipboard(v),
                              font=("Arial", 11), height=1)
            copy_btn.pack(side=tk.LEFT, padx=(5, 0), fill=tk.Y)
            
            # Thêm checkbox cho mật khẩu
            is_pwd_var = tk.BooleanVar(value=True)
            pwd_check = tk.Checkbutton(field_frame, text="Mật khẩu", variable=is_pwd_var, font=("Arial", 11))
            pwd_check.pack(side=tk.LEFT, padx=(5, 0), fill=tk.Y)
            value_entry.is_pwd_var = is_pwd_var
        else:
            # Hiển thị text box bình thường
            value_var = tk.StringVar(value=value)
            value_entry = tk.Entry(field_frame, textvariable=value_var, width=25, font=("Arial", 11))
            value_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.Y)
            
            # Lưu thông tin field_id
            value_entry.field_id = field_id
            value_entry.is_password = is_password
            value_entry.is_new = new_field
            value_entry.label_entry = label_entry
            
            # Nút copy
            copy_btn = tk.Button(field_frame, text="Copy", 
                              command=lambda v=value: self.copy_to_clipboard(v),
                              font=("Arial", 11), height=1)
            copy_btn.pack(side=tk.LEFT, padx=(5, 0), fill=tk.Y)
            
            # Thêm checkbox cho mật khẩu
            is_pwd_var = tk.BooleanVar(value=False)
            pwd_check = tk.Checkbutton(field_frame, text="Mật khẩu", variable=is_pwd_var, font=("Arial", 11))
            pwd_check.pack(side=tk.LEFT, padx=(5, 0), fill=tk.Y)
            value_entry.is_pwd_var = is_pwd_var
        
        # Thêm nút xóa nếu là field mới
        if new_field:
            def remove_field():
                field_frame.destroy()
                self.field_entries.remove(value_entry)
            
            remove_btn = tk.Button(field_frame, text="X", command=remove_field, font=("Arial", 11), height=1)
            remove_btn.pack(side=tk.LEFT, padx=(5, 0), fill=tk.Y)
        
        # Thêm vào danh sách để cập nhật sau này
        self.field_entries.append(value_entry)
    
    def add_new_field(self, parent, entry_id):
        """Thêm một trường mới vào danh sách"""
        # Tạo một field mới với ID tạm thời là -1 (sẽ được cập nhật sau khi lưu)
        self.create_field_entry(parent, -1, "Trường mới", "", False, True)
        self.show_alert("Đã thêm trường mới, nhớ lưu lại để cập nhật!", "info")
    
    def save_entry_changes(self):
        """Lưu thay đổi thông tin entry"""
        if not self.current_entry_id or not hasattr(self, 'field_entries'):
            return
            
        try:
            # Kết nối database
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            # Cập nhật từng field
            for entry in self.field_entries:
                field_id = entry.field_id
                value = entry.get()
                label = entry.label_entry.get()
                is_password = entry.is_pwd_var.get()  # Lấy giá trị từ checkbox
                
                # Nếu là mật khẩu và đang hiển thị dạng ẩn, lấy giá trị thật
                if is_password and hasattr(entry, 'is_visible') and not entry.is_visible and hasattr(entry, 'real_value') and value == "•" * len(entry.real_value):
                    value = entry.real_value
                
                # Kiểm tra xem là field mới hay field đã tồn tại
                if hasattr(entry, 'is_new') and entry.is_new:
                    # Thêm field mới vào database
                    cursor.execute("""
                        INSERT INTO fields (entry_id, label, value, is_password)
                        VALUES (?, ?, ?, ?)
                    """, (self.current_entry_id, label, value, is_password))
                else:
                    # Cập nhật field đã tồn tại
                    cursor.execute("""
                        UPDATE fields SET label = ?, value = ?, is_password = ? WHERE id = ?
                    """, (label, value, is_password, field_id))
            
            conn.commit()
            conn.close()
            
            # Thông báo thành công
            self.show_alert("Đã lưu thay đổi thành công!", "success")
            
            # Tải lại thông tin chi tiết
            self.load_entry_details(self.current_entry_id)
            
        except Exception as e:
            self.show_alert(f"Có lỗi xảy ra: {str(e)}", "error")
    
    def clear_entry_details(self):
        """Xóa thông tin chi tiết entry"""
        for widget in self.entry_details_frame.winfo_children():
            widget.destroy()
    
    def add_tab(self):
        """Thêm tab mới"""
        tab_name = simpledialog.askstring("Thêm danh mục", "Nhập tên danh mục:")
        if not tab_name:
            return
            
        # Kiểm tra xem tên tab đã tồn tại chưa
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM tabs WHERE user_id = ? AND name = ?", (self.user_id, tab_name))
        if cursor.fetchone():
            self.show_alert("Tên danh mục đã tồn tại!", "error")
            conn.close()
            return
        
        # Thêm tab vào database
        cursor.execute("INSERT INTO tabs (user_id, name) VALUES (?, ?)", 
                     (self.user_id, tab_name))
        
        conn.commit()
        conn.close()
        
        # Tải lại danh sách tabs
        self.load_tabs()
        self.show_alert(f"Đã thêm danh mục '{tab_name}' thành công", "success")
    
    def delete_tab(self):
        """Xóa tab hiện tại"""
        if not self.current_tab_id:
            return
        
        # Xác nhận xóa
        confirm = messagebox.askyesno("Xác nhận", 
                                   "Bạn có chắc chắn muốn xóa danh mục này? Tất cả mật khẩu trong danh mục sẽ bị xóa.")
        if not confirm:
            return
        
        # Xóa tab từ database
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tabs WHERE id = ?", (self.current_tab_id,))
        
        conn.commit()
        conn.close()
        
        # Reset các biến
        self.current_tab_id = None
        self.current_entry_id = None
        
        # Cập nhật giao diện
        self.entries_title.config(text="Chưa chọn danh mục")
        self.add_entry_button.config(state=tk.DISABLED)
        self.delete_tab_button.config(state=tk.DISABLED)
        self.rename_tab_button.config(state=tk.DISABLED)
        
        # Xóa các entries
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)
        
        # Hiển thị "Chưa có thông tin"
        self.display_no_info()
        
        # Tải lại danh sách tabs
        self.load_tabs()
        self.show_alert("Đã xóa danh mục thành công", "success")
    
    def add_entry(self):
        """Thêm entry (mật khẩu) mới"""
        if not self.current_tab_id:
            return
        
        # Tạo cửa sổ để thêm entry mới
        entry_window = tk.Toplevel(self.master)
        entry_window.title("Thêm mật khẩu mới")
        entry_window.geometry("650x550")
        entry_window.transient(self.master)
        entry_window.grab_set()
        
        # Container
        container = tk.Frame(entry_window, padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        tk.Label(container, text="Thêm mật khẩu mới", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # Tiêu đề entry
        tk.Label(container, text="Tiêu đề:", font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=5)
        title_entry = tk.Entry(container, width=40, font=("Arial", 11))
        title_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Frame chứa danh sách fields
        fields_frame = tk.Frame(container)
        fields_frame.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW, pady=10)
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Tạo canvas để cuộn được
        canvas = tk.Canvas(fields_frame)
        scrollbar = tk.Scrollbar(fields_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        fields_list_frame = tk.Frame(canvas)
        fields_list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=fields_list_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Danh sách các fields
        fields = []
        
        # Hàm thêm field
        def add_field():
            field_frame = tk.Frame(fields_list_frame)
            field_frame.pack(fill=tk.X, pady=5)
            
            # Label
            label_entry = tk.Entry(field_frame, width=20, font=("Arial", 11))
            label_entry.insert(0, f"Field {len(fields) + 1}")
            label_entry.pack(side=tk.LEFT, padx=(0, 5))
            
            # Value
            value_entry = tk.Entry(field_frame, width=30, font=("Arial", 11))
            value_entry.pack(side=tk.LEFT, padx=(0, 5))
            
            # Checkbox để xác định có phải là mật khẩu không
            is_password = tk.BooleanVar()
            tk.Checkbutton(field_frame, text="Mật khẩu", variable=is_password, font=("Arial", 11)).pack(side=tk.LEFT)
            
            # Nút xóa field
            def remove_field():
                field_frame.destroy()
                fields.remove((label_entry, value_entry, is_password))
            
            tk.Button(field_frame, text="X", command=remove_field, font=("Arial", 11)).pack(side=tk.LEFT, padx=(5, 0))
            
            # Nút gợi ý mật khẩu
            def suggest_password():
                # Tạo mật khẩu ngẫu nhiên
                password = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) 
                                for _ in range(12))
                value_entry.delete(0, tk.END)
                value_entry.insert(0, password)
                is_password.set(True)
            
            tk.Button(field_frame, text="🔑", command=suggest_password, font=("Arial", 11)).pack(side=tk.LEFT, padx=(5, 0))
            
            # Thêm vào danh sách
            fields.append((label_entry, value_entry, is_password))
        
        # Thêm 2 field mặc định
        add_field()
        add_field()
        
        # Nút thêm field
        add_field_button = tk.Button(container, text="Thêm trường", command=add_field, font=("Arial", 11))
        add_field_button.grid(row=3, column=0, sticky=tk.W, pady=10)
        
        # Nút lưu
        def save_entry():
            title = title_entry.get().strip()
            
            if not title:
                self.show_alert("Vui lòng nhập tiêu đề!", "error")
                return
            
            # Kiểm tra xem có field nào không
            if not fields:
                self.show_alert("Vui lòng thêm ít nhất một trường thông tin!", "error")
                return
            
            # Lưu vào database
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            # Thêm entry
            cursor.execute("""
                INSERT INTO entries (tab_id, title) 
                VALUES (?, ?)
            """, (self.current_tab_id, title))
            
            entry_id = cursor.lastrowid
            
            # Thêm các fields
            for label_entry, value_entry, is_password in fields:
                label = label_entry.get().strip()
                value = value_entry.get()
                
                if not label:
                    label = "Không có nhãn"
                
                cursor.execute("""
                    INSERT INTO fields (entry_id, label, value, is_password)
                    VALUES (?, ?, ?, ?)
                """, (entry_id, label, value, is_password.get()))
            
            conn.commit()
            conn.close()
            
            # Đóng cửa sổ
            entry_window.destroy()
            
            # Tải lại danh sách entries
            self.load_entries()
            self.show_alert("Đã thêm mật khẩu mới thành công!", "success")
        
        save_button = tk.Button(container, text="Lưu", command=save_entry, width=10, font=("Arial", 11))
        save_button.grid(row=3, column=2, sticky=tk.E, pady=10)
    
    def delete_entry(self):
        """Xóa entry hiện tại"""
        if not self.current_entry_id:
            return
        
        # Xác nhận xóa
        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa mật khẩu này?")
        if not confirm:
            return
        
        # Xóa entry từ database
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM entries WHERE id = ?", (self.current_entry_id,))
        
        conn.commit()
        conn.close()
        
        # Reset biến
        self.current_entry_id = None
        
        # Cập nhật giao diện
        self.delete_entry_button.config(state=tk.DISABLED)
        
        # Hiển thị "Chưa có thông tin"
        self.display_no_info()
        
        # Tải lại danh sách entries
        self.load_entries()
        self.show_alert("Đã xóa mật khẩu thành công", "success")
    
    def copy_to_clipboard(self, value):
        """Sao chép giá trị vào clipboard"""
        pyperclip.copy(value)
        
        # Hiển thị thông báo toast thay vì message box
        self.show_alert("Đã sao chép vào clipboard!", "info")
    
    def show_toast(self, message, duration=3000, bg_color="#4a7abc", fg_color="white"):
        """Hiển thị thông báo tạm thời tự biến mất sau một khoảng thời gian
        
        Args:
            message: Nội dung thông báo
            duration: Thời gian hiển thị (ms)
            bg_color: Màu nền
            fg_color: Màu chữ
        """
        # Tạo top-level window không có viền
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
        label = tk.Label(toast, text=message, background=bg_color, foreground=fg_color,
                      font=("Arial", 11), wraplength=280, padx=10, pady=10)
        label.pack(fill=tk.BOTH, expand=True)
        
        # Tự động đóng sau khoảng thời gian duration
        toast.after(duration, toast.destroy)
    
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
            
        # Sử dụng hàm show_toast để hiển thị
        self.show_toast(message, 3000, bg_color, "white")
    
    def logout(self):
        """Đăng xuất khỏi ứng dụng"""
        # Xác nhận đăng xuất
        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất?")
        if not confirm:
            return
        
        # Gọi callback để hiển thị lại màn hình đăng nhập
        self.logout_callback()
    
    def create_default_tab(self):
        """Tạo tab mặc định cho người dùng"""
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO tabs (user_id, name) VALUES (?, ?)", 
                     (self.user_id, "General"))
        
        conn.commit()
        conn.close()
        
        self.show_alert("Đã tạo danh mục mặc định", "info") 