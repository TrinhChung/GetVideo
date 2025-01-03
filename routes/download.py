from flask import Blueprint, render_template, request, flash
from youtube import download_video_by_url, download_video_facebook

download_bp = Blueprint("download", __name__)


@download_bp.route("/download-url", methods=["GET", "POST"])
def download_from_url():
    if request.method == "POST":
        video_url = request.form.get("video_url")
        if video_url:
            try:
                download_video_by_url(video_url)
                flash("Video đã được tải xuống thành công!", "success")
                return render_template("downloadFromUrl.html")
            except Exception as e:
                flash(f"Đã xảy ra lỗi: {e}", "danger")

    return render_template("downloadFromUrl.html")


@download_bp.route("/download-facebook-url", methods=["POST"])
def download_from_facebook_url():
    if request.method == "POST":
        video_url = request.form.get("video_url")
        if video_url:
            try:
                download_video_facebook(video_url)
                flash("Video từ Facebook đã được tải xuống thành công!", "success")
                return render_template("downloadFromUrl.html")
            except Exception as e:
                flash(f"Đã xảy ra lỗi: {e}", "danger")

    return render_template("downloadFromUrl.html")
