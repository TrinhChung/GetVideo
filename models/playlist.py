# models/playlist.py
from database_init import db

class Playlist(db.Model):
    __tablename__ = "playlist"

    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(255))
