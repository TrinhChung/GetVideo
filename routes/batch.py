from flask import Blueprint, render_template, request, redirect, url_for
from yt_list import get_playlist_info_and_video_details
from youtube import download_video
from flask_mysqldb import MySQL
from app import mysql

batch_bp = Blueprint("batch", __name__)


@batch_bp.route("/batch", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        get_playlist_info_and_video_details(
            request.form["playlist_url"], mysql.connection
        )
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM videos")
        videos = cur.fetchall()
        cur.close()
        return render_template("index.html", videos=videos)

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM videos")
    videos = cur.fetchall()
    cur.close()
    return render_template("index.html", videos=videos)


@batch_bp.route("/download/<video_id>", methods=["POST"])
def download_video_route(video_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM videos WHERE id = %s", (video_id,))
    video = cur.fetchone()

    if video and video[3] == "No":
        try:
            download_video(video_id)
            cur.execute(
                "UPDATE videos SET crawled = %s WHERE id = %s", ("Yes", video_id)
            )
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("index"))
        except Exception as e:
            cur.close()
            return render_template(
                "error.html", error_message=f"Đã xảy ra lỗi khi tải video: {e}"
            )

    cur.close()
    return redirect(url_for("index"))


@batch_bp.route("/download_all", methods=["POST"])
def download_all_videos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM videos WHERE crawled = 'No'")
    videos_to_download = cur.fetchall()

    for video in videos_to_download:
        try:
            download_video(video[0])
            cur.execute(
                "UPDATE videos SET crawled = %s WHERE id = %s", ("Yes", video[0])
            )
        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")

    mysql.connection.commit()
    cur.close()
    return redirect(url_for("index"))
