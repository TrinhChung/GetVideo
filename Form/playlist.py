from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class PlaylistForm(FlaskForm):
    playlist_url = StringField("Playlist URL", validators=[DataRequired()])
    submit = SubmitField("Add Playlist")


class GetVideoFromPlaylistForm(FlaskForm):
    playlist_id = StringField("Playlist ID", validators=[DataRequired()])
    submit = SubmitField("Get Video")


class GetAllVideosForm(FlaskForm):
    submit = SubmitField("Get All Videos")
