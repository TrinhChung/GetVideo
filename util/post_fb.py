from facebook import GraphAPI
from dotenv import load_dotenv
import os
import requests
from models.page import Page  # Assuming Page is defined in page.py
from database_init import db  # Assuming db is initialized in database_init.py
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from flask import  flash

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
def create_post_page(page_id, access_token, message):
    try:
        graph.put_object(parent_object=page_id, connection_name="feed", message=message)
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

        if not pages:
            print("Không có trang nào được liên kết với tài khoản này.")
            return False

        print(f"Đã tìm thấy {len(pages)} trang. Đang lưu vào cơ sở dữ liệu...")

        # Kết nối cơ sở dữ liệu sử dụng SQLAlchemy
        for page in pages:
            page_id = page.get("id")
            name = page.get("name")
            category = page.get("category", None)
            page_access_token = page.get("access_token")

            # Lấy expires_at từ get_token_data_from_facebook
            token_data, expires_at = get_token_data_from_facebook(page_access_token)

            if expires_at is None:
                expires_at = None  # Nếu không có expires_at, gán là None

            # Kiểm tra xem page_id có tồn tại trong cơ sở dữ liệu chưa
            existing_page = Page.query.filter_by(page_id=page_id).first()

            if existing_page:
                # Nếu đã tồn tại, cập nhật thông tin của trang
                existing_page.name = name
                existing_page.category = category
                existing_page.access_token = page_access_token
                existing_page.expires_at = expires_at
                existing_page.facebook_account_id = facebook_account_id
            else:
                # Nếu chưa có, tạo mới một bản ghi
                new_page = Page(
                    page_id=page_id,
                    name=name,
                    category=category,
                    access_token=page_access_token,
                    expires_at=expires_at,
                    facebook_account_id=facebook_account_id,
                )
                db.session.add(new_page)

        # Xác nhận thay đổi vào cơ sở dữ liệu
        db.session.commit()
        print("Dữ liệu đã được lưu thành công!")

        return True

    except IntegrityError as e:
        db.session.rollback()  # Rollback nếu có lỗi IntegrityError
        print(f"Lỗi cơ sở dữ liệu: {e}")
        return False
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return False


def process_expires_at(token_data):
    """
    Xử lý expires_at từ dữ liệu token của Facebook.
    Trả về thời gian hết hạn hoặc None nếu không có thời gian hết hạn.
    """
    expires_at = token_data.get("expires_at", None)
    if expires_at == 0:
        expires_at = datetime(
            2100, 1, 1
        )  # Nếu expires_at = 0, đặt ngày hết hạn là năm 2100
    else:
        expires_at = datetime.fromtimestamp(expires_at) if expires_at else None
    return expires_at


def get_token_data_from_facebook(access_token):
    """
    Gửi yêu cầu đến API của Facebook để kiểm tra thông tin và thời hạn của Access Token.
    Trả về dữ liệu token hoặc None nếu có lỗi.
    """
    app_id = os.getenv("APP_ID")  # Thay bằng App ID của bạn
    app_secret = os.getenv("APP_SECRET")  # Thay bằng App Secret của bạn
    app_access_token = f"{app_id}|{app_secret}"

    # Endpoint để debug token
    url = f"https://graph.facebook.com/debug_token?input_token={access_token}&access_token={app_access_token}"

    try:
        # Gửi yêu cầu
        response = requests.get(url, timeout=10)
        data = response.json()

        if "data" in data:
            token_data = data["data"]
            expires_at = process_expires_at(token_data)  # Sử dụng hàm xử lý expires_at
            return token_data, expires_at
        else:
            print("Không thể lấy thông tin token.")
            print(data)
            return None, None
    except requests.Timeout:
        print("Request timed out.")
    except requests.RequestException as e:
        print(f"Lỗi khi kiểm tra token: {str(e)}")
        return None, None


def check_token_expiry(access_token, page_id):
    """
    Kiểm tra thông tin và thời hạn của Access Token và cập nhật expires_at vào cơ sở dữ liệu.
    """
    try:
        # Lấy dữ liệu token từ Facebook
        token_data, expires_at = get_token_data_from_facebook(access_token)

        if token_data:
            is_valid = token_data.get("is_valid", False)

            print(f"Token hợp lệ: {is_valid}")
            print(f"Expires_at: {expires_at}")

            # Tìm page tương ứng với page_id
            page = Page.query.filter_by(page_id=page_id).first()

            if page:
                # Cập nhật expires_at vào bảng Page
                page.expires_at = expires_at
                db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu

                flash(
                    f"Token Debug Success and expires_at updated for page: {page.name}",
                    "success",
                )
            else:
                flash("Page not found.", "error")

            return token_data, expires_at
        else:
            print("Không thể lấy dữ liệu token.")
            return None, None
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return None, None
