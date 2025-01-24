import os
import yt_dlp
from util.until import extract_facebook_video_id
import random
import string


def download_video_from_url(video_url, download_path):
    """
    Tải video từ một URL bất kỳ được hỗ trợ bởi yt_dlp.
    :param video_url: URL của video
    :param download_path: Thư mục lưu video (mặc định là DOWNLOAD_PATH)
    :return: Đường dẫn file video đã tải và độ dài video
    """
    # Tạo một chuỗi số ngẫu nhiên dài 12 chữ số
    random_digits = "".join(random.choices(string.digits, k=12))

    # Cài đặt các tùy chọn cho việc tải video
    ydl_opts = {
        "format": "best",  # Tải video có chất lượng tốt nhất
        "outtmpl": os.path.join(
            download_path, f"{random_digits}.%(ext)s"
        ),  # Lưu video vào thư mục chỉ định với tên là chuỗi số
        "noplaylist": True,  # Tải 1 video duy nhất, không tải playlist
        "quiet": False,  # Hiển thị thông tin tải về trong terminal
    }

    try:
        # Tải video vào thư mục chỉ định
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                video_url, download=True
            )  # Tải video và lấy thông tin
            video_path = os.path.join(download_path, f"{random_digits}.{info['ext']}")
            video_duration = info.get("duration", 0)
            print(f"Video đã được tải về: {video_path}")
            return video_path, video_duration
    except Exception as e:
        raise Exception(f"Đã xảy ra lỗi khi tải video: {e}")


def download_video(video_id):
    """
    Tải video từ YouTube bằng video_id.
    :param video_id: ID của video trên YouTube
    :return: Đường dẫn file video đã tải
    """
    # Thư mục lưu video mặc định
    DOWNLOAD_PATH = r"./Videos/Film/Youtube"

    # Tạo thư mục nếu chưa tồn tại
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)

    # Tạo URL YouTube từ video_id
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return download_video_from_url(video_url, DOWNLOAD_PATH)


def download_video_facebook(video_url):
    """
    Tải video từ YouTube bằng video_id.
    :param video_id: ID của video trên YouTube
    :return: Đường dẫn file video đã tải
    """
    video_id = extract_facebook_video_id(video_url);
    # Thư mục lưu video mặc định
    DOWNLOAD_PATH = r"./Videos/Film/Facebook"

    # Tạo thư mục nếu chưa tồn tại
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)

    # Tạo URL YouTube từ video_id
    video_url = f"https://www.facebook.com/watch/?v={video_id}"
    return download_video_from_url(video_url, DOWNLOAD_PATH)


def download_video_by_url(video_url):
    """
    Tải video từ YouTube bằng video_id.
    :param video_id: ID của video trên YouTube
    :return: Đường dẫn file video đã tải
    """
    # Thư mục lưu video mặc định
    DOWNLOAD_PATH = r"./Videos/Film/Tiktok"

    # Tạo thư mục nếu chưa tồn tại
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)

    return download_video_from_url(video_url, DOWNLOAD_PATH)
