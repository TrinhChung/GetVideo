from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User  # Make sure you have a User model in models/user.py
from database_init import db

auth_bp = Blueprint("auth", __name__)


# Route to show the login page
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Try to find the user by username
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id  # Store user ID in session
            flash("Đăng nhập thành công", "success")
            return redirect(url_for("batch.batch_youtube_playlist"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng", "danger")

    return render_template("login.html")


# Route to show the registration page
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_hash = generate_password_hash(password)  # Encrypt the password

        # Create a new user instance
        new_user = User(username=username, password=password_hash)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Đăng ký thành công", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            flash(f"Đã xảy ra lỗi khi đăng ký: {e}", "danger")

    return render_template("register.html")


# Route to handle logout
@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)  # Remove user from session
    flash("Đã đăng xuất", "info")
    return redirect(url_for("auth.login"))
