import mysql.connector
from mysql.connector import Error
import time
from dotenv import load_dotenv
import os

load_dotenv()

PASSWORD_DB = os.getenv("PASSWORD_DB")  # Token truy cập của bạn

# Kết nối đến MySQL
try:
    connection = mysql.connector.connect(
        host="localhost",  # Máy chủ MySQL
        user="root",  # Tên người dùng MySQL
        password=PASSWORD_DB,  # Mật khẩu người dùng MySQL
        database="video",  # Tên cơ sở dữ liệu
    )

    # Kiểm tra kết nối
    if connection.is_connected():
        print("Đã kết nối thành công đến MySQL")
except Error as e:
    print(f"Lỗi kết nối MySQL: {e}")
    time.sleep(5)  # Đợi 5 giây và thử lại
    connection = mysql.connector.connect(
        host="localhost", user="root", password=PASSWORD_DB
    )
    cursor = connection.cursor()
    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS video"
    )  # Tạo cơ sở dữ liệu nếu chưa có
    print("Đã tạo cơ sở dữ liệu video.")
    connection.database = "video"  # Chuyển đổi kết nối sang cơ sở dữ liệu video

# Khởi tạo con trỏ để thực thi câu lệnh SQL
cursor = connection.cursor()

# Tạo bảng playlist
create_playlist_table = """
CREATE TABLE IF NOT EXISTS playlist (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255)
)
"""

# Tạo bảng videos
create_videos_table = """
CREATE TABLE IF NOT EXISTS videos (
    video_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255),
    crawled BOOLEAN DEFAULT FALSE,
    playlist_id VARCHAR(255),
    FOREIGN KEY (playlist_id) REFERENCES playlists(id)
);
"""

create_facebook_accounts_table = """
CREATE TABLE IF NOT EXISTS facebook_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY, -- ID tự tăng làm khóa chính
    email VARCHAR(255) UNIQUE,         -- Email của tài khoản Facebook, có thể null
    access_token TEXT NOT NULL         -- Access token của tài khoản, bắt buộc
);
"""

create_pages_table = """
CREATE TABLE IF NOT EXISTS pages (
    page_id VARCHAR(255) PRIMARY KEY,  -- ID của page
    name VARCHAR(255),                 -- Tên page, có thể null
    category VARCHAR(255),             -- Loại danh mục của page, có thể null
    access_token TEXT NOT NULL,        -- Access token của page, bắt buộc
    expires_at DATETIME,               -- Thời gian hết hạn của token, có thể null
    facebook_account_id INT,           -- Khóa ngoại tới bảng facebook_accounts, có thể null
    FOREIGN KEY (facebook_account_id) REFERENCES facebook_accounts(id) ON DELETE CASCADE
);
"""

# Thực thi câu lệnh tạo bảng
try:
    cursor.execute(create_playlist_table)  # Tạo bảng playlist
    cursor.execute(create_videos_table)  # Tạo bảng videos
    cursor.execute(create_facebook_accounts_table)  # Tạo bảng token account
    cursor.execute(create_pages_table)  # Tạo bảng videos
    print("Đã tạo thành công bảng playlist và videos.")
except mysql.connector.Error as err:
    print(f"Lỗi khi tạo bảng: {err}")

# Đóng kết nối
cursor.close()
connection.close()
