from database_init import db

class FacebookCampaign(db.Model):
    __tablename__ = "facebook_campaign"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    facebook_campaign_id = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    objective = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_time = db.Column(db.DateTime, nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)  # Thêm trường start_time
    end_time = db.Column(db.DateTime, nullable=True)  # Thêm trường end_time

    # Quan hệ với bảng FacebookAccount
    facebook_account_id = db.Column(
        db.Integer, db.ForeignKey("facebook_account.id"), nullable=False
    )
    facebook_account = db.relationship(
        "FacebookAccount", back_populates="facebook_campaigns"
    )

    # Quan hệ với bảng FacebookAdAccount
    facebook_ad_account_id = db.Column(
        db.Integer, db.ForeignKey("facebook_ad_accounts.id"), nullable=False
    )
    facebook_ad_account = db.relationship(
        "FacebookAdAccount", back_populates="facebook_campaigns"
    )

    # Added column for special ad categories
    special_ad_categories = db.Column(db.String(255), nullable=True)

    def __repr__(self):

        return f"<FacebookCampaign {self.name}>"
