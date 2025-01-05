from flask_wtf import FlaskForm
from wtforms import SubmitField


class VideoDownloadForm(FlaskForm):
    submit = SubmitField("Download Video")


class VideoSplitForm(FlaskForm):
    submit = SubmitField("Split Video")
