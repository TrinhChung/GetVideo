# Form.account_fb.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


class AddFacebookAccountForm(FlaskForm):
    facebook_user_id = StringField("Facebook User ID", validators=[DataRequired()])
    access_token = TextAreaField("Access Token", validators=[DataRequired()])
