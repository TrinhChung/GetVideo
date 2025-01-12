# models/playlist.py
from database_init import db

class Playlist(db.Model):
    __tablename__ = "playlist"

    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(255))

    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # Khóa ngoại liên kết với bảng User

    # Quan hệ với bảng User
    user = db.relationship("User", backref=db.backref("playlists", lazy=True))
