# models/facebook_account.py
from database_init import db


class FacebookAccount(db.Model):
    __tablename__ = "facebook_account"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    facebook_user_id = db.Column(
        db.String(255), unique=True, nullable=True
    )  # Change email to facebook_user_id
    access_token = db.Column(db.Text, nullable=False)

    # Quan hệ với bảng Page
    pages = db.relationship("Page", back_populates="facebook_account", lazy=True)

    # Quan hệ với FacebookAdAccount sử dụng back_populates
    facebook_ad_accounts = db.relationship(
        "FacebookAdAccount", back_populates="facebook_account", lazy=True
    )

    # Quan hệ với FacebookCampaign
    facebook_campaigns = db.relationship(
        "FacebookCampaign", back_populates="facebook_account", lazy=True
    )

    def __repr__(self):
        return f"<FacebookAccount {self.facebook_user_id}>"
