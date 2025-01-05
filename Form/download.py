from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL


class VideoDownloadForm(FlaskForm):
    video_url = StringField("Video URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Download Video")
