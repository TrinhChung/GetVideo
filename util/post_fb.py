from flask import flash
from facebook import GraphAPI
from dotenv import load_dotenv
import os
import requests
from models.page import Page  # Assuming Page is defined in page.pyz
from database_init import db  # Assuming db is initialized in database_init.py
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from requests.exceptions import RequestException
from models.facebook_ad_account import FacebookAdAccount
from util.ads import fetch_facebook_campaigns
from models.facebook_account import FacebookAccount
from models.facebook_campaign import FacebookCampaign
from util.until import convert_to_mysql_datetime

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy ACCESS_TOKEN và PAGE_ID từ .env
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # Token truy cập của bạn
PAGE_ID = os.getenv("PAGE_ID")  # ID của Trang
APP_ID = os.getenv("APP_ID")

# Nội dung bài viết
post_message = "Đây là bài đăng thử nghiệm từ Python. 🚀"


# Đăng bài viết
def create_post_page(page_id, access_token, message):
    # Khởi tạo GraphAPI
    graph = GraphAPI(access_token=access_token)
    try:
        graph.put_object(parent_object=page_id, connection_name="feed", message=message)
        print("Bài đăng đã được đăng thành công!")
    except Exception as e:
        print(f"Lỗi khi đăng bài viết: {str(e)}")


def start_video_upload_for_reels(page_id, access_token):
    """
    Bắt đầu quá trình tải video lên Reels của Facebook.

    Parameters:
    - page_id: ID của trang Facebook
    - access_token: Token truy cập Facebook API
    """
    # URL để bắt đầu quá trình tải video lên Reels
    url = f"https://graph.facebook.com/v21.0/{page_id}/video_reels"

    # Dữ liệu gửi đi trong yêu cầu POST
    data = {"upload_phase": "start", "access_token": access_token}

    # Header yêu cầu
    headers = {"Content-Type": "application/json"}

    try:
        # Gửi yêu cầu POST
        response = requests.post(url, json=data, headers=headers)

        # Kiểm tra phản hồi từ Facebook
        if response.status_code == 200:
            print("Quá trình tải video lên Reels đã được bắt đầu thành công!")
            print(response.json())
            return response.json().get("video_id")  # Trả về dữ liệu JSON nếu cần
        else:
            print(f"Lỗi khi bắt đầu tải video lên Reels: {response.status_code}")
            print(response.text)
            return None

    except requests.RequestException as e:
        print(f"Đã xảy ra lỗi khi gửi yêu cầu: {e}")
        return None

def publish_video_reel(page_id: str, access_token: str, video_id: str, description: str) -> dict:
    """
    Publish a video reel on Facebook after uploading
    
    Args:
        page_id (str): Facebook page ID
        access_token (str): Facebook page access token  
        video_id (str): ID of the uploaded video
        description (str): Description/caption for the reel
        
    Returns:
        dict: Response from the Facebook API
        
    Raises:
        Exception: If publishing fails
    """
    try:
        # API endpoint
        publish_url = f"https://graph.facebook.com/v21.0/{page_id}/video_reels"
        
        # Request parameters
        params = {
            'access_token': access_token,
            'video_id': video_id,
            'upload_phase': 'finish',
            'video_state': 'PUBLISHED',
            'description': description
        }
        
        # Send POST request to publish the video
        response = requests.post(publish_url, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            print("Step publish finish success")
        else:
            raise Exception(f"Publishing failed with status code {response.status_code}: {response.text}")
            
    except Exception as e:
        raise Exception(f"Error publishing video reel: {str(e)}")

def upload_video_to_reel(video_path, access_token, page_id, message):
    """
    Tải video lên Facebook sử dụng API.

    Parameters:
    - video_path: Đường dẫn tới file video
    - access_token: Token truy cập Facebook API
    """

    # Lấy kích thước của video
    file_size = os.path.getsize(video_path)

    video_id = start_video_upload_for_reels(page_id, access_token)

    if not video_id:
        return None

    # URL tải video lên
    upload_url = f"https://rupload.facebook.com/video-upload/v21.0/{video_id}"

    # Header yêu cầu
    headers = {
        "Authorization": f"OAuth {access_token}",
        "offset": "0",  # Tùy chọn
        "file_size": str(file_size),  # Kích thước file
    }
    print(str(file_size))

    try:
        # Gửi yêu cầu POST với dữ liệu video
        with open(video_path, "rb") as video_file:
            response = requests.post(
                upload_url,
                headers=headers,
                data=video_file,
            )

        # Kiểm tra phản hồi từ Facebook
        if response.status_code == 200:
            print("Video tải lên reel thành công!")
            publish_video_reel(page_id, access_token, video_id, message)
        else:
            print(f"Lỗi khi tải video lên: {response.status_code}")
            print(response.text)
            return None

    except requests.RequestException as e:
        print(f"Đã xảy ra lỗi khi gửi yêu cầu: {e}")
        return None


def create_video_post(page_id, access_token, video_path, message=""):
    """
    Đăng video lên Facebook page theo cú pháp phân tải video.

    Parameters:
    - page_id: ID của trang Facebook
    - access_token: token truy cập Facebook API
    - video_path: Đường dẫn tới file video
    - message: Tin nhắn kèm video (tùy chọn)
    """

    # Kiểm tra sự tồn tại của video
    if not os.path.exists(video_path):
        raise Exception(f"Video file không tồn tại: {video_path}")

    # URL cho việc tạo phiên tải lên
    upload_url = f"https://graph-video.facebook.com/v21.0/{page_id}/videos"

    try:
        # Gửi yêu cầu POST để tạo phiên tải lên
        with open(video_path, 'rb') as video_file:
            files = {'file': video_file}
            payload = {
                'access_token': access_token,
                'description': message,
                'title': message
            }
            response = requests.post(upload_url, data=payload, files=files)

        # Lấy ID của phiên tải lên
        video_id = response.json().get("id")

        if not video_id:
            raise Exception("Không nhận được session ID cho phiên tải lên video.")

        flash(f"Video upload has been created successfully: {video_id}")

        upload_video_to_reel(video_path, access_token, page_id, message)

        return video_id

    except RequestException as e:
        print(e)
        raise Exception(f"Error when publish video: {e}")


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
        
        #time.sleep(3600)

        # Lấy danh sách các trang được quản lý
        response = graph.get_object("me/accounts")
        pages = response.get("data", [])

        if not pages:
            flash(
                f"Không có trang nào được liên kết với tài khoản này.",
                "danger",
            )
            return

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
            existing_page = Page.query.filter_by(page_id=page_id, facebook_account_id=facebook_account_id).first()

            if existing_page:
                # Nếu đã tồn tại, cập nhật thông tin của trang
                existing_page.name = name
                existing_page.category = category
                existing_page.access_token = page_access_token
                existing_page.expires_at = expires_at
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


def get_ad_accounts(access_token, facebook_account_id):
    """
    Lấy danh sách các tài khoản quảng cáo mà người dùng quản lý và lưu vào database.

    Args:
        access_token (str): Token truy cập Facebook API.
        user_id (int): ID người dùng trong hệ thống.

    Returns:
        list: Danh sách các tài khoản quảng cáo.
    """
    try:
        # Khởi tạo GraphAPI
        graph = GraphAPI(access_token=access_token)

        # Lấy thông tin chi tiết về các tài khoản quảng cáo
        fields = (
            "adaccounts{account_id,name,id,account_status,currency,balance,"
            "amount_spent,spend_cap,timezone_name,timezone_offset_hours_utc,"
            "business{id,name},created_time}"
        )

        response = graph.get_object(f"me?fields={fields}")

        # Debug response
        print(response)

        # Lấy danh sách tài khoản quảng cáo
        ad_accounts = response.get("adaccounts", {}).get("data", [])

        if not ad_accounts:
            flash(
                "Không có tài khoản quảng cáo nào được liên kết với tài khoản này.",
                "danger",
            )
            return []

        print(f"Đã tìm thấy {len(ad_accounts)} tài khoản quảng cáo.")

        for ad_account in ad_accounts:
            # Kiểm tra tài khoản đã tồn tại chưa
            existing_account = FacebookAdAccount.query.filter_by(
                facebook_ad_account_id=ad_account.get("account_id"),
                facebook_account_id=facebook_account_id
            ).first()

            if existing_account:
                # Cập nhật thông tin nếu đã tồn tại
                existing_account.name = ad_account.get("name")
                existing_account.account_status = ad_account.get("account_status")
                existing_account.currency = ad_account.get("currency")
                existing_account.balance = (
                    float(ad_account.get("balance", 0))
                    if ad_account.get("balance")
                    else None
                )
                existing_account.amount_spent = (
                    float(ad_account.get("amount_spent", 0))
                    if ad_account.get("amount_spent")
                    else None
                )
                existing_account.spend_cap = (
                    float(ad_account.get("spend_cap", 0))
                    if ad_account.get("spend_cap")
                    else None
                )
                existing_account.timezone_name = ad_account.get("timezone_name")
                existing_account.timezone_offset_hours_utc = float(
                    ad_account.get("timezone_offset_hours_utc", 0)
                )
                existing_account.business_id = ad_account.get("business", {}).get("id")
                existing_account.business_name = ad_account.get("business", {}).get(
                    "name"
                )
                existing_account.created_time = (
                    datetime.strptime(
                        ad_account.get("created_time"), "%Y-%m-%dT%H:%M:%S%z"
                    )
                    if ad_account.get("created_time")
                    else None
                )
                existing_account.facebook_account_id = facebook_account_id
            else:
                # Tạo mới nếu chưa tồn tại
                new_account = FacebookAdAccount(
                    facebook_ad_account_id=ad_account.get("account_id"),
                    name=ad_account.get("name"),
                    account_status=ad_account.get("account_status"),
                    currency=ad_account.get("currency"),
                    balance=(
                        float(ad_account.get("balance", 0))
                        if ad_account.get("balance")
                        else None
                    ),
                    amount_spent=(
                        float(ad_account.get("amount_spent", 0))
                        if ad_account.get("amount_spent")
                        else None
                    ),
                    spend_cap=(
                        float(ad_account.get("spend_cap", 0))
                        if ad_account.get("spend_cap")
                        else None
                    ),
                    timezone_name=ad_account.get("timezone_name"),
                    timezone_offset_hours_utc=float(
                        ad_account.get("timezone_offset_hours_utc", 0)
                    ),
                    business_id=ad_account.get("business", {}).get("id"),
                    business_name=ad_account.get("business", {}).get("name"),
                    created_time=(
                        datetime.strptime(
                            ad_account.get("created_time"), "%Y-%m-%dT%H:%M:%S%z"
                        )
                        if ad_account.get("created_time")
                        else None
                    ),
                    facebook_account_id=facebook_account_id,
                )
                db.session.add(new_account)

        # Lưu thay đổi vào database
        db.session.commit()
        print("Đã cập nhật thông tin tài khoản quảng cáo thành công.")

        return ad_accounts

    except requests.RequestException as e:
        print(f"Đã xảy ra lỗi khi lấy danh sách tài khoản quảng cáo: {str(e)}")
        return []


def sync_facebook_campaigns(facebook_account_id):
    facebook_account = FacebookAccount.query.filter_by(id=facebook_account_id).first()
    if not facebook_account:
        return "No Facebook account found", False

    updated_count = 0
    created_count = 0

    access_token = facebook_account.access_token
    facebook_ad_accounts = FacebookAdAccount.query.filter_by(
        facebook_account_id=facebook_account_id
    ).all()

    if not facebook_ad_accounts:
        return f"No Facebook Ad Accounts found for account {facebook_account.id}", False

    for ad_account in facebook_ad_accounts:
        try:
            campaigns = fetch_facebook_campaigns(
                ad_account.facebook_ad_account_id, access_token
            )
        except Exception as e:
            print(
                f"Error fetching campaigns from Facebook for account {ad_account.name}: {e}"
            )
            continue

        for campaign in campaigns:
            existing_campaign = FacebookCampaign.query.filter_by(
                facebook_campaign_id=campaign["id"]
            ).first()

            created_time = campaign.get("created_time")
            start_time = campaign.get("start_time")
            end_time = campaign.get("end_time")

            if created_time:
                created_time = datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S%z")
                created_time = convert_to_mysql_datetime(created_time)
            if start_time and start_time != "1970-01-01T00:00:00+0000":
                start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S%z")
                start_time = convert_to_mysql_datetime(start_time)
            else:
                start_time = None
            if end_time and end_time != "1970-01-01T00:00:00+0000":
                end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S%z")
                end_time = convert_to_mysql_datetime(end_time)
            else:
                end_time = None

            special_ad_categories = campaign.get("special_ad_categories", "")
            if isinstance(special_ad_categories, list):
                special_ad_categories = ",".join(special_ad_categories)

            if existing_campaign:
                existing_campaign.name = campaign.get("name", existing_campaign.name)
                existing_campaign.objective = campaign.get(
                    "objective", existing_campaign.objective
                )
                existing_campaign.status = campaign.get(
                    "status", existing_campaign.status
                )
                existing_campaign.created_time = (
                    created_time or existing_campaign.created_time
                )
                existing_campaign.start_time = (
                    start_time or existing_campaign.start_time
                )
                existing_campaign.end_time = end_time or existing_campaign.end_time
                existing_campaign.special_ad_categories = special_ad_categories
                db.session.commit()
                updated_count += 1
            else:
                new_campaign = FacebookCampaign(
                    facebook_campaign_id=campaign["id"],
                    name=campaign.get("name"),
                    objective=campaign.get("objective"),
                    status=campaign.get("status"),
                    created_time=created_time,
                    start_time=start_time,
                    end_time=end_time,
                    facebook_account_id=facebook_account.id,
                    special_ad_categories=special_ad_categories,
                    facebook_ad_account_id=ad_account.id,
                )
                db.session.add(new_campaign)
                db.session.commit()
                created_count += 1

    return (
        f"Sync completed: {created_count} new campaigns created, {updated_count} campaigns updated.",
        True,
    )


def delete_facebook_account(id):
    try:
        account = FacebookAccount.query.get(id)

        if account:
            # Xóa tất cả các Page liên kết với tài khoản
            # for page in account.pages:
            #     for stack_posts in page.stack_posts:
            #         db.session.delete(stack_posts)
            #     db.session.delete(page)

            # Xóa tất cả các chiến dịch liên kết với tài khoản
            for campaign in account.facebook_campaigns:
                db.session.delete(campaign)

            # Xóa tất cả các tài khoản quảng cáo liên kết với tài khoản
            for ad_account in account.facebook_ad_accounts:
                db.session.delete(ad_account)

            # db.session.delete(account)
            db.session.commit()

            print("Facebook account and related data deleted successfully!", "success")
            return True
        else:
            print("Account not found.", "danger")
            return False
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}", "danger")
        return False


def fetch_facebook_ad_details(ad_id_list, adset_id_list, access_token):
    base_url = "https://graph.facebook.com/v21.0"

    # Gọi API cho từng adset_id
    print("\nFetching Ad Set Details:")
    for adset_id in adset_id_list:
        adset_url = f"{base_url}/{adset_id}"
        params = {"fields": "id,name,status,daily_budget", "access_token": access_token}

        response = requests.get(adset_url, params=params)
        if response.status_code == 200:
            adset_data = response.json()
            print(f"Ad Set {adset_id}: {adset_data}")
        else:
            flash("Đã gọi quá nhiều chuyển sang tài khoản ads khác hoặc đợi 1 tiếng")
            print(
                f"Failed to fetch Ad Set {adset_id}: {response.json().get('error', {}).get('message', 'Unknown error')}"
            )
            return False;

    # Gọi API cho từng ad_id
    print("\nFetching Ad Details:")
    for ad_id in ad_id_list:
        ad_url = f"{base_url}/{ad_id}"
        params = {
            "fields": "id,name,status,creative{object_type,object_story_spec,title,body}",
            "access_token": access_token,
        }

        response = requests.get(ad_url, params=params)
        if response.status_code == 200:
            ad_data = response.json()
            print(f"Ad {ad_id}: {ad_data}")
        else:
            flash("Đã gọi quá nhiều chuyển sang tài khoản ads khác hoặc đợi 1 tiếng")
            print(
                f"Failed to fetch Ad {ad_id}: {response.json().get('error', {}).get('message', 'Unknown error')}"
            )
            return False;
    return True;


def get_facebook_insights(ad_account_id, access_token):
    """
    Lấy dữ liệu báo cáo từ Facebook Ads API.

    Parameters:
        ad_account_id (str): ID của tài khoản quảng cáo Facebook.
        access_token (str): Mã token để xác thực API.
        start_date (str): Ngày bắt đầu (định dạng YYYY-MM-DD).
        end_date (str): Ngày kết thúc (định dạng YYYY-MM-DD).

    Returns:
        bool: False nếu có lỗi, in dữ liệu nếu thành công.
    """
    url = f"https://graph.facebook.com/v22.0/act_{ad_account_id}/insights"

    params = {
        "fields": "impressions,clicks,spend",
        "access_token": access_token,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Kiểm tra nếu có lỗi HTTP

        data = response.json()

        # Kiểm tra nếu phản hồi có lỗi từ API
        if "error" in data:
            print("Lỗi từ Facebook API:", data["error"]["message"])
            return False

        # In dữ liệu nhận được
        print("Dữ liệu nhận được:", data)
        return True

    except requests.exceptions.RequestException as e:
        print("Lỗi khi gửi yêu cầu:", e)
        return False
