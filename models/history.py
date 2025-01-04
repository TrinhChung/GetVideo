# models/history.py
from database_init import db
from datetime import datetime


class History(db.Model):
    __tablename__ = "history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.String(310), nullable=False)  # Nội dung thông báo
    job_name = db.Column(db.String(255), nullable=False)  # Tên công việc
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow
    )  # Thời gian tạo, mặc định là thời gian hiện tại

    def __repr__(self):
        return f"<History {self.job_name} at {self.created_at}>"
