# models/category_video.py
from database_init import db

class VideoCategory(db.Model):
    __tablename__ = "video_category"

    video_id = db.Column(db.Integer, db.ForeignKey("videos.id"), primary_key=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), primary_key=True
    )

    video = db.relationship(
        "Video", backref=db.backref("video_categories", lazy="dynamic")
    )
    category = db.relationship(
        "Category", backref=db.backref("video_categories", lazy="dynamic")
    )
