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
    """Trigger 2 loại API call: get_posts_of_pages, get_ads_detail (tổng 600 calls)."""
    if "facebook_user_id" not in session:
        flash("You need to log in to access this page.", "danger")
        return redirect(url_for("auth.login"))

    token = _get_access_token()
    if not token:
        return redirect(url_for("api_calls.api_calls_home"))

    fb_api = "https://graph.facebook.com/v21.0"
    total_calls = 600  # tổng số call
    delay_sec = 0.05  # tránh bị chặn rate limit

    try:
        # --- NÚT LẤY POST CỦA PAGE ---
        if action == "get_posts_of_pages":
            # Lấy danh sách page
            response = requests.get(
                f"{fb_api}/me/accounts", params={"access_token": token}
            )
            if not response.ok:
                flash(f"Lỗi lấy danh sách page: {response.text}", "danger")
                return redirect(url_for("api_calls.api_calls_home"))

            pages = response.json().get("data", [])
            if not pages:
                flash("Không có trang nào được liên kết với tài khoản này.", "danger")
                return redirect(url_for("api_calls.api_calls_home"))

            flash(
                f"Đã tìm thấy {len(pages)} trang. Đang gọi {total_calls} API...", "info"
            )

            calls_per_page = max(1, total_calls // len(pages))
            call_count = 0

            for page in pages:
                for _ in range(calls_per_page):
                    page_id = page["id"]
                    page_access_token = page["access_token"]
                    posts_url = f"{fb_api}/{page_id}/posts"
                    posts_params = {
                        "fields": "id,message,created_time,reactions.summary(true),comments.summary(true)",
                        "access_token": page_access_token,
                    }
                    post_res = requests.get(posts_url, params=posts_params)
                    call_count += 1

                    if not post_res.ok:
                        flash(
                            f"Lỗi lấy post cho page {page_id}: {post_res.text}",
                            "danger",
                        )
                        break

                    # Xử lý dữ liệu ở đây nếu muốn
                    time.sleep(delay_sec)

            flash(f"Hoàn tất {call_count} calls lấy bài viết của page.", "success")

        # --- NÚT LẤY ADS DETAIL ---
        elif action == "get_ads_detail":
            acc_res = requests.get(
                f"{fb_api}/me/adaccounts", params={"access_token": token}
            )
            if not acc_res.ok:
                flash(f"Lỗi lấy danh sách ad account: {acc_res.text}", "danger")
                return redirect(url_for("api_calls.api_calls_home"))

            accounts = acc_res.json().get("data", [])
            if not accounts:
                flash("Không tìm thấy tài khoản quảng cáo nào.", "danger")
                return redirect(url_for("api_calls.api_calls_home"))

            flash(
                f"Đã tìm thấy {len(accounts)} ad account. Đang gọi {total_calls} API...",
                "info",
            )

            calls_per_acc = max(1, total_calls // len(accounts))
            call_count = 0

            for acc in accounts:
                account_id = acc["id"].replace("act_", "")
                for _ in range(calls_per_acc):
                    ads_url = f"{fb_api}/act_{account_id}/ads"
                    ads_params = {
                        "fields": (
                            "id,adset_id,name,status,"
                            "insights{impressions,clicks,spend,cpm,cpc,cpp,ctr,frequency,date_start,date_stop}"
                        ),
                        "access_token": token,
                    }
                    ads_res = requests.get(ads_url, params=ads_params)
                    call_count += 1

                    if not ads_res.ok:
                        flash(
                            f"Lỗi lấy ads của account {account_id}: {ads_res.text}",
                            "danger",
                        )
                        break

                    time.sleep(delay_sec)

            flash(f"Hoàn tất {call_count} calls lấy chi tiết ads.", "success")

        else:
            flash("Unknown action.", "danger")

    except Exception as exc:
        logging.exception("Unexpected error in API trigger")
        flash(f"Lỗi: {exc}", "danger")

    return redirect(url_for("api_calls.api_calls_home"))
