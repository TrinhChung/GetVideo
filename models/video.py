# models/video.py
from database_init import db


class Video(db.Model):
    __tablename__ = "video"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video_id = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    crawled = db.Column(db.Boolean, default=False)
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlist.id"))
    path = db.Column(db.String(255))
    duration = db.Column(db.Integer)
    splited = db.Column(
        db.Boolean, default=False
    )  # Thêm trường splited với mặc định là False
    playlist = db.relationship("Playlist", backref=db.backref("video", lazy=True))

    facebook_account_id = db.Column(db.Integer, db.ForeignKey("facebook_account.id"))
    
    facebook_account = db.relationship(
        "FacebookAccount", backref=db.backref("videos", lazy=True)
    )
