from flask import session, redirect, url_for, flash


def login_required(func):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:  # Kiểm tra session
            flash("Bạn cần đăng nhập để truy cập trang này.", "danger")
            return redirect(url_for("auth.login"))  # Chuyển hướng đến trang đăng nhập
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__  # Giữ nguyên tên hàm để Flask không báo lỗi
    return wrapper
