# routes/pages.py
from flask import Blueprint, render_template
from models.page import Page  # Import model Page đã tạo

# Tạo blueprint cho pages
pages_bp = Blueprint("pages", __name__)


# Route để hiển thị danh sách các pages
@pages_bp.route("/pages")
def show_pages():
    # Sử dụng SQLAlchemy để lấy tất cả các pages
    pages = Page.query.all()  # Lấy tất cả các trang từ bảng 'pages'
    print(pages)
    # Trả về trang HTML với danh sách pages
    return render_template("pages.html", pages=pages)
