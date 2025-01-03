from facebook import GraphAPI
from dotenv import load_dotenv
import os
import requests
from database_init import mysql

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy ACCESS_TOKEN và PAGE_ID từ .env
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # Token truy cập của bạn
PAGE_ID = os.getenv("PAGE_ID")  # ID của Trang

# Khởi tạo GraphAPI


# Nội dung bài viết
post_message = "Đây là bài đăng thử nghiệm từ Python. 🚀"

# Đăng bài viết
def create_post_page(page_id, access_token, message):
    try:
        graph = GraphAPI(access_token=access_token)
        graph.put_object(
            parent_object=page_id, connection_name="feed", message=message
        )
        print("Bài đăng đã được đăng thành công!")
    except Exception as e:
        print(f"Lỗi khi đăng bài viết: {str(e)}")


def create_post_by_request(access_token):
    url = f"https://graph.facebook.com/v21.0/me?access_token={access_token}&debug=all&fields=accounts&format=json&method=get&origin_graph_explorer=1&pretty=0&suppress_http_code=1&transport=cors"
    try:
        response = requests.get(url, timeout=10)
        print(response.json())
    except requests.Timeout:
        print("Request timed out")
    except requests.RequestException as e:
        print(f"Error occurred: {str(e)}")


def get_access_token_page_by_id(page_id, access_token):
    try:
        url = f"https://graph.facebook.com/{page_id}?fields=access_token&access_token={access_token}"
        response = requests.get(url, timeout=10)
        return response.json().get("access_token")
    except requests.Timeout:
        print("Request timed out")
    except requests.RequestException as e:
        print(f"Error occurred: {str(e)}")


def get_account(access_token, facebook_account_id):
    try:
        # Tạo kết nối Graph API
        graph = GraphAPI(access_token=access_token)

        # Lấy danh sách các trang được quản lý
        response = graph.get_object("me/accounts")
        pages = response.get("data", [])

        print(access_token)
        print(facebook_account_id)

        if not pages:
            print("Không có trang nào được liên kết với tài khoản này.")
            return False

        print(f"Đã tìm thấy {len(pages)} trang. Đang lưu vào cơ sở dữ liệu...")

        # Kết nối MySQL
        cursor = mysql.connection.cursor()

        # Lưu thông tin từng trang vào cơ sở dữ liệu
        for page in pages:
            page_id = page.get("id")
            name = page.get("name")
            category = page.get(
                "category", None
            )  # Một số trang có thể không có danh mục
            page_access_token = page.get("access_token")
            expires_at = None

            # Thêm hoặc cập nhật thông tin trang vào bảng `pages`
            cursor.execute(
                """
            INSERT INTO pages (page_id, name, category, access_token, expires_at,facebook_account_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                category = VALUES(category),
                access_token = VALUES(access_token);
            """,
                (
                    page_id,
                    name,
                    category,
                    page_access_token,
                    expires_at,
                    facebook_account_id,
                ),
            )

        # Xác nhận thay đổi
        mysql.connection.commit()
        return True

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return False

    finally:
        # Đóng kết nối
        cursor.close()


# access_token_page = get_access_token_page_by_id(PAGE_ID)
# print(access_token_page)
# create_post_page(PAGE_ID, post_message)
