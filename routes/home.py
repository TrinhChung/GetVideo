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
