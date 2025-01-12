# models/facebook_campaign.py
from database_init import db

class FacebookCampaign(db.Model):
    __tablename__ = "facebook_campaign"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    facebook_campaign_id = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    objective = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Quan hệ với bảng FacebookAccount
    facebook_account_id = db.Column(
        db.Integer, db.ForeignKey("facebook_account.id"), nullable=False
    )
    facebook_account = db.relationship(
        "FacebookAccount", back_populates="facebook_campaigns"
    )

    def __repr__(self):
        return f"<FacebookCampaign {self.name}>"
