from database_init import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # Mã hóa mật khẩu
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow
    )  # Thời gian tạo tài khoản

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        """Mã hóa mật khẩu trước khi lưu trữ."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Kiểm tra mật khẩu người dùng nhập vào với mật khẩu đã mã hóa."""
        return check_password_hash(self.password_hash, password)
