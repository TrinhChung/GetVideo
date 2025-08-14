from flask import Blueprint, render_template, session, flash, redirect, url_for
from models.facebook_account import FacebookAccount
from models.facebook_ad_account import FacebookAdAccount
from models.page import Page
import requests
import logging
import time

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
    """Check if response indicates Facebook API rate limit."""
    try:
        # Status code 429: rõ ràng là rate limit
        if response.status_code == 429:
            flash(
                "Facebook API rate limit reached (HTTP 429). Please pause and try again later.",
                "danger",
            )
            return True

        # Facebook có thể trả 200/400 nhưng chứa thông báo limit trong JSON
        data = response.json()
        error = data.get("error", {})
        if error.get("code") == 4 or "Application request limit reached" in error.get(
            "message", ""
        ):
            flash(
                "Facebook API rate limit reached (code 4). Please pause and try again later.",
                "danger",
            )
            return True
    except ValueError:
        # Không phải JSON, bỏ qua
        pass
    return False


def _get_access_token():
    """Lấy access token của user hiện tại."""
    facebook_account_id = session.get("facebook_user_id")
    account = FacebookAccount.query.filter_by(id=facebook_account_id).first()
    if not account:
        flash("Facebook account not found.", "danger")
        return None
    return account.access_token


@api_calls_bp.route("/api_calls/trigger/<string:action>", methods=["POST"])
def trigger_api_call(action: str):
    """Trigger specific Facebook API call repeatedly until near rate limit."""
    if "facebook_user_id" not in session:
        flash("You need to log in to access this page.", "danger")
        return redirect(url_for("auth.login"))

    token = _get_access_token()
    if not token:
        return redirect(url_for("api_calls.api_calls_home"))

    fb_api = "https://graph.facebook.com/v21.0"
    max_calls = 400
    delay_sec = 0.02

    try:
        for i in range(max_calls):
            try:
                response = None

                if action == "account_fb":
                    response = requests.get(
                        f"{fb_api}/me", params={"access_token": token}
                    )

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
                            flash(
                                f"Stopped after {i+1} calls due to rate limit.",
                                "warning",
                            )
                            return redirect(url_for("api_calls.api_calls_home"))

                elif action == "list_ad_accounts":
                    response = requests.get(
                        f"{fb_api}/me/adaccounts", params={"access_token": token}
                    )

                elif action in {"fetch_facebook_campaigns", "list_fb_campaigns"}:
                    ads = FacebookAdAccount.query.filter_by(
                        facebook_account_id=session["facebook_user_id"]
                    ).all()
                    for ad in ads:
                        response = requests.get(
                            f"{fb_api}/{ad.facebook_ad_account_id}/campaigns",
                            params={"access_token": token},
                        )
                        if _check_rate_limit(response):
                            flash(
                                f"Stopped after {i+1} calls due to rate limit.",
                                "warning",
                            )
                            return redirect(url_for("api_calls.api_calls_home"))

                elif action in {"view_ads", "get_account_ads"}:
                    ads = FacebookAdAccount.query.filter_by(
                        facebook_account_id=session["facebook_user_id"]
                    ).all()
                    for ad in ads:
                        response = requests.get(
                            f"{fb_api}/{ad.facebook_ad_account_id}/ads",
                            params={"access_token": token},
                        )
                        if _check_rate_limit(response):
                            flash(
                                f"Stopped after {i+1} calls due to rate limit.",
                                "warning",
                            )
                            return redirect(url_for("api_calls.api_calls_home"))

                else:
                    flash("Unknown action.", "danger")
                    return redirect(url_for("api_calls.api_calls_home"))

                if response and _check_rate_limit(response):
                    flash(f"Stopped after {i+1} calls due to rate limit.", "warning")
                    break

                if response and not response.ok:
                    flash(f"API call failed at loop {i+1}: {response.text}", "danger")
                    break

                time.sleep(delay_sec)

            except requests.RequestException as req_err:
                logging.exception("Request error")
                flash(f"Request error at loop {i+1}: {req_err}", "danger")
                break

        else:
            flash(f"Finished {max_calls} calls without hitting rate limit.", "success")

    except Exception as exc:
        logging.exception("Unexpected error in API loop")
        flash(f"Unexpected error: {exc}", "danger")

    return redirect(url_for("api_calls.api_calls_home"))
