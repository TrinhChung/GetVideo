# models/facebook_ad_account.py
from database_init import db


class FacebookAdAccount(db.Model):
    __tablename__ = "facebook_ad_accounts"

    id = db.Column(db.Integer, primary_key=True)

    # ID tài khoản quảng cáo Facebook (act_<account_id>)
    facebook_ad_account_id = db.Column(db.String(255), unique=False, nullable=False)

    # Tên tài khoản quảng cáo
    name = db.Column(db.String(255), nullable=False)

    # Trạng thái hoạt động của tài khoản
    account_status = db.Column(db.Integer, nullable=False)

    # Đơn vị tiền tệ (VND, USD, ...)
    currency = db.Column(db.String(10), nullable=False)

    # Số dư tài khoản quảng cáo (có thể âm nếu nợ)
    balance = db.Column(db.Float, nullable=True)

    # Tổng số tiền đã chi tiêu
    amount_spent = db.Column(db.Float, nullable=True)

    # Giới hạn chi tiêu tối đa
    spend_cap = db.Column(db.Float, nullable=True)

    # Múi giờ tài khoản
    timezone_name = db.Column(db.String(100), nullable=True)

    # Độ lệch múi giờ UTC
    timezone_offset_hours_utc = db.Column(db.Float, nullable=True)

    # ID doanh nghiệp liên kết (nếu có)
    business_id = db.Column(db.String(255), nullable=True)

    # Tên doanh nghiệp liên kết
    business_name = db.Column(db.String(255), nullable=True)

    # Ngày tạo tài khoản
    created_time = db.Column(db.DateTime, nullable=True)
    
    # Khóa ngoại liên kết với FacebookAccount
    facebook_account_id = db.Column(
        db.Integer, db.ForeignKey("facebook_account.id", ondelete="CASCADE")
    )

    # Thiết lập mối quan hệ với FacebookAccount sử dụng back_populates
    facebook_account = db.relationship(
        "FacebookAccount", back_populates="facebook_ad_accounts"
    )

    # Mối quan hệ với bảng FacebookCampaign
    facebook_campaigns = db.relationship(
        "FacebookCampaign", back_populates="facebook_ad_account"
    )

    def __repr__(self):
        return f"<FacebookAdAccount {self.name}>"
