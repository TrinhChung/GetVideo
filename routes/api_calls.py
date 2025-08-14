from flask import Blueprint, render_template, session, flash, redirect, url_for
from models.facebook_account import FacebookAccount
from models.facebook_ad_account import FacebookAdAccount
from models.page import Page
import requests
import logging

api_calls_bp = Blueprint("api_calls", __name__)


@api_calls_bp.route("/api_calls", methods=["GET"])
def api_calls_home():
    """Render page with buttons to trigger various Facebook API calls."""
    if "facebook_user_id" not in session:
        flash("You need to log in to access this page.", "danger")
        return redirect(url_for("auth.login"))

    facebook_account_id = session["facebook_user_id"]
    pages = Page.query.filter_by(facebook_account_id=facebook_account_id).all()
    ad_accounts = FacebookAdAccount.query.filter_by(
        facebook_account_id=facebook_account_id
    ).all()
    return render_template("api_calls.html", pages=pages, ad_accounts=ad_accounts)


def _check_rate_limit(response):
    if response.status_code == 429:
        flash("Facebook API rate limit reached. Please pause and try again later.", "danger")
        return True
    return False


def _get_access_token():
    facebook_account_id = session.get("facebook_user_id")
    account = FacebookAccount.query.filter_by(id=facebook_account_id).first()
    if not account:
        flash("Facebook account not found.", "danger")
        return None
    return account.access_token


@api_calls_bp.route("/api_calls/trigger/<string:action>", methods=["POST"])
def trigger_api_call(action: str):
    """Trigger specific Facebook API call and report rate limit status."""
    if "facebook_user_id" not in session:
        flash("You need to log in to access this page.", "danger")
        return redirect(url_for("auth.login"))

    token = _get_access_token()
    if not token:
        return redirect(url_for("api_calls.api_calls_home"))

    try:
        response = None
        fb_api = "https://graph.facebook.com/v21.0"
        if action == "account_fb":
            response = requests.get(f"{fb_api}/me", params={"access_token": token})
        elif action == "get_pages":
            response = requests.get(
                f"{fb_api}/me/accounts", params={"access_token": token}
            )
        elif action == "list_posts":
            pages = Page.query.filter_by(
                facebook_account_id=session["facebook_user_id"]
            ).all()
            for page in pages:
                response = requests.get(
                    f"{fb_api}/{page.page_id}/posts",
                    params={"access_token": page.access_token},
                )
                if _check_rate_limit(response):
                    return redirect(url_for("api_calls.api_calls_home"))
        elif action == "list_ad_accounts":
            response = requests.get(
                f"{fb_api}/me/adaccounts", params={"access_token": token}
            )
        elif action in {"fetch_facebook_campaigns", "list_fb_campaigns"}:
            ad = FacebookAdAccount.query.filter_by(
                facebook_account_id=session["facebook_user_id"]
            ).first()
            if ad:
                response = requests.get(
                    f"{fb_api}/{ad.facebook_ad_account_id}/campaigns",
                    params={"access_token": token},
                )
            else:
                flash("No ad account found for campaigns.", "warning")
        elif action in {"view_ads", "get_account_ads"}:
            ad = FacebookAdAccount.query.filter_by(
                facebook_account_id=session["facebook_user_id"]
            ).first()
            if ad:
                response = requests.get(
                    f"{fb_api}/{ad.facebook_ad_account_id}/ads",
                    params={"access_token": token},
                )
            else:
                flash("No ad account found for ads.", "warning")
        else:
            flash("Unknown action.", "danger")
            return redirect(url_for("api_calls.api_calls_home"))

        if response and _check_rate_limit(response):
            return redirect(url_for("api_calls.api_calls_home"))
        if response is not None and response.ok:
            flash(f"Called {action} API successfully.", "success")
        elif response is not None:
            flash(f"API call failed: {response.text}", "danger")
    except requests.RequestException as exc:
        logging.exception("Error calling Facebook API")
        flash(f"Error calling API: {exc}", "danger")
    return redirect(url_for("api_calls.api_calls_home"))
