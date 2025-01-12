# models.page.py
from database_init import db


class Page(db.Model):
    __tablename__ = "page"

    page_id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255))
    category = db.Column(db.String(255))
    access_token = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    facebook_account_id = db.Column(db.Integer, db.ForeignKey("facebook_account.id"))

    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # Khóa ngoại liên kết với bảng User

    # Quan hệ với bảng User
    user = db.relationship("User", backref=db.backref("pages", lazy=True))

    # Quan hệ với bảng FacebookAccount
    facebook_account = db.relationship("FacebookAccount", back_populates="pages")

    def __repr__(self):
        return f"<Page {self.name} (ID: {self.page_id})>"
