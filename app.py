from flask import Flask, session, redirect, url_for, flash, request, g
from flask_migrate import Migrate
from database_init import db
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from werkzeug.middleware.proxy_fix import ProxyFix
from log import setup_logging
from util.until import format_datetime
from util.get_env_before_request import get_env_before_request
import os
import logging

load_dotenv()

migrate = Migrate()


def create_app():
    app = Flask(__name__, static_url_path="/static")

    # ===== Logging =====
    setup_logging()

    # ===== SECRET_KEY =====
    secret = os.getenv("SECRET_KEY") or "dev-secret-change-me"
    if secret == "dev-secret-change-me":
        logging.warning(
            "SECRET_KEY is not set in environment. Using a DEV fallback. "
            "Set SECRET_KEY in your .env for persistent sessions."
        )
    app.config["SECRET_KEY"] = secret

    # ===== ENV flags =====
    is_prod = os.getenv("FLASK_ENV") == "production"

    # ===== Cookie/Session =====
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=60)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = is_prod
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["PREFERRED_URL_SCHEME"] = "https" if is_prod else "http"

    # ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # ===== CSRF =====
    CSRFProtect(app)

    # ===== DB =====
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql://{os.getenv('USER_DB')}:{os.getenv('PASSWORD_DB')}"
        f"@{os.getenv('ADDRESS_DB')}/{os.getenv('NAME_DB')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ===== Jinja filter & caching =====
    app.jinja_env.filters["datetimeformat"] = format_datetime
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = timedelta(minutes=30)

    # ===== Import models để SQLAlchemy nhận biết =====
    import models.facebook_account
    import models.page
    import models.playlist
    import models.video_split
    import models.stack_post
    import models.video
    import models.facebook_ad_account
    import models.app_env

    # ===== Before request =====
    @app.before_request
    def before_request_load_env():
        get_env_before_request()

    # ===== Context globals =====
    @app.context_processor
    def inject_common_env():
        env = getattr(g, "client_env", {}) or {}
        return dict(
            app_name=env.get("APP_NAME", "DUCK_MANAGER"),
            contact_email=env.get("EMAIL", "support@example.com"),
            address=env.get(
                "ADDRESS", "147 Thái Phiên, Phường 9, Quận 11, TP.HCM, Việt Nam"
            ),
            dns_web=env.get("DNS_WEB", "smartrent.id.vn"),
            tax_number=env.get("TAX_NUMBER", "0318728792"),
            phone_number=env.get("PHONE_NUMBER", "07084773484"),
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
    from routes.api_calls import api_calls_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(facebook_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(stack_post_bp)
    app.register_blueprint(ads_manager_bp)
    app.register_blueprint(api_calls_bp)

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
        if request.endpoint is None:
            return
        if "facebook_user_id" not in session and request.endpoint not in allowed_routes:
            flash("You need to log in to access this page.", "danger")
            return redirect(url_for("auth.login"))

    # ===== Template filter =====
    @app.template_filter("format_currency")
    def format_currency(value, currency="USD"):
        if isinstance(value, (int, float)):
            return f"{value:,.2f} {currency}"
        return value

    return app


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        from sqlalchemy import inspect

        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        required_tables = ["user", "product"]
        missing_tables = [t for t in required_tables if t not in existing_tables]
        if missing_tables:
            print(f"Creating missing tables: {missing_tables}")
            db.create_all()
        else:
            print("All required tables already exist. Skipping db.create_all().")

    app.run(host="127.0.0.1", port=5000, debug=True)
