import yt_dlp
from util.until import generate_playlist_url
from models.video import Video
from models.playlist import Playlist
from database_init import db


def get_existing_playlist(playlist_id, user_id):
    """
    Lấy thông tin playlist đã tồn tại từ database.
    Args:
        playlist_id: ID của playlist
    Returns:
        Tuple chứa (playlist_title, danh sách video_ids) hoặc None nếu không tồn tại
    """
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=user_id).first()

    if not playlist:
        return None

    existing_video_ids = [video.video_id for video in playlist.videos]

    return playlist.title, existing_video_ids


def get_playlist_info_and_video_details(playlist_id, user_id):
    """
    Hàm chính để xử lý playlist và cập nhật database.
    """
    try:
        # Bước 1: Lấy URL playlist từ ID
        playlist_url = generate_playlist_url(playlist_id)

        # Bước 2: Kiểm tra playlist trong database
        existing_data = get_existing_playlist(playlist_id, user_id)

        # Bước 3: Lấy thông tin mới từ YouTube
        yt_playlist_id, yt_playlist_title, yt_videos = get_playlist_from_youtube(
            playlist_url
        )

        # Bước 4: Xác thực ID playlist
        if playlist_id != yt_playlist_id:
            raise ValueError("ID playlist từ URL không khớp với dữ liệu từ YouTube")

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
                    playlist_id, yt_playlist_title, new_videos, user_id
                )
                print(f"Đã thêm {len(new_videos)} video mới vào playlist")
            else:
                print("Không có video mới để thêm")
        else:
            print("Thêm playlist mới...")
            save_playlist_and_videos_to_mysql(playlist_id, yt_playlist_title, yt_videos, user_id)
            print(f"Đã thêm playlist mới với {len(yt_videos)} video")

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")


# Lưu thông tin vào bảng playlist và videos
def save_playlist_and_videos_to_mysql(playlist_id, playlist_title, video_data, user_id):
    print("Đang lưu thông tin playlist và video...")
    print(user_id)

    # Lưu thông tin playlist vào bảng playlist
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=user_id).first()
    if not playlist:
        playlist = Playlist(id=playlist_id, title=playlist_title, user_id=user_id)
        db.session.add(playlist)

    # Lưu thông tin video vào bảng videos
    for video in video_data:
        # Kiểm tra nếu video đã tồn tại
        if not Video.query.filter_by(
            video_id=video["id"], playlist_id=playlist_id, user_id=user_id
        ).first():
            video_entry = Video(
                video_id=video["id"],
                title=video["title"],
                playlist_id=playlist_id,
                crawled=False,  # False: video chưa được crawl
                user_id=user_id
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

            playlist_id = info_dict.get("id", "Unknown ID")
            playlist_title = info_dict.get("title", "Unknown Title")

            video_data = [
                {"id": video["id"], "title": video["title"]}
                for video in info_dict["entries"]
            ]

            return playlist_id, playlist_title, video_data
    except Exception as e:
        raise Exception(f"Lỗi khi lấy thông tin playlist: {e}")
