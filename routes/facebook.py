from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from database_init import db
from models.facebook_account import FacebookAccount
from util.post_fb import get_account, get_ad_accounts
from Form.account_fb import AddFacebookAccountForm
import os
from dotenv import load_dotenv
from models.facebook_ad_account import FacebookAdAccount

load_dotenv()  # Đọc file .env

facebook_bp = Blueprint("facebook", __name__)


# Lấy danh sách tài khoản Facebook
@facebook_bp.route("/account_fb/")
def account_fb():
    facebook_app_id = os.getenv("APP_ID")

    form = AddFacebookAccountForm()

    user_id = session.get("user_id")  # Lấy user_id từ session
    if not user_id:
        flash("Bạn cần đăng nhập để sử dụng chức năng này", "danger")
        return redirect(url_for("auth.login"))

    accounts = FacebookAccount.query.filter_by(user_id=user_id).all()  # Lấy tất cả các tài khoản từ bảng
    return render_template(
        "account_fb.html", accounts=accounts, form=form, facebook_app_id=facebook_app_id
    )


# Thêm hoặc cập nhật tài khoản Facebook
@facebook_bp.route("/account_fb/add_account", methods=["GET", "POST"])
def add_fb_account():
    form = AddFacebookAccountForm()

    user_id = session.get("user_id")  # Get user_id from session
    if not user_id:
        flash("Bạn cần đăng nhập để sử dụng chức năng này", "danger")
        return redirect(url_for("auth.login"))

    # Get existing Facebook accounts for the user
    accounts = FacebookAccount.query.filter_by(user_id=user_id).all()

    if form.validate_on_submit():
        facebook_user_id = (
            form.facebook_user_id.data
        )  # Assuming 'email' form field is now facebook_user_id
        access_token = form.access_token.data

        # Check if account already exists
        existing_account = FacebookAccount.query.filter_by(
            facebook_user_id=facebook_user_id
        ).first()

        if existing_account:
            # Update access_token if account exists
            existing_account.access_token = access_token
            try:
                db.session.commit()
                flash("Facebook account updated successfully!", "success")
                # If the request is an API request, return a JSON response
                if request.is_json:
                    return jsonify(
                        {
                            "success": True,
                            "message": "Facebook account updated successfully!",
                        }
                    )
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", "danger")
                return jsonify({"success": False, "message": f"Error: {e}"}), 500
        else:
            # Create new account if not exists
            new_account = FacebookAccount(
                facebook_user_id=facebook_user_id,
                access_token=access_token,
                user_id=user_id,
            )
            try:
                db.session.add(new_account)
                db.session.commit()
                flash("Facebook account added successfully!", "success")
                # If the request is an API request, return a JSON response
                if request.is_json:
                    return jsonify(
                        {
                            "success": True,
                            "message": "Facebook account added successfully!",
                        }
                    )
                return redirect(url_for("facebook.account_fb"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", "danger")
                return jsonify({"success": False, "message": f"Error: {e}"}), 500
    else:
        flash("Giá trị điền không hợp lệ!", "danger")
        return redirect(url_for("facebook.account_fb"))


# Xóa tài khoản Facebook
@facebook_bp.route("/account_fb/delete_account/<int:id>", methods=["GET", "POST"])
def delete_fb_account(id):
    try:
        account = FacebookAccount.query.get(id)  # Tìm tài khoản theo ID
        if account:
            # Xóa tất cả các Page liên kết với tài khoản
            for page in account.pages:
                db.session.delete(page)

            # Xóa tất cả các Facebook Ad Account liên kết với tài khoản
            for ad_account in account.facebook_ad_accounts:
                db.session.delete(ad_account)

            db.session.delete(account)  # Xóa tài khoản Facebook
            db.session.commit()  # Cam kết thay đổi vào cơ sở dữ liệu
            flash(
                "Facebook account, related pages, and ad accounts deleted successfully!",
                "success",
            )
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

    user_id = session.get("user_id")  # Lấy user_id từ session
    if not user_id:
        flash("Bạn cần đăng nhập để sử dụng chức năng này", "danger")
        return redirect(url_for("auth.login"))

    if not access_token:
        flash("Access token không được cung cấp.", "danger")
        error_message = "Access token không được cung cấp."
        return render_template("error.html", error_message=error_message)

    try:
        # Gọi hàm get_account để lấy danh sách các trang
        pages = get_account(access_token, id, user_id)
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


@facebook_bp.route("/account_fb/get_account_ads", methods=["POST"])
def get_account_ads():
    access_token = request.form.get("access_token")

    user_id = session.get("user_id")  # Lấy user_id từ session
    if not user_id:
        flash("Bạn cần đăng nhập để sử dụng chức năng này", "danger")
        return redirect(url_for("auth.login"))

    get_ad_accounts(access_token, user_id)

    return redirect(url_for("facebook.account_fb"))


@facebook_bp.route("/ad_accounts", methods=["GET"])
def list_ad_accounts():
    """
    Lấy danh sách tất cả tài khoản quảng cáo của user và hiển thị.
    """
    user_id = session.get("user_id")  # Lấy user_id từ session
    if not user_id:
        flash("Bạn cần đăng nhập để sử dụng chức năng này", "danger")
        return redirect(url_for("auth.login"))
    
    # Lấy tất cả tài khoản quảng cáo theo user_id
    ad_accounts = FacebookAdAccount.query.filter_by(user_id=user_id).all()

    return render_template("ad_accounts.html", ad_accounts=ad_accounts)
