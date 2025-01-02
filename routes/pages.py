from flask import Blueprint, render_template
from database_init import mysql

# Tạo blueprint cho pages
pages_bp = Blueprint("pages", __name__)


# Route để hiển thị danh sách các pages
@pages_bp.route("/pages")
def show_pages():
    # Kết nối đến MySQL và lấy dữ liệu từ bảng pages
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pages")
    pages = cursor.fetchall()  # Lấy tất cả các trang

    # Đóng kết nối
    cursor.close()

    # Trả về trang HTML với danh sách pages
    return render_template("pages.html", pages=pages)
