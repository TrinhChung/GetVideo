# models/category.py
from database_init import db

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(
        db.String(100), unique=True, nullable=False
    )  # Tên thể loại (Hướng dẫn, Giới thiệu, ...)

    videos = db.relationship(
        "Video",
        secondary="video_category",
        backref=db.backref("categories", lazy="dynamic"),
    )

    def __repr__(self):
        return f"<Category {self.name}>"
