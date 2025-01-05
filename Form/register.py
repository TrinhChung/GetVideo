from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length, Email, EqualTo


class RegisterForm(FlaskForm):
    username = StringField(
        "Tên đăng nhập",
        validators=[
            InputRequired(),
            Length(
                min=4, max=20, message="Tên đăng nhập phải có độ dài từ 4 đến 20 ký tự."
            ),
        ],
    )
    email = EmailField(
        "Email",
        validators=[InputRequired(), Email(message="Vui lòng nhập email hợp lệ.")],
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[
            InputRequired(),
            Length(min=6, message="Mật khẩu phải có ít nhất 6 ký tự."),
        ],
    )
    confirm_password = PasswordField(
        "Xác nhận mật khẩu",
        validators=[
            InputRequired(),
            EqualTo("password", message="Mật khẩu không khớp."),
        ],
    )
