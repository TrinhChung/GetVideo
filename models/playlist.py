# models/playlist.py
from database_init import db

class Playlist(db.Model):
    __tablename__ = "playlist"

    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(255))
    facebook_account_id = db.Column(db.Integer, db.ForeignKey("facebook_account.id"))
    facebook_account = db.relationship(
        "FacebookAccount", backref=db.backref("playlists", lazy=True)
    )
