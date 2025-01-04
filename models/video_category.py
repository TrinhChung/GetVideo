# models/video_category.py
from database_init import db


class VideoCategory(db.Model):
    __tablename__ = "video_category"

    video_id = db.Column(db.Integer, db.ForeignKey("video.id"), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), primary_key=True)
