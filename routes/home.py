from flask import Response,render_template, send_from_directory, Blueprint,current_app
import os

home_bp = Blueprint("home", __name__)

@home_bp.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@home_bp.route("/polices", methods=["GET", "POST"])
def polices():
    return render_template("polices.html")

@home_bp.route("/terms", methods=["GET", "POST"])
def terms():
    return render_template("term.html")


@home_bp.route("/permissions", methods=["GET", "POST"])
def permissions():
    return render_template("permission.html")


@home_bp.route("/favicon.ico")
def favicon():
    return send_from_directory(
        "static", "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )

@home_bp.route('/logs/app.log')
def view_log():
    log_dir = os.path.join(current_app.root_path, 'static')
    log_file = 'app.log'

    # Đọc nội dung file log
    log_path = os.path.join(log_dir, log_file)

    try:
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Trả về nội dung file log dưới dạng văn bản
        return Response(log_content, content_type='text/plain')
    
    except FileNotFoundError:
        return "Log file not found.", 404

@home_bp.route('/download-pdf', methods=["GET"])
def download_pdf():
    # Đường dẫn tới tệp PDF
    file_path = os.path.join(current_app.root_path, 'static', 'TrinhVanChung_BackendEngineer.pdf')

    # Kiểm tra nếu file tồn tại
    if os.path.exists(file_path):
        # Chỉ cần truyền thư mục nơi chứa tệp, không cần phải sử dụng os.path.dirname nữa
        return send_from_directory('static', 'TrinhVanChung_BackendEngineer.pdf', as_attachment=True)
    else:
        return "File not found.", 404