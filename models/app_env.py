from database_init import db
from datetime import datetime


class AppEnv(db.Model):
    __tablename__ = "app_env"

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), unique=True, nullable=False)

    app_id = db.Column(db.String(100))
    app_secret = db.Column(db.String(255))
    secret_key = db.Column(db.String(255))
    flask_env = db.Column(db.String(50))

    password_db = db.Column(db.String(255))
    name_db = db.Column(db.String(100))
    user_db = db.Column(db.String(100))
    address_db = db.Column(db.String(100))

    app_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    address = db.Column(db.String(500))
    phone_number = db.Column(db.String(50))
    dns_web = db.Column(db.String(255))
    company_name = db.Column(db.String(255))
    tax_number = db.Column(db.String(50))
    company_global_name = db.Column(db.String(255), nullable=True)
    company_short_name = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<AppEnv {self.domain} - {self.app_name}>"
