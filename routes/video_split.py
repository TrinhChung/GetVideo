from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.video_split import VideoSplit
from models.page import Page
from models.stack_post import StackPost
from datetime import datetime, timedelta
from database_init import db
from Form.video_split import VideoSplitScheduleForm

# Tạo Blueprint cho video_split
video_split_bp = Blueprint("video_split", __name__)


# Route để hiển thị các video đã chia nhỏ và danh sách các trang (Page)
@video_split_bp.route("/video_splits", methods=["GET"])
def video_splits():
    # Tạo form mới
    form = VideoSplitScheduleForm()

    facebook_account_id = session.get("facebook_user_id")  # Lấy user_id từ session
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    # Lấy tất cả video splits từ cơ sở dữ liệu
    video_splits = VideoSplit.query.filter_by(
        facebook_account_id=facebook_account_id
    ).all()

    # Lấy tất cả các trang (Page)
    pages = Page.query.filter_by(facebook_account_id=facebook_account_id).all()

    # Cập nhật choices cho form
    form.page_id.choices = [(page.page_id, page.name) for page in pages]
    form.selected_splits.choices = [(split.id, split.title) for split in video_splits]

    # Render template và truyền vào form, danh sách video splits và các trang
    return render_template(
        "video_splits.html", form=form, video_splits=video_splits, pages=pages
    )


# Route để thêm các video vào lịch phát hành
@video_split_bp.route("/add_to_schedule", methods=["POST"])
def add_to_schedule():
    form = VideoSplitScheduleForm()

    facebook_account_id = session.get("facebook_user_id")  # Lấy user_id từ session
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    # Lấy tất cả pages và video splits để cập nhật choices
    pages = Page.query.filter_by(facebook_account_id=facebook_account_id).all()
    video_splits = VideoSplit.query.filter_by(
        facebook_account_id=facebook_account_id
    ).all()
    form.page_id.choices = [(page.page_id, page.name) for page in pages]
    form.selected_splits.choices = [(split.id, split.title) for split in video_splits]

    if form.validate_on_submit():
        try:
            # Tìm thời gian lớn nhất của các bản ghi StackPost có cùng page_id
            last_post = (
                StackPost.query.filter_by(page_id=form.page_id.data)
                .order_by(StackPost.time.desc())
                .first()
            )

            # Tính toán thời gian bắt đầu
            if last_post:
                start_time = last_post.time + timedelta(hours=2)
            else:
                start_time = datetime.utcnow() + timedelta(hours=2)

            # Đếm số video thực sự được thêm
            videos_added = 0
            videos_skipped = 0

            # Thêm các video vào lịch phát hành
            for index, split_id in enumerate(form.selected_splits.data):
                # Kiểm tra xem bản ghi đã tồn tại chưa
                existing_post = StackPost.query.filter_by(
                    page_id=form.page_id.data,
                    video_split_id=split_id,
                    facebook_account_id=facebook_account_id,
                ).first()

                if existing_post:
                    videos_skipped += 1
                    continue

                # Lấy tiêu đề của video split từ cơ sở dữ liệu
                video_split = VideoSplit.query.get(split_id)

                if video_split:
                    title = video_split.title
                else:
                    title = f"Video {split_id}"

                # Tính thời gian cho video hiện tại
                current_time = start_time + timedelta(hours=2 * videos_added)

                # Tạo StackPost mới cho video
                new_stack_post = StackPost(
                    page_id=form.page_id.data,
                    time=current_time,
                    video_split_id=split_id,
                    title=title,
                    status="waiting",
                    facebook_account_id=facebook_account_id,
                )

                db.session.add(new_stack_post)
                videos_added += 1

            # Lưu các thay đổi vào cơ sở dữ liệu
            db.session.commit()

            # Hiển thị thông báo phù hợp
            if videos_added > 0:
                if videos_skipped > 0:
                    flash(
                        f"Đã thêm {videos_added} video mới vào lịch phát hành. "
                        f"{videos_skipped} video đã bỏ qua do đã tồn tại.",
                        "success",
                    )
                else:
                    flash(
                        f"Đã thêm {videos_added} video vào lịch phát hành thành công",
                        "success",
                    )
            else:
                flash(
                    "Không có video nào được thêm mới. Tất cả video đã tồn tại trong lịch phát hành.",
                    "info",
                )

        except Exception as e:
            db.session.rollback()
            flash(f"Đã xảy ra lỗi: {e}", "danger")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Lỗi ở trường {field}: {error}", "danger")

    return redirect(url_for("video_split.video_splits"))
