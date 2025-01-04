from database_init import db


class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(
        db.String(100), unique=True, nullable=False
    )  # Tên thể loại (Hướng dẫn, Giới thiệu, ...)

    # Mối quan hệ nhiều-nhiều với Playlist thông qua bảng phụ 'category_playlist'
    playlists = db.relationship(
        "Playlist",
        secondary="category_playlist",  # Liên kết với bảng phụ 'category_playlist'
        backref=db.backref("category", lazy="dynamic"),
    )

    # Mối quan hệ nhiều-nhiều với Video thông qua bảng phụ 'video_category'
    videos = db.relationship(
        "Video",
        secondary="video_category",  # Liên kết với bảng phụ 'video_category'
        backref=db.backref("category", lazy="dynamic"),
    )

    # Mối quan hệ nhiều-nhiều với VideoSplit thông qua bảng phụ 'video_split_category'
    videos_split = db.relationship(
        "VideoSplit",
        secondary="video_split_category",  # Cập nhật tên bảng phụ
        back_populates="categories",  # Liên kết với back_populates trong VideoSplit
    )

    def __repr__(self):
        return f"<Category {self.name}>"
