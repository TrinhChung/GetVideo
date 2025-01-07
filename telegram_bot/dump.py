import mysql.connector
from mysql.connector import Error
import time
from dotenv import load_dotenv
import os

load_dotenv()

PASSWORD_DB = os.getenv("PASSWORD_DB")  # Token truy cập của bạn

def get_pages():
    # Kết nối đến MySQL
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",  # Máy chủ MySQL
            user="root",  # Tên người dùng MySQL
            password=PASSWORD_DB,  # Mật khẩu người dùng MySQL
            database="video",  # Tên cơ sở dữ liệu
        )

        if connection.is_connected():
            print("Đã kết nối thành công đến MySQL")
            
            # Khởi tạo con trỏ để thực thi câu lệnh SQL
            cursor = connection.cursor()
            query = "SELECT * FROM page"
            try:
                # Thực thi truy vấn
                cursor.execute(query)
                # Lấy toàn bộ kết quả
                result = cursor.fetchall()
                return result
            except Exception as query_error:
                print(f"Lỗi khi thực thi truy vấn: {query_error}")
                return []
            finally:
                # Đảm bảo đóng con trỏ sau khi sử dụng
                cursor.close()
    except Error as connect_error:
        print(f"Lỗi kết nối MySQL: {connect_error}")
        return []
    finally:
        # Đảm bảo đóng kết nối nếu nó được mở
        if connection and connection.is_connected():
            connection.close()
            print("Đã đóng kết nối MySQL")