from facebook import GraphAPI
from dotenv import load_dotenv
import os

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy ACCESS_TOKEN và PAGE_ID từ .env
ACCESS_TOKEN = os.getenv("DUCK_ACCESS_TOKEN")  # Token truy cập của bạn
PAGE_ID = os.getenv("PAGE_ID")  # ID của Trang

# Khởi tạo GraphAPI
graph = GraphAPI(access_token=ACCESS_TOKEN)

# Nội dung bài viết
post_message = "Đây là bài đăng thử nghiệm từ Python. 🚀"

# Đăng bài viết
try:
    response = graph.put_object(
        parent_object=PAGE_ID, connection_name="feed", message=post_message
    )
    print("Bài đăng đã được đăng thành công!")
    print("Phản hồi:", response)
except Exception as e:
    print("Lỗi khi đăng bài viết:", e)
