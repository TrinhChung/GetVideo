from flask import Blueprint, render_template, request, flash
from util.youtube import download_video_by_url, download_video_facebook
from Form.download import VideoDownloadForm

download_bp = Blueprint("download", __name__)


@download_bp.route("/download-url", methods=["GET", "POST"])
def download_from_url():
    form = VideoDownloadForm()

    if form.validate_on_submit():
        video_url = form.video_url.data
        try:
            download_video_by_url(
                video_url
            )  # Giả sử hàm download_video_by_url xử lý tải video
            flash("Video đã được tải xuống thành công!", "success")
            return render_template("downloadFromUrl.html", form=form)
        except Exception as e:
            flash(f"Đã xảy ra lỗi: {e}", "danger")

    return render_template("downloadFromUrl.html", form=form)


@download_bp.route("/download-facebook-url", methods=["POST"])
def download_from_facebook_url():
    form = VideoDownloadForm()

    if form.validate_on_submit():
        video_url = form.video_url.data
        try:
            download_video_facebook(
                video_url
            )  # Giả sử hàm download_video_facebook xử lý tải video từ Facebook
            flash("Video từ Facebook đã được tải xuống thành công!", "success")
            return render_template("downloadFromUrl.html", form=form)
        except Exception as e:
            flash(f"Đã xảy ra lỗi: {e}", "danger")

    return render_template("downloadFromUrl.html", form=form)
