from flask_wtf import FlaskForm
from wtforms import SubmitField

class StackPostForm(FlaskForm):
    submit = SubmitField("Đăng Video")
