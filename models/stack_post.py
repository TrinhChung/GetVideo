# models.stack_post.py
from database_init import db
from datetime import datetime

class StackPost(db.Model):
    __tablename__ = "stack_post"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page_id = db.Column(
        db.String(255), db.ForeignKey("page.page_id"), nullable=False
    )  # Liên kết với Page qua page_id
    time = db.Column(db.DateTime, default=datetime.utcnow)  # Thời gian đăng bài
    video_split_id = db.Column(
        db.Integer, db.ForeignKey("video_split.id"), nullable=False
    )  # Liên kết với video_splits
    posted_video_id = db.Column(db.String(64), nullable=True)
    title = db.Column(db.String(255), nullable=False)  # Tiêu đề bài đăng
    status = db.Column(
        db.String(50), nullable=False
    )  # Trạng thái của bài đăng, ví dụ: "pending", "completed"

    # Mối quan hệ giữa StackPost và VideoSplit
    video_split = db.relationship(
        "VideoSplit", backref=db.backref("stack_post", lazy=True)
    )

    facebook_account_id = db.Column(db.Integer, db.ForeignKey("facebook_account.id"))
    
    facebook_account = db.relationship(
        "FacebookAccount", backref=db.backref("stack_posts", lazy=True)
    )

    # Mối quan hệ giữa StackPost và Page
    page = db.relationship("Page", backref="stack_posts", lazy=True)
