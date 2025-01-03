from flask import Flask
from database_init import mysql
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__, static_url_path="/static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    app.config["MYSQL_HOST"] = "localhost"
    app.config["MYSQL_USER"] = "root"
    app.config["MYSQL_PASSWORD"] = os.getenv("PASSWORD_DB")
    app.config["MYSQL_DB"] = "video"

    mysql.init_app(app)

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
    app.run(debug=True)
