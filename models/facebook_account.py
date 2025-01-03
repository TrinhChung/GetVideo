# models/facebook_account.py
from database_init import db

class FacebookAccount(db.Model):
    __tablename__ = "facebook_accounts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=True)
    access_token = db.Column(db.Text, nullable=False)
    pages = db.relationship("Page", backref="facebook_account", lazy=True)
