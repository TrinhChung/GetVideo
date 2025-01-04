# models/video_split_category.py
from database_init import db


class VideoSplitCategory(db.Model):
    __tablename__ = "video_split_category"

    video_split_id = db.Column(
        db.Integer, db.ForeignKey("video_split.id"), primary_key=True
    )
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), primary_key=True)
