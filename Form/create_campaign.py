from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DateTimeField,SelectMultipleField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import CheckboxInput

class FacebookCampaignForm(FlaskForm):
    campaign_name = StringField(
        "Campaign Name", validators=[DataRequired(), Length(min=3, max=100)]
    )
    ad_account_id = SelectField(
        "Ad Account",
        choices=[],  # Choices will be set in the view
        validators=[DataRequired()],
    )
    objective = SelectField(
        "Objective",
        choices=[
            ("OUTCOME_AWARENESS", "Outcome Awareness"),
            ("OUTCOME_ENGAGEMENT", "Outcome Engagement"),
            ("OUTCOME_LEADS", "Outcome Leads"),
            ("OUTCOME_SALES", "Outcome Sales"),
            ("OUTCOME_TRAFFIC", "Outcome Traffic"),
            ("OUTCOME_APP_PROMOTION", "Outcome App Promotion"),
            ("CONVERSIONS", "Conversions"),
        ],
        validators=[DataRequired()],
    )
    status = SelectField(
        "Status",
        choices=[("PAUSED", "Paused"), ("ACTIVE", "Active")],
        validators=[DataRequired()],
    )
    special_ad_categories = SelectField(
        "Special Ad Categories",
        choices=[
            ("NONE", "None"),
            ("HOUSING", "Housing"),
            ("EMPLOYMENT", "Employment"),
            ("CREDIT", "Credit"),
            ("FINANCIAL_PRODUCTS_SERVICES", "Financial Products / Services"),
            ("ISSUES_ELECTIONS_POLITICS", "Issues, Elections, or Politics"),
        ],
        validators=[DataRequired()],
    )
    start_time = DateTimeField("Start Time", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    end_time = DateTimeField("End Time", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    submit = SubmitField("Create Campaign")


class CampaignForm(FlaskForm):
    selected_campaigns = SelectMultipleField(
        "Selected Campaigns", coerce=int, widget=CheckboxInput()
    )
