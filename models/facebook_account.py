from database_init import db


class FacebookAccount(db.Model):
    __tablename__ = "facebook_account"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=True)
    access_token = db.Column(db.Text, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # Khóa ngoại liên kết với bảng User

    # Quan hệ với bảng User
    user = db.relationship("User", backref=db.backref("facebook_accounts", lazy=True))

    # Quan hệ với bảng Page
    pages = db.relationship("Page", back_populates="facebook_account", lazy=True)

    def __repr__(self):
        return f"<FacebookAccount {self.email}>"
