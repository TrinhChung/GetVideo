# models/category_playlist.py
from database_init import db


class CategoryPlaylist(db.Model):
    __tablename__ = "category_playlist"

    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlist.id"), primary_key=True)
