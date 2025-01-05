from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired


class VideoSplitScheduleForm(FlaskForm):
    page_id = SelectField("Chọn Trang", validators=[DataRequired()], coerce=int)
    selected_splits = SelectMultipleField(
        "Chọn Video Splits", validators=[DataRequired()], coerce=int
    )
    submit = SubmitField("Thêm vào lịch phát hành")
