from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from util.yt_list import get_playlist_info_and_video_details
from database_init import db
from models.playlist import Playlist
from util.until import extract_playlist_id
from Form.playlist import PlaylistForm, GetVideoFromPlaylistForm, GetAllVideosForm

playlist_bp = Blueprint("playlist", __name__)


# Route để hiển thị và quản lý playlist
@playlist_bp.route("/batch/playlist", methods=["GET", "POST"])
def batch_youtube_playlist():
    form = PlaylistForm()

    user_id = session.get("user_id")  # Lấy user_id từ session
    if not user_id:
        flash("Bạn cần đăng nhập để sử dụng chức năng này", "danger")
        return redirect(url_for("auth.login"))

    if form.validate_on_submit():
        playlist_url = form.playlist_url.data
        playlist_id = extract_playlist_id(playlist_url)

        if not playlist_id:
            flash("Không thể trích xuất playlist ID từ URL", "danger")
            return redirect(url_for("playlist.batch_youtube_playlist"))

        try:
            get_playlist_info_and_video_details(playlist_id, user_id)
            flash("Playlist đã được thêm thành công", "success")
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi thêm playlist: {e}", "danger")

        return redirect(url_for("playlist.batch_youtube_playlist"))

    playlists = Playlist.query.filter_by(user_id=user_id).all()
    return render_template("playlist.html", playlists=playlists, form=form)


# Route để lấy video từ playlist
@playlist_bp.route("/batch/get_video_from_playlist", methods=["GET", "POST"])
def get_video_from_playlist():
    form = GetVideoFromPlaylistForm()

    user_id = session.get("user_id")  # Lấy user_id từ session
    if not user_id:
        flash("Bạn cần đăng nhập để sử dụng chức năng này", "danger")
        return redirect(url_for("auth.login"))

    if form.validate_on_submit():
        playlist_id = form.playlist_id.data

        try:
            get_playlist_info_and_video_details(playlist_id, user_id)
            flash("Video đã được thêm từ playlist", "success")
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi lấy video từ playlist: {e}", "danger")
            return render_template(
                "error.html",
                error_message=f"Đã xảy ra lỗi khi lấy video từ playlist: {e}",
            )

        return redirect(url_for("playlist.batch_youtube_playlist"))

    return redirect(url_for("playlist.batch_youtube_playlist"))


# Route để lấy video từ tất cả playlist
@playlist_bp.route("/batch/get_all_videos", methods=["POST"])
def get_all_videos():
    form = GetAllVideosForm()

    user_id = session.get("user_id")  # Lấy user_id từ session
    if not user_id:
        flash("Bạn cần đăng nhập để sử dụng chức năng này", "danger")
        return redirect(url_for("auth.login"))

    if form.validate_on_submit():
        playlists = Playlist.query.filter_by(user_id=user_id).all()

        for playlist in playlists:
            try:
                get_playlist_info_and_video_details(playlist.id, user_id)
                flash(f"Video đã được thêm từ playlist {playlist.title}", "success")
            except Exception as e:
                flash(
                    f"Đã xảy ra lỗi khi lấy video từ playlist {playlist.title}: {e}",
                    "danger",
                )
                print(f"Đã xảy ra lỗi khi lấy video từ playlist {playlist.title}: {e}")

    return redirect(url_for("playlist.batch_youtube_playlist"))
