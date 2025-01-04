# models/platform.py
from database_init import db

class Platform(db.Model):
    __tablename__ = "platforms"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(
        db.String(100), unique=True, nullable=False
    )  # Tên nền tảng (Facebook, YouTube, TikTok)

    videos = db.relationship(
        "Video",
        secondary="video_platform",
        backref=db.backref("platforms", lazy="dynamic"),
    )

    def __repr__(self):
        return f"<Platform {self.name}>"
