# routes.auth.py
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
from models.facebook_account import FacebookAccount
from database_init import db
from Form.login import LoginForm
import os
from dotenv import load_dotenv
from util.post_fb import get_account, get_ad_accounts,sync_facebook_campaigns, delete_facebook_account

auth_bp = Blueprint("auth", __name__)

load_dotenv()


# Route to show the login page
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form=LoginForm()
    facebook_app_id = os.getenv("APP_ID")

    # Handle Facebook login response
    if request.method == "POST":
        facebook_user_id = request.json.get("facebook_user_id")
        access_token = request.json.get("access_token")

        if facebook_user_id and access_token:
            # Kiểm tra nếu tài khoản đã tồn tại
            account = FacebookAccount.query.filter_by(
                facebook_user_id=facebook_user_id
            ).first()
            if not account:
                # Tạo tài khoản mới nếu chưa tồn tại
                account = FacebookAccount(
                    facebook_user_id=facebook_user_id, access_token=access_token
                )
                db.session.add(account)
                db.session.commit()
            else:
                # Nếu tài khoản đã tồn tại, cập nhật access_token
                account.access_token = access_token
                db.session.commit()

            # Lưu vào session
            print(facebook_user_id)
            session["facebook_user_id"] = account.id

            # Lấy ra danh sách page
            get_account(access_token, account.id)

            # Lấy ra danh sách tài khoản quảng cáo
            get_ad_accounts(access_token, account.id)

            # lấy ra danh sách chiến dịch
            sync_facebook_campaigns(account.id)

            flash("Log in successfully!!", "success")
            print("User logged in successfully")
            return jsonify(
                {
                    "success": True,
                    "message": "Facebook account added successfully!",
                }
            )

        flash("Login failed!", "danger")
        return jsonify({"success": False, "message": f"Login failed"}), 500

    return render_template("login_fb.html", form=form, facebook_app_id=facebook_app_id)


# Route to handle logout
@auth_bp.route("/logout")
def logout():
    facebook_account_id = session.get("facebook_user_id")
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))
    
    delete_facebook_account(facebook_account_id)
    session.pop("facebook_user_id", None)  # Remove Facebook user from session
    flash("You are signed out", "info")
    return redirect(url_for("auth.login"))
