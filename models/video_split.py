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

    # Cột type_duration với kiểu dữ liệu Integer
    type_duration = db.Column(db.Integer)  # Cột type_duration kiểu int

    # Khóa ngoại video_id tham chiếu tới bảng Video
    video_id = db.Column(db.Integer, db.ForeignKey("video.id"), nullable=True)
    video = db.relationship("Video", backref=db.backref("splits", lazy=True))

    facebook_account_id = db.Column(db.Integer, db.ForeignKey("facebook_account.id"))
    facebook_account = db.relationship(
        "FacebookAccount", backref=db.backref("video_splits", lazy=True)
    )

    # Mối quan hệ với Category thông qua bảng phụ 'video_split_category'
    categories = db.relationship(
        "Category",
        secondary="video_split_category",  # Cập nhật tên bảng phụ
        back_populates="videos_split",  # Liên kết với back_populates trong Category
    )

    def __repr__(self):
        return f"<VideoSplit {self.title} (ID: {self.id})>"
