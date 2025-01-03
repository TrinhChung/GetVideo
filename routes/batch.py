from flask import Blueprint, render_template, request, redirect, url_for, flash
from yt_list import get_playlist_info_and_video_details
from youtube import download_video
from database_init import mysql
from until import extract_playlist_id

batch_bp = Blueprint("batch", __name__)


# Route để hiển thị danh sách playlist và thêm playlist mới
@batch_bp.route("/batch/playlist", methods=["GET", "POST"])
def batch_youtube_playlist():
    if request.method == "POST":
        playlist_url = request.form["playlist_url"]
        playlist_id = extract_playlist_id(playlist_url)

        if not playlist_id:
            flash("Không thể trích xuất playlist ID từ URL", "danger")
            return redirect(url_for("batch.batch_youtube_playlist"))

        try:
            get_playlist_info_and_video_details(playlist_id, mysql.connection)
            flash("Playlist đã được thêm thành công", "success")
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi thêm playlist: {e}", "danger")

        return redirect(url_for("batch.batch_youtube_playlist"))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM playlist")
    playlists = cur.fetchall()
    cur.close()

    return render_template("playlist.html", playlists=playlists)


# Route để lấy video từ một playlist cụ thể
@batch_bp.route("/batch/get_video_from_playlist", methods=["POST"])
def get_video_from_playlist():
    playlist_id = request.form["playlist_id"]

    try:
        # Lấy thông tin video từ playlist
        get_playlist_info_and_video_details(playlist_id, mysql.connection)
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
    # Truy vấn tất cả playlist
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM playlist")
    playlists = cur.fetchall()

    for playlist in playlists:
        try:
            # Lấy thông tin video cho từng playlist
            get_playlist_info_and_video_details(playlist[0], mysql.connection)
            flash(f"Video đã được thêm từ playlist {playlist[1]}", "success")
        except Exception as e:
            flash(
                f"Đã xảy ra lỗi khi lấy video từ playlist {playlist[1]}: {e}", "danger"
            )
            print(f"Đã xảy ra lỗi khi lấy video từ playlist {playlist[1]}: {e}")

    return redirect(url_for("batch.batch_youtube_playlist"))


# Route để hiển thị và quản lý video
@batch_bp.route("/batch/videos", methods=["GET", "POST"])
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM videos")
    videos = cur.fetchall()
    cur.close()
    return render_template("videos.html", videos=videos)


@batch_bp.route("/download/<video_id>", methods=["POST"])
def download_video_route(video_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM videos WHERE video_id = %s", (video_id,))
    video = cur.fetchone()

    if video and video[3] == False:
        try:
            video_path, video_duration = download_video(video_id)

            # Lưu video path và video duration vào cơ sở dữ liệu
            cur.execute(
                "UPDATE videos SET crawled = %s, path = %s, duration = %s WHERE video_id = %s",
                (True, video_path, video_duration, video_id),
            )
            mysql.connection.commit()
            cur.close()
            flash("Video đã được tải xuống thành công", "success")
            return redirect(url_for("batch.index"))
        except Exception as e:
            cur.close()
            flash(f"Đã xảy ra lỗi khi tải video: {e}", "danger")

    cur.close()
    flash("Video đã được tải hoặc không có trong hệ thống", "info")
    return redirect(url_for("batch.index"))


@batch_bp.route("/batch/download_all", methods=["POST"])
def download_all_videos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM videos WHERE crawled = 'No'")
    videos_to_download = cur.fetchall()
    print(videos_to_download)

    for video in videos_to_download:
        try:
            video_path, video_duration = download_video(video[1])

            # Lưu video path và video duration vào cơ sở dữ liệu
            cur.execute(
                "UPDATE videos SET crawled = %s, path = %s, duration = %s WHERE id = %s",
                (True, video_path, video_duration, video[0]),
            )
            flash(f"Video {video[2]} đã được tải xuống", "success")
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi tải video {video[2]}: {e}", "danger")
            print(f"Đã xảy ra lỗi: {e}")

    mysql.connection.commit()
    cur.close()
    return redirect(url_for("batch.index"))
