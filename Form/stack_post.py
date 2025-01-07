from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField

class StackPostForm(FlaskForm):
    selected_posts = SelectMultipleField(
        "Chọn Video Posts", coerce=int
    )
    submit = SubmitField("Đăng Video")
