# models/playlist.py
from database_init import db

class Playlist(db.Model):
    __tablename__ = "playlist"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_id = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))

    videos = db.relationship("Video", back_populates="playlist", lazy=True)

    facebook_account_id = db.Column(db.Integer, db.ForeignKey("facebook_account.id"))
    facebook_account = db.relationship(
        "FacebookAccount", backref=db.backref("playlists", lazy=True)
    )
