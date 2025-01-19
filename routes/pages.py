# routes/pages.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.page import Page  # Import model Page đã tạo
from util.post_fb import check_token_expiry  # Import hàm check_token_expiry
from Form.page import PageForm  # Import form PageForm đã tạo
# Tạo blueprint cho pages
pages_bp = Blueprint("pages", __name__)


# Route để hiển thị danh sách các pages
@pages_bp.route("/pages")
def show_pages():
    form = PageForm()  # Tạo form mới

    facebook_account_id = session.get("facebook_user_id")  # Lấy user_id từ session
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    # Sử dụng SQLAlchemy để lấy tất cả các pages
    pages = Page.query.filter_by(
        facebook_account_id=facebook_account_id
    ).all()  # Lấy tất cả các trang từ bảng 'pages'
    # Trả về trang HTML với danh sách pages
    return render_template("pages.html", pages=pages, form=form)

# Route để debug token và lưu expires_at
@pages_bp.route("/pages/debug-token", methods=["POST"])
def debug_token():
    token = request.form.get("token")  # Lấy token từ biểu mẫu
    page_id = request.form.get("page_id")  # Lấy page_id từ biểu mẫu

    if not token or not page_id:
        flash("Token and Page ID are required.", "error")
        return redirect(url_for("pages.show_pages"))

    try:
        # Gọi hàm check_token_expiry từ post_fb.py
        check_token_expiry(token, page_id)
    except Exception as e:
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("pages.show_pages"))
