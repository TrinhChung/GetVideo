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

    # Quan hệ với bảng FacebookAccount
    facebook_account = db.relationship("FacebookAccount", back_populates="pages")

    def __repr__(self):
        return f"<Page {self.name} (ID: {self.page_id})>"
