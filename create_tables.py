import mysql.connector
from mysql.connector import Error
import time

# Kết nối đến MySQL
try:
    connection = mysql.connector.connect(
        host="localhost",  # Máy chủ MySQL
        user="root",  # Tên người dùng MySQL
        password="chungtrinh1904",  # Mật khẩu người dùng MySQL
        database="video",  # Tên cơ sở dữ liệu
    )

    # Kiểm tra kết nối
    if connection.is_connected():
        print("Đã kết nối thành công đến MySQL")
except Error as e:
    print(f"Lỗi kết nối MySQL: {e}")
    time.sleep(5)  # Đợi 5 giây và thử lại
    connection = mysql.connector.connect(
        host="localhost", user="root", password="chungtrinh1904"
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
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Tạo bảng videos
create_videos_table = """
CREATE TABLE IF NOT EXISTS videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    playlist_id INT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (playlist_id) REFERENCES playlist(id) ON DELETE CASCADE
);
"""

# Thực thi câu lệnh tạo bảng
try:
    cursor.execute(create_playlist_table)  # Tạo bảng playlist
    cursor.execute(create_videos_table)  # Tạo bảng videos
    print("Đã tạo thành công bảng playlist và videos.")
except mysql.connector.Error as err:
    print(f"Lỗi khi tạo bảng: {err}")

# Đóng kết nối
cursor.close()
connection.close()
