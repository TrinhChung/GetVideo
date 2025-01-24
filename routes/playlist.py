from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from util.yt_list import get_playlist_info_and_video_details
from database_init import db
from models.playlist import Playlist
from Form.playlist import PlaylistForm, GetVideoFromPlaylistForm, GetAllVideosForm

playlist_bp = Blueprint("playlist", __name__)


# Route để hiển thị và quản lý playlist
@playlist_bp.route("/batch/playlist", methods=["GET", "POST"])
def batch_youtube_playlist():
    form = PlaylistForm()

    facebook_account_id = session.get("facebook_user_id")  # Lấy user_id từ session
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))
    print(facebook_account_id)

    if form.validate_on_submit():
        playlist_url = form.playlist_url.data

        try:
            get_playlist_info_and_video_details(playlist_url, facebook_account_id)
            flash("Playlist đã được thêm thành công", "success")
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi thêm playlist: {e}", "danger")

        return redirect(url_for("playlist.batch_youtube_playlist"))

    playlists = Playlist.query.filter_by(facebook_account_id=facebook_account_id).all()
    return render_template("playlist.html", playlists=playlists, form=form)


# Route để lấy video từ playlist
@playlist_bp.route("/batch/get_video_from_playlist", methods=["GET", "POST"])
def get_video_from_playlist():
    form = GetVideoFromPlaylistForm()

    facebook_account_id = session.get("facebook_user_id")  # Lấy user_id từ session
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    if form.validate_on_submit():
        playlist_id = form.playlist_id.data

        try:
            get_playlist_info_and_video_details(playlist_id, facebook_account_id)
            flash("Video đã được thêm từ playlist", "success")
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi lấy video từ playlist: {e}", "danger")
    else:
        flash("Tham số truyền vào không hợp lệ", "danger")

    return redirect(url_for("playlist.batch_youtube_playlist"))


# Route để lấy video từ tất cả playlist
@playlist_bp.route("/batch/get_all_videos", methods=["POST"])
def get_all_videos():
    form = GetAllVideosForm()

    facebook_account_id = session.get("facebook_user_id")  # Lấy user_id từ session
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    if form.validate_on_submit():
        playlists = Playlist.query.filter_by(
            facebook_account_id=facebook_account_id
        ).all()

        for playlist in playlists:
            try:
                get_playlist_info_and_video_details(
                    playlist.playlist_id, facebook_account_id
                )
                flash(f"Video đã được thêm từ playlist {playlist.title}", "success")
            except Exception as e:
                flash(
                    f"Đã xảy ra lỗi khi lấy video từ playlist {playlist.title}: {e}",
                    "danger",
                )

    return redirect(url_for("playlist.batch_youtube_playlist"))
