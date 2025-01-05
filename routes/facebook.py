from flask import Blueprint, render_template, request, redirect, url_for, flash
from database_init import db
from models.facebook_account import FacebookAccount
from util.post_fb import get_account
from Form.account_fb import AddFacebookAccountForm

facebook_bp = Blueprint("facebook", __name__)


# Lấy danh sách tài khoản Facebook
@facebook_bp.route("/account_fb/")
def account_fb():
    form = AddFacebookAccountForm()
    accounts = FacebookAccount.query.all()  # Lấy tất cả các tài khoản từ bảng
    return render_template("account_fb.html", accounts=accounts, form=form)


# Thêm hoặc cập nhật tài khoản Facebook
@facebook_bp.route("/account_fb/add_account", methods=["GET", "POST"])
def add_fb_account():
    form = AddFacebookAccountForm()

    # Lấy danh sách tài khoản Facebook hiện có
    accounts = FacebookAccount.query.all()

    if form.validate_on_submit():
        email = form.email.data
        access_token = form.access_token.data

        # Kiểm tra nếu tài khoản đã tồn tại
        existing_account = FacebookAccount.query.filter_by(email=email).first()

        if existing_account:
            # Nếu tài khoản đã tồn tại, cập nhật thông tin access_token
            existing_account.access_token = access_token
            try:
                db.session.commit()  # Cam kết thay đổi vào cơ sở dữ liệu
                flash("Facebook account updated successfully!", "success")
            except Exception as e:
                db.session.rollback()  # Nếu có lỗi, rollback để đảm bảo tính toàn vẹn dữ liệu
                flash(f"Error: {e}", "danger")
        else:
            # Nếu tài khoản chưa tồn tại, tạo tài khoản mới
            new_account = FacebookAccount(email=email, access_token=access_token)
            try:
                db.session.add(new_account)  # Thêm vào phiên làm việc của SQLAlchemy
                db.session.commit()  # Cam kết thay đổi vào cơ sở dữ liệu
                flash("Facebook account added successfully!", "success")
            except Exception as e:
                db.session.rollback()  # Nếu có lỗi, rollback để đảm bảo tính toàn vẹn dữ liệu
                flash(f"Error: {e}", "danger")

        return redirect(url_for("facebook.account_fb"))

    # Nếu form không hợp lệ, trả về trang account_fb với thông tin tài khoản và form hiện tại
    return render_template("account_fb.html", accounts=accounts, form=form)


# Xóa tài khoản Facebook
@facebook_bp.route("/account_fb/delete_account/<int:id>", methods=["GET", "POST"])
def delete_fb_account(id):
    try:
        account = FacebookAccount.query.get(id)  # Tìm tài khoản theo ID
        if account:
            db.session.delete(account)  # Xóa tài khoản
            db.session.commit()  # Cam kết thay đổi vào cơ sở dữ liệu
            flash("Facebook account deleted successfully!", "success")
        else:
            flash("Account not found.", "danger")
    except Exception as e:
        db.session.rollback()  # Nếu có lỗi, rollback để đảm bảo tính toàn vẹn dữ liệu
        flash(f"Error: {e}", "danger")

    return redirect(url_for("facebook.account_fb"))


# Lấy các trang Facebook liên kết với tài khoản
@facebook_bp.route("/account_fb/get_pages", methods=["POST"])
def get_pages():
    access_token = request.form.get("access_token")
    id = request.form.get("id")

    if not access_token:
        flash("Access token không được cung cấp.", "danger")
        error_message = "Access token không được cung cấp."
        return render_template("error.html", error_message=error_message)

    try:
        # Gọi hàm get_account để lấy danh sách các trang
        pages = get_account(access_token, id)
        if pages:
            flash("Lấy thông tin các trang thành công", "success")
            return redirect(url_for("pages.show_pages"))
        else:
            flash("Không thể lấy thông tin trang.", "danger")
            error_message = "Không thể lấy thông tin trang."
            return render_template("error.html", error_message=error_message)
    except Exception as e:
        flash(f"Lỗi: {e}", "danger")
        error_message = f"Lỗi: {e}"
        return render_template("error.html", error_message=error_message)
