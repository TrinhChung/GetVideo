# models/video.py
from database_init import db


class Video(db.Model):
    __tablename__ = "video"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video_id = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    crawled = db.Column(db.Boolean, default=False)
    playlist_id = db.Column(db.String(255), db.ForeignKey("playlist.id"))
    path = db.Column(db.String(255))
    duration = db.Column(db.Integer)
    splited = db.Column(
        db.Boolean, default=False
    )  # Thêm trường splited với mặc định là False
    playlist = db.relationship("Playlist", backref=db.backref("video", lazy=True))

    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # Khóa ngoại liên kết với bảng User

    # Quan hệ với bảng User
    user = db.relationship("User", backref=db.backref("videos", lazy=True))
