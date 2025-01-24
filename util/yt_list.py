import yt_dlp
from util.until import generate_playlist_url
from models.video import Video
from models.playlist import Playlist
from database_init import db
from util.until import extract_playlist_id
from flask import redirect, url_for, flash

def get_existing_playlist(playlist_id, facebook_account_id):
    """
    Lấy thông tin playlist đã tồn tại từ database.
    Args:
        playlist_id: ID của playlist
    Returns:
        Tuple chứa (playlist_title, danh sách video_ids) hoặc None nếu không tồn tại
    """
    playlist = Playlist.query.filter_by(
        playlist_id=playlist_id, facebook_account_id=facebook_account_id
    ).first()

    if not playlist:
        return None

    existing_video_ids = [video.video_id for video in playlist.videos]

    return playlist.title, existing_video_ids


def get_playlist_info_and_video_details(playlist_id, facebook_account_id):
    """
    Hàm chính để xử lý playlist và cập nhật database.
    """
    try:
        # Bước 2: Kiểm tra playlist trong database
        existing_data = get_existing_playlist(playlist_id, facebook_account_id)

        # Bước 3: Lấy thông tin mới từ YouTube
        yt_playlist_title, yt_videos = get_playlist_or_channel_videos(
            playlist_id
        )

        # Bước 5: Xử lý dữ liệu
        if existing_data:
            existing_title, existing_video_ids = existing_data
            print(f"Playlist '{existing_title}' đã tồn tại. Kiểm tra video mới...")

            # Lọc ra các video chưa tồn tại
            new_videos = [
                video for video in yt_videos if video["id"] not in existing_video_ids
            ]

            if new_videos:
                save_playlist_and_videos_to_mysql(
                    playlist_id, yt_playlist_title, new_videos, facebook_account_id
                )
                flash(f"Đã thêm {len(new_videos)} video mới vào playlist")
            else:
                flash("Không có video mới để thêm")
        else:
            print("Thêm playlist mới...")
            save_playlist_and_videos_to_mysql(
                playlist_id, yt_playlist_title, yt_videos, facebook_account_id
            )
            flash(f"Đã thêm playlist mới với {len(yt_videos)} video")

    except Exception as e:
        raise Exception(f"Đã xảy ra lỗi: {e}")


# Lưu thông tin vào bảng playlist và videos
def save_playlist_and_videos_to_mysql(
    playlist_id, playlist_title, video_data, facebook_account_id
):
    print("Đang lưu thông tin playlist và video...")

    # Lưu thông tin playlist vào bảng playlist
    playlist = Playlist.query.filter_by(
        playlist_id=playlist_id, facebook_account_id=facebook_account_id
    ).first()
    if not playlist:
        playlist = Playlist(
            playlist_id=playlist_id,
            title=playlist_title,
            facebook_account_id=facebook_account_id,
        )
        db.session.add(playlist)
    else:
        playlist.title = playlist_title
        playlist.facebook_account_id = facebook_account_id

    # Lưu thông tin video vào bảng videos
    for video in video_data:
        # Kiểm tra nếu video đã tồn tại
        if not Video.query.filter_by(
            video_id=video["id"],
            playlist_id=playlist.id,
            facebook_account_id=facebook_account_id,
        ).first():
            video_entry = Video(
                video_id=video["id"],
                title=video["title"],
                playlist_id=playlist.id,
                crawled=False,  # False: video chưa được crawl
                facebook_account_id=facebook_account_id,
            )
            db.session.add(video_entry)

    # Commit và đóng kết nối
    db.session.commit()

    print(f"Thông tin playlist và video đã được lưu vào MySQL.")


def get_playlist_from_youtube(playlist_url):
    """
    Lấy thông tin playlist từ YouTube sử dụng yt-dlp.
    Args:
        playlist_url: URL của playlist YouTube
    Returns:
        Tuple chứa (playlist_id, playlist_title, danh sách video)
    """
    ydl_opts = {
        "extract_flat": True,
        "quiet": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(playlist_url, download=False)

            if not info_dict.get("entries"):
                raise ValueError("Không tìm thấy video trong playlist")

            playlist_title = info_dict.get("title", "Unknown Title")

            video_data = [
                {"id": video["id"], "title": video["title"]}
                for video in info_dict["entries"]
            ]

            return playlist_title, video_data
    except Exception as e:
        raise Exception(f"Lỗi khi lấy thông tin playlist: {e}")


def get_playlist_or_channel_videos(url):
    """
    Lấy thông tin playlist hoặc kênh từ YouTube sử dụng yt-dlp.
    Args:
        url: URL của playlist hoặc kênh YouTube
    Returns:
        Tuple chứa (playlist_id, playlist_title, danh sách video)
    """
    ydl_opts = {
        "extract_flat": True,
        "quiet": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            if not info_dict.get("entries"):
                raise ValueError("Không tìm thấy video trong playlist hoặc kênh")

            playlist_title = info_dict.get("title", "Unknown Title")

            video_data = []
            for video in info_dict["entries"]:
                # Kiểm tra xem video có thông tin đầy đủ không
                if video and "id" in video and "title" in video:
                    video_data.append({"id": video["id"], "title": video["title"]})

            return playlist_title, video_data
    except Exception as e:
        raise Exception(f"Lỗi khi lấy thông tin: {e}")
