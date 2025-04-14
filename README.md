# KITPass - Ứng dụng quản lý mật khẩu desktop

KITPass là ứng dụng quản lý mật khẩu đơn giản được xây dựng bằng Python và Tkinter. Ứng dụng cho phép người dùng lưu trữ và quản lý mật khẩu một cách an toàn.

## Tính năng

- Đăng nhập/Đăng ký để bảo vệ dữ liệu
- Quản lý mật khẩu theo các danh mục (tabs)
- Thêm/Xóa danh mục mật khẩu
- Thêm/Xóa các mục mật khẩu với nhiều trường thông tin
- Ẩn/Hiện mật khẩu
- Sao chép nhanh thông tin vào clipboard
- Tạo mật khẩu ngẫu nhiên

## Cấu trúc thư mục

```
KITPass/
├── src/               # Mã nguồn chính
│   ├── main.py        # Điểm vào chính
│   ├── login.py       # Module đăng nhập
│   └── password_manager.py  # Module quản lý mật khẩu
├── tools/             # Công cụ build và tiện ích
│   ├── build_exe.py   # Script tạo file .exe
│   ├── build_exe.bat  # Batch file để tạo .exe
│   ├── create_shortcut.py  # Script tạo shortcut
│   └── create_shortcut.bat # Batch file tạo shortcut
├── data/              # Thư mục chứa dữ liệu
│   └── kitpass.db     # Cơ sở dữ liệu SQLite
├── build/             # Thư mục build tạm thời
├── dist/              # Thư mục chứa build output
├── KITPass.exe        # File thực thi chính (sau khi build)
├── KITPass.spec       # Tệp cấu hình PyInstaller
├── setup_exe.bat      # Script tự động tạo file .exe và shortcut
└── run.bat            # Script chạy ứng dụng từ source code
```

## Yêu cầu

- Python 3.6 trở lên
- Tkinter (thường được cài đặt sẵn với Python)
- Module pyperclip để sao chép vào clipboard

## Cài đặt

1. Sao chép repository về máy:
```
git clone https://github.com/yourusername/kitpass.git
cd kitpass
```

2. Cài đặt thư viện cần thiết:
```
pip install -r requirements.txt
```

3. Chạy ứng dụng:
```
run.bat
```

hoặc

```
python src/main.py
```

## Tạo file thực thi (.exe)

Bạn có thể tạo file thực thi (.exe) để chạy ứng dụng mà không cần cài đặt Python:

### Cách 1: Sử dụng trình cài đặt tự động (Khuyên dùng)

1. Chạy file `setup_exe.bat` bằng cách nhấp đúp vào nó.
2. Đợi quá trình hoàn tất (sẽ tự động cài đặt các thư viện cần thiết, biên dịch file .exe và tạo shortcut trên Desktop).
3. Sử dụng shortcut trên Desktop hoặc file `KITPass.exe` trong thư mục gốc để chạy ứng dụng.

### Cách 2: Tạo file .exe thủ công

1. Chạy file `tools\build_exe.bat` để tạo file .exe.
2. (Tùy chọn) Chạy file `tools\create_shortcut.bat` để tạo shortcut trên Desktop.

## Hướng dẫn sử dụng

### Đăng ký và đăng nhập

- Khi khởi động ứng dụng lần đầu, bạn cần đăng ký một tài khoản mới.
- Nhấn nút "Đăng ký" và điền thông tin tài khoản.
- Sau khi đăng ký, hệ thống sẽ tự động tạo một danh mục mặc định "General".
- Đăng nhập với tài khoản đã đăng ký để sử dụng ứng dụng.

### Quản lý danh mục

- Phần bên trái màn hình hiển thị danh sách các danh mục.
- Nhấn nút "Thêm danh mục" để tạo danh mục mới.
- Chọn một danh mục và nhấn nút "Xóa" để xóa danh mục đó.

### Quản lý mật khẩu

- Sau khi chọn một danh mục, bạn có thể thêm mật khẩu mới bằng cách nhấn nút "Thêm mật khẩu".
- Mỗi mục mật khẩu có thể có nhiều trường thông tin, mỗi trường gồm một nhãn và giá trị.
- Bạn có thể đánh dấu trường thông tin là mật khẩu để ẩn nội dung mặc định.
- Nhấn biểu tượng 🔑 để tạo mật khẩu ngẫu nhiên.
- Nhấn biểu tượng 👁️ để hiển thị/ẩn mật khẩu.
- Nhấn biểu tượng 📋 để sao chép giá trị vào clipboard.

## Bảo mật

- Mật khẩu được lưu trữ trong cơ sở dữ liệu SQLite với mã hóa hash (SHA-256) và salt.
- Dữ liệu được lưu trữ trong thư mục `data` của ứng dụng.

## Phát triển thêm

Ứng dụng này được thiết kế với mục đích dễ mở rộng. Một số hướng phát triển có thể:

- Mã hóa cơ sở dữ liệu
- Thêm tính năng sao lưu và khôi phục dữ liệu
- Tích hợp trình duyệt web
- Thêm tính năng tạo mật khẩu mạnh tùy chỉnh
- Hỗ trợ đồng bộ hóa đám mây
- Cải thiện giao diện người dùng

## Giấy phép

MIT License 