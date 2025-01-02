from facebook import GraphAPI
from dotenv import load_dotenv
import os
import requests

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy ACCESS_TOKEN và PAGE_ID từ .env
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # Token truy cập của bạn
PAGE_ID = os.getenv("PAGE_ID")  # ID của Trang

# Khởi tạo GraphAPI
graph = GraphAPI(access_token=ACCESS_TOKEN)

# Nội dung bài viết
post_message = "Đây là bài đăng thử nghiệm từ Python. 🚀"

# Đăng bài viết
def create_post_page(page_id, message):
    try:
        graph.put_object(
            parent_object=page_id, connection_name="feed", message=message
        )
        print("Bài đăng đã được đăng thành công!")
    except Exception as e:
        print(f"Lỗi khi đăng bài viết: {str(e)}")

def create_post_by_request():
    url = f"https://graph.facebook.com/v21.0/me?access_token={ACCESS_TOKEN}&debug=all&fields=accounts&format=json&method=get&origin_graph_explorer=1&pretty=0&suppress_http_code=1&transport=cors"
    try:
        response = requests.get(url, timeout=10)
        print(response.json())
    except requests.Timeout:
        print("Request timed out")
    except requests.RequestException as e:
        print(f"Error occurred: {str(e)}")

def get_access_token_page_by_id(page_id):
    try:
        url = f"https://graph.facebook.com/{page_id}?fields=access_token&access_token={ACCESS_TOKEN}"
        response = requests.get(url, timeout=10)
        return response.json().get("access_token")
    except requests.Timeout:
        print("Request timed out")
    except requests.RequestException as e:
        print(f"Error occurred: {str(e)}")

def get_account():
    profile = graph.get_object("me")
    print("Token hoạt động! Tài khoản:", profile)

access_token_page = get_access_token_page_by_id(PAGE_ID)
print(access_token_page)
# create_post_page(PAGE_ID, post_message)
