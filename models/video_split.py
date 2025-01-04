from database_init import db


class VideoSplit(db.Model):
    __tablename__ = "video_split"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    duration = db.Column(db.Integer)
    type = db.Column(
        db.String(50), nullable=False
    )  # type = 'facebook', 'youtube', or 'tiktok'

    # Mối quan hệ với Category thông qua bảng phụ 'video_split_category'
    categories = db.relationship(
        "Category",
        secondary="video_split_category",  # Cập nhật tên bảng phụ
        back_populates="videos_split",  # Liên kết với back_populates trong Category
    )

    def __repr__(self):
        return f"<VideoSplit {self.title} (ID: {self.id})>"
