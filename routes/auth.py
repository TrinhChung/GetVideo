# routes.auth.py
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from models.user import User
from database_init import db
from Form.login import LoginForm
from Form.register import RegisterForm
import os
from dotenv import load_dotenv

auth_bp = Blueprint("auth", __name__)

load_dotenv()  # Đọc file .env

# Route to show the login page
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    facebook_app_id = os.getenv("APP_ID")
    # if form.validate_on_submit():  # Check if the form is valid on submit
    #     username = form.username.data
    #     password = form.password.data
    #     remember_me = form.remember_me.data

    #     # Try to find the user by username
    #     user = User.query.filter_by(username=username).first()

    #     if user and user.check_password(password):
    #         # Check if the user is active
    #         if not user.active:
    #             flash(
    #                 "Tài khoản của bạn chưa được kích hoạt. Vui lòng cầu xin quản trị viên.",
    #                 "danger",
    #             )
    #             return redirect(url_for("auth.login"))

    #         session["user_id"] = user.id  # Store user ID in session
    #         # Handle "Remember me" functionality
    #         if remember_me:
    #             session.permanent = (
    #                 True  # This will set the session to use a permanent lifetime
    #             )
    #         else:
    #             session.permanent = False

    #         flash("Đăng nhập thành công", "success")
    #         return redirect(url_for("home.home"))  # Redirect to home page
    #     else:
    #         flash("Tên đăng nhập hoặc mật khẩu không đúng", "danger")

    return render_template("login_fb.html", form=form, facebook_app_id=facebook_app_id)


# Route to show the registration page
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():  # Check if the form is valid on submit
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash("Tên đăng nhập đã tồn tại", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Email đã được sử dụng", "danger")
        else:
            # Create a new user instance
            new_user = User(username=username, email=email)
            new_user.set_password(password)  # Hash and set password

            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Đăng ký thành công", "success")
                flash("Vui lòng chờ quản trị viên kích hoạt", "danger")
                return redirect(url_for("auth.login"))  # Redirect to login page
            except Exception as e:
                db.session.rollback()  # Rollback in case of an error
                flash(f"Đã xảy ra lỗi khi đăng ký: {e}", "danger")

    return render_template("register.html", form=form)


# Route to handle logout
@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)  # Remove user from session
    flash("Signed out", "info")
    return redirect(url_for("auth.login"))
