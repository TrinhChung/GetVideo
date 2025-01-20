from flask import Blueprint, render_template, request, redirect, url_for, flash, session
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

    facebook_account_id = session.get("facebook_user_id")  # Lấy user_id từ session
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    # Lấy tham số từ query string
    page_id = request.args.get("page_id")
    status = request.args.get("status")

    # Query cơ bản
    query = StackPost.query

    # Áp dụng các bộ lọc nếu có
    if page_id:
        query = query.filter_by(
            page_id=page_id, facebook_account_id=facebook_account_id
        )
    if status:
        query = query.filter_by(status=status, facebook_account_id=facebook_account_id)

    # Sắp xếp theo thời gian
    query = query.order_by(StackPost.time.asc())

    # Lấy danh sách bài đăng
    stack_posts = query.filter_by(facebook_account_id=facebook_account_id)

    # Lấy danh sách các trang để hiển thị trong form lọc
    pages = Page.query.filter_by(facebook_account_id=facebook_account_id)

    return render_template(
        "stack_posts.html",
        stack_posts=stack_posts,
        pages=pages,  # Truyền danh sách các trang
        form=form,  # Truyền form vào template
        page_id=page_id,  # Truyền page_id để giữ lại giá trị trong form
        status=status,
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
                posted_video_id = create_video_post(
                    page_id=page.page_id,
                    access_token=page.access_token,
                    video_path=post.video_split.path,
                    message=post.title,
                )

                # Cập nhật trạng thái thành công
                post.status = "posted"
                post.video_id = posted_video_id  # Cập nhật ID video
                db.session.commit()
                flash("Posted video successfully", "success")

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


@stack_post_bp.route("/stack_posts/delete_selected", methods=["POST"])
def delete_selected():
    selected_posts = request.form.getlist(
        "selected_posts[]"
    )  # Lấy danh sách ID từ request
    print(selected_posts)  # Kiểm tra danh sách ID
    if not selected_posts:
        flash("Không có bài viết nào được chọn để xóa.", "warning")
        return redirect(url_for("stack_post.index"))

    try:
        # Xóa các bài viết được chọn
        StackPost.query.filter(StackPost.id.in_(selected_posts)).delete(
            synchronize_session=False
        )
        db.session.commit()
        flash(f"Đã xóa {len(selected_posts)} bài viết.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi khi xóa bài viết: {str(e)}", "danger")

    return redirect(url_for("stack_post.index"))
