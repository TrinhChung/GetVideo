from flask import Flask, session, redirect, url_for, flash, request
from flask_migrate import Migrate
from database_init import db
from dotenv import load_dotenv
import os
import secrets
from flask_wtf.csrf import CSRFProtect

# Import tất cả các mô hình
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

load_dotenv()

migrate = Migrate()


def create_app():
    app = Flask(__name__, static_url_path="/static")
    app.config["SECRET_KEY"] = secrets.token_hex(16)
    csrf = CSRFProtect(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql://root:{os.getenv('PASSWORD_DB')}@localhost/video"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from routes.home import home_bp
    from routes.playlist import playlist_bp
    from routes.video import video_bp
    from routes.download import download_bp
    from routes.facebook import facebook_bp
    from routes.pages import pages_bp
    from routes.auth import auth_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(playlist_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(facebook_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)

    @app.before_request
    def require_login():
        allowed_routes = ["auth.login", "auth.register", "static"]
        if "user_id" not in session and request.endpoint not in allowed_routes:
            flash("Bạn cần đăng nhập để truy cập trang này.", "danger")
            return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    app = create_app()
    # Flask-Migrate sẽ tự động xử lý migrations
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
