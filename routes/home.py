from flask import render_template, Blueprint

home_bp = Blueprint("home", __name__)


@home_bp.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")
