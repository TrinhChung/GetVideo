from flask import Blueprint, render_template, request, redirect, url_for, flash
from yt_list import get_playlist_info_and_video_details
from database_init import db
from models.playlist import Playlist
from models.video import Video
from until import extract_playlist_id
from youtube import download_video

batch_bp = Blueprint("batch", __name__)


# Route để hiển thị và quản lý playlist
@batch_bp.route("/batch/playlist", methods=["GET", "POST"])
def batch_youtube_playlist():
    if request.method == "POST":
        playlist_url = request.form["playlist_url"]
        playlist_id = extract_playlist_id(playlist_url)

        if not playlist_id:
            flash("Không thể trích xuất playlist ID từ URL", "danger")
            return redirect(url_for("batch.batch_youtube_playlist"))

        try:
            # Sử dụng get_playlist_info_and_video_details để xử lý playlist và cập nhật vào database
            get_playlist_info_and_video_details(playlist_id)
            flash("Playlist đã được thêm thành công", "success")
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi thêm playlist: {e}", "danger")

        return redirect(url_for("batch.batch_youtube_playlist"))

    playlists = Playlist.query.all()  # Lấy dữ liệu từ bảng Playlist bằng SQLAlchemy
    return render_template("playlist.html", playlists=playlists)


# Route để lấy video từ playlist
@batch_bp.route("/batch/get_video_from_playlist", methods=["POST"])
def get_video_from_playlist():
    playlist_id = request.form["playlist_id"]

    try:
        # Lấy thông tin video từ playlist
        get_playlist_info_and_video_details(playlist_id)
        flash("Video đã được thêm từ playlist", "success")
    except Exception as e:
        flash(f"Đã xảy ra lỗi khi lấy video từ playlist: {e}", "danger")
        return render_template(
            "error.html", error_message=f"Đã xảy ra lỗi khi lấy video từ playlist: {e}"
        )

    return redirect(url_for("batch.batch_youtube_playlist"))


# Route để lấy video từ tất cả playlist
@batch_bp.route("/batch/get_all_videos", methods=["POST"])
def get_all_videos():
    playlists = Playlist.query.all()  # Lấy tất cả playlist từ cơ sở dữ liệu

    for playlist in playlists:
        try:
            # Lấy thông tin video cho từng playlist
            get_playlist_info_and_video_details(playlist.id)  # Truyền playlist ID
            flash(f"Video đã được thêm từ playlist {playlist.title}", "success")
        except Exception as e:
            flash(
                f"Đã xảy ra lỗi khi lấy video từ playlist {playlist.title}: {e}",
                "danger",
            )
            print(f"Đã xảy ra lỗi khi lấy video từ playlist {playlist.title}: {e}")

    return redirect(url_for("batch.batch_youtube_playlist"))


# Route để hiển thị và quản lý video
@batch_bp.route("/batch/videos", methods=["GET", "POST"])
def index():
    videos = Video.query.all()  # Lấy tất cả video từ cơ sở dữ liệu
    return render_template("videos.html", videos=videos)


# Route để tải xuống video theo video_id
@batch_bp.route("/download/<video_id>", methods=["POST"])
def download_video_route(video_id):
    video = Video.query.filter_by(video_id=video_id).first()  # Lấy video từ database

    if video and not video.crawled:
        try:
            video_path, video_duration = download_video(video_id)

            # Lưu video path và video duration vào cơ sở dữ liệu
            video.path = video_path
            video.duration = video_duration
            video.crawled = True  # Đánh dấu video đã được tải xuống
            db.session.commit()

            flash("Video đã được tải xuống thành công", "success")
            return redirect(url_for("batch.index"))
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi tải video: {e}", "danger")
    else:
        flash("Video đã được tải hoặc không có trong hệ thống", "info")

    return redirect(url_for("batch.index"))

# Route để tải tất cả video chưa được tải xuống
@batch_bp.route("/batch/download_all", methods=["POST"])
def download_all_videos():
    videos_to_download = Video.query.filter_by(
        crawled=False
    ).all()  # Lấy các video chưa tải xuống

    for video in videos_to_download:
        try:
            video_path, video_duration = download_video(video.video_id)

            # Lưu video path và video duration vào cơ sở dữ liệu
            video.path = video_path
            video.duration = video_duration
            video.crawled = True
            db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu

            flash(f"Video {video.title} đã được tải xuống", "success")
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi tải video {video.title}: {e}", "danger")
            print(f"Đã xảy ra lỗi: {e}")

    return redirect(url_for("batch.index"))
