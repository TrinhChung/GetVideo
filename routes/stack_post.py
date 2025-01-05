from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.stack_post import StackPost
from models.page import Page
from database_init import db
from util.post_fb import create_video_post
from Form.stack_post import StackPostForm

stack_post_bp = Blueprint("stack_post", __name__)


@stack_post_bp.route("/stack_posts", methods=["GET"])
def index():
    # Khởi tạo form
    form = StackPostForm()

    # Lấy tham số từ query string
    page_id = request.args.get("page_id", type=int)
    status = request.args.get("status")

    # Query cơ bản
    query = StackPost.query

    # Áp dụng các bộ lọc nếu có
    if page_id:
        query = query.filter_by(page_id=page_id)
    if status:
        query = query.filter_by(status=status)

    # Sắp xếp theo thời gian
    query = query.order_by(StackPost.time.asc())

    # Lấy danh sách bài đăng
    stack_posts = query.all()

    return render_template(
        "stack_posts.html",
        stack_posts=stack_posts,
        form=form,  # Truyền form vào template
    )


@stack_post_bp.route("/stack_post/post_video/<int:post_id>", methods=["POST"])
def post_video(post_id):
    form = StackPostForm()

    if form.validate_on_submit():  # Kiểm tra nếu form hợp lệ và đã được submit
        try:
            # Lấy thông tin stack post
            post = StackPost.query.get_or_404(post_id)

            # Lấy thông tin page
            page = Page.query.get(post.page_id)
            if not page or not page.access_token:
                flash("Không tìm thấy thông tin page hoặc access token", "danger")
                return redirect(url_for("stack_post.index"))

            # Lấy đường dẫn video từ video_split
            if not post.video_split or not post.video_split.path:
                flash("Không tìm thấy đường dẫn video", "danger")
                return redirect(url_for("stack_post.index"))

            # Cập nhật trạng thái sang processing
            post.status = "processing"
            db.session.commit()

            # Thực hiện đăng video
            try:
                create_video_post(
                    page_id=page.page_id,
                    access_token=page.access_token,
                    video_path=post.video_split.path,
                    message=post.title,
                )

                # Cập nhật trạng thái thành công
                post.status = "posted"
                db.session.commit()
                flash("Đăng video thành công", "success")

            except Exception as e:
                # Cập nhật trạng thái lỗi
                post.status = "error"
                db.session.commit()
                raise e

        except Exception as e:
            flash(f"Lỗi khi đăng video: {str(e)}", "danger")

        return redirect(url_for("stack_post.index"))

    # Nếu form chưa được submit hoặc không hợp lệ, chỉ render lại trang danh sách bài viết
    flash("Dữ liệu không hợp lệ hoặc yêu cầu không được gửi đúng cách", "danger")
    return redirect(url_for("stack_post.index"))
