from flask import Flask
from flask_migrate import Migrate
from database_init import db
from dotenv import load_dotenv
import os

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
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql://root:{os.getenv('PASSWORD_DB')}@localhost/video"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from routes.home import home_bp
    from routes.batch import batch_bp
    from routes.download import download_bp
    from routes.facebook import facebook_bp
    from routes.pages import pages_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(batch_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(facebook_bp)
    app.register_blueprint(pages_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    # Flask-Migrate sẽ tự động xử lý migrations
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
