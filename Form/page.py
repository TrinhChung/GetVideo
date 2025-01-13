from flask_wtf import FlaskForm
from wtforms import SubmitField

class PageForm(FlaskForm):
    submit = SubmitField("Debug Token")
