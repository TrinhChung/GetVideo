from flask import Flask, session, redirect, url_for, flash, request
from flask_migrate import Migrate
from database_init import db
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from werkzeug.middleware.proxy_fix import ProxyFix
from log import setup_logging

from util.until import format_datetime

import os
import logging

load_dotenv()

migrate = Migrate()


def create_app():
    app = Flask(__name__, static_url_path="/static")

    # ===== Logging =====
    setup_logging()

    # ===== SECRET_KEY (bắt buộc cho session/CSRF) =====
    secret = os.getenv("SECRET_KEY")
    if not secret:
        # Fallback chỉ nên dùng cho DEV; mỗi lần restart sẽ mất session cũ.
        secret = "dev-secret-change-me"
        logging.warning(
            "SECRET_KEY is not set in environment. Using a DEV fallback. "
            "Set SECRET_KEY in your .env for persistent sessions."
        )
    app.config["SECRET_KEY"] = secret

    # ===== ENV flags =====
    # Đặt FLASK_ENV=production khi deploy (qua Cloudflare/HTTPS)
    is_prod = os.getenv("FLASK_ENV") == "production"

    # ===== Cookie/Session =====
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=60)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = is_prod  # HTTPS ở prod, HTTP khi dev local
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["PREFERRED_URL_SCHEME"] = "https" if is_prod else "http"

    # Nếu app chạy sau reverse proxy (Cloudflare/Nginx), dùng ProxyFix để đọc đúng scheme/IP/host
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # ===== CSRF =====
    csrf = CSRFProtect(app)

    # ===== DB =====
    # Thêm charset utf8mb4 (khuyến nghị) nếu cần: mysql://user:pass@host/db?charset=utf8mb4
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql://{os.getenv('USER_DB')}:{os.getenv('PASSWORD_DB')}"
        f"@{os.getenv('ADDRESS_DB')}/{os.getenv('NAME_DB')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ===== Jinja filter & caching =====
    app.jinja_env.filters["datetimeformat"] = format_datetime
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = timedelta(minutes=30)
    # app.config["TEMPLATES_AUTO_RELOAD"] = not is_prod  # mở nếu muốn auto reload template khi dev

    # ===== Context globals =====
    @app.context_processor
    def inject_common_env():
        return dict(
            app_name=os.getenv("APP_NAME", "DUCK_MANAGER"),
            contact_email=os.getenv("EMAIL", "support@example.com"),
            address=os.getenv(
                "ADDRESS", "147 Thái Phiên, Phường 9,Quận 11, TP.HCM, Việt Nam"
            ),
            dns_web=os.getenv("DNS_WEB", "smartrent.id.vn"),
            tax_number=os.getenv("TAX_NUMBER", "0318728792"),
            phone_number=os.getenv("PHONE_NUMBER", "07084773484"),
        )

    # ===== Init extensions =====
    db.init_app(app)
    migrate.init_app(app, db)

    # ===== Blueprints =====
    from routes.home import home_bp
    from routes.facebook import facebook_bp
    from routes.pages import pages_bp
    from routes.auth import auth_bp
    from routes.stack_post import stack_post_bp
    from routes.ads_manager import ads_manager_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(facebook_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(stack_post_bp)
    app.register_blueprint(ads_manager_bp)

    # ===== Auth guard =====
    @app.before_request
    def require_login():
        allowed_routes = {
            "auth.login",
            "auth.logout",
            "home.polices",
            "home.terms",
            "home.home",
            "static",
        }
        # Một số request có thể không có endpoint (404, favicon, debugger resource...)
        if request.endpoint is None:
            return
        if "facebook_user_id" not in session and request.endpoint not in allowed_routes:
            flash("You need to log in to access this page.", "danger")
            return redirect(url_for("auth.login"))

    # ===== Jinja filter: format_currency =====
    @app.template_filter("format_currency")
    def format_currency(value, currency="USD"):
        if isinstance(value, (int, float)):
            return f"{value:,.2f} {currency}"
        return value

    return app


if __name__ == "__main__":
    app = create_app()
    # Flask-Migrate sẽ tự động xử lý migrations

    with app.app_context():
        from sqlalchemy import inspect

        # Import models để SQLAlchemy biết bảng (nếu bạn dùng db.create_all() khi thiếu)
        from models.category_playlist import CategoryPlaylist
        from models.category import Category
        from models.facebook_account import FacebookAccount
        from models.history import History
        from models.page import Page
        from models.playlist import Playlist
        from models.stack_post import StackPost
        from models.video_category import VideoCategory
        from models.video_split_category import VideoSplitCategory
        from models.video_split import VideoSplit
        from models.video import Video
        from models.facebook_ad_account import FacebookAdAccount

        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        # TODO: thay danh sách này bằng cách tự động duyệt db.Model nếu muốn
        required_tables = ["user", "product"]
        missing_tables = [t for t in required_tables if t not in existing_tables]
        if missing_tables:
            print(f"Creating missing tables: {missing_tables}")
            db.create_all()
        else:
            print("All required tables already exist. Skipping db.create_all().")

    # Gợi ý: bind rõ host/port để khớp Cloudflare Tunnel (127.0.0.1:5000)
    app.run(host="127.0.0.1", port=5000, debug=True)
