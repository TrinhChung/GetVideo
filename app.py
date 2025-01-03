from flask import Flask
from database_init import db
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

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
    app.run(debug=True)
