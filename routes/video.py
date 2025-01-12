from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    Response,
    session,
)
from database_init import db
from models.video import Video
from util.youtube import download_video
from util.split_video import split_video  # Nhập hàm split_video
from Form.video import VideoDownloadForm, VideoSplitForm

video_bp = Blueprint("video", __name__)

VIDEO_FOLDER = './'

# Route để hiển thị và quản lý video
@video_bp.route("/videos", methods=["GET"])
def index():
    form = VideoDownloadForm()

    user_id = session.get("user_id")  # Lấy user_id từ session
    if not user_id:
        flash("Bạn cần đăng nhập để sử dụng chức năng này", "danger")
        return redirect(url_for("auth.login"))
    
    videos = Video.query.filter_by(user_id=user_id).all()
    form = VideoDownloadForm()
    return render_template("videos.html", videos=videos, form=form)


# Route để tải xuống video theo video_id
@video_bp.route("/download/<video_id>", methods=["GET"])
def download_video_route(video_id):
    video = Video.query.filter_by(video_id=video_id).first()

    if video and not video.crawled:
        try:
            video_path, video_duration = download_video(video_id)
            video.path = video_path
            video.duration = video_duration
            video.crawled = True
            db.session.commit()

            flash("Video đã được tải xuống thành công", "success")
            return redirect(url_for("video.index"))
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi tải video: {e}", "danger")
    else:
        flash("Video đã được tải hoặc không có trong hệ thống", "info")

    return redirect(url_for("video.index"))


# Route để tải tất cả video chưa được tải xuống
@video_bp.route("/video/download_all", methods=["POST"])
def download_all_videos():

    user_id = session.get("user_id")  # Lấy user_id từ session
    if not user_id:
        flash("Bạn cần đăng nhập để sử dụng chức năng này", "danger")
        return redirect(url_for("auth.login"))
    
    videos_to_download = Video.query.filter_by(crawled=False, user_id=user_id).all()

    for video in videos_to_download:
        try:
            video_path, video_duration = download_video(video.video_id)
            video.path = video_path
            video.duration = video_duration
            video.crawled = True
            db.session.commit()

            flash(f"Video {video.title} đã được tải xuống", "success")
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi tải video {video.title}: {e}", "danger")
            print(f"Đã xảy ra lỗi: {e}")

    return redirect(url_for("video.index"))


# Route để chia video
@video_bp.route("/split_video/<video_id>", methods=["POST"])
def split_video_route(video_id):
    user_id = session.get("user_id")  # Lấy user_id từ session
    if not user_id:
        flash("Bạn cần đăng nhập để sử dụng chức năng này", "danger")
        return redirect(url_for("auth.login"))

    video = Video.query.filter_by(video_id=video_id).first()

    if video and video.path:
        try:
            segment_duration_sec = 60  # Chỉnh sửa thời gian chia đoạn theo nhu cầu
            split_video(video.path, segment_duration_sec, user_id)

            flash("Video đã được chia thành các phần", "success")
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi chia video: {e}", "danger")
    else:
        flash("Video không hợp lệ hoặc chưa có đường dẫn", "info")

    return redirect(url_for("video.index"))

# Route để chia các video đã chọn
@video_bp.route("/split_selected_videos", methods=["POST"])
def split_selected_videos():
    user_id = session.get("user_id")  # Lấy user_id từ session
    if not user_id:
        flash("Bạn cần đăng nhập để sử dụng chức năng này", "danger")
        return redirect(url_for("auth.login"))
    
    ids = request.form.getlist(
        "selected_videos"
    )  # Lấy danh sách video_id đã chọn
    split_duration = request.form.get("split_duration", type=int)

    # Lặp qua từng video đã chọn và chia video
    for id in ids:
        video = Video.query.filter_by(id=id).first()
        print(video.path)

        if video and video.path:
            try:
                split_video(video.path, split_duration, user_id)
                flash(f"Video {video.title} đã được chia thành các phần", "success")
            except Exception as e:
                flash(f"Đã xảy ra lỗi khi chia video {video.title}: {e}", "danger")
        else:
            flash(f"Video {id} không hợp lệ hoặc chưa có đường dẫn", "info")

    return redirect(url_for("video.index"))

@video_bp.route('/videos/<path:filename>')
def serve_video(filename):
    try:
        # Serve the file with correct Content-Type
        response = send_from_directory(VIDEO_FOLDER, filename)
        response.headers["Content-Type"] = "video/mp4"
        return response
    except FileNotFoundError:
        return Response("File not found", status=404)
