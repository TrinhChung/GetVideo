# Import các thư viện và model cần thiết
from flask import (
    Blueprint,
    request,
    flash,
    redirect,
    url_for,
    session,
    render_template,
)
from facebook import GraphAPI
from models.facebook_account import FacebookAccount
from models.facebook_campaign import FacebookCampaign
from models.facebook_ad_account import FacebookAdAccount
from datetime import datetime
from database_init import db

ads_manager_bp = Blueprint("ads_manager", __name__)


# Route tạo chiến dịch quảng cáo
@ads_manager_bp.route("/campaign_fb/create", methods=["GET", "POST"])
def create_fb_campaign():
    # Lấy user_id từ session
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    # Lấy danh sách tài khoản quảng cáo Facebook của người dùng
    ad_accounts = FacebookAdAccount.query.filter_by(user_id=user_id).all()

    if request.method == "POST":
        # Lấy access_token của người dùng từ database
        facebook_account = FacebookAccount.query.filter_by(user_id=user_id).first()
        if not facebook_account:
            flash("Facebook account not found", "danger")
            return redirect(url_for("facebook.add_fb_account"))

        # Lấy ad_account_id từ input
        ad_account_id = request.form.get("ad_account_id")
        if not ad_account_id:
            flash("Facebook Ad Account ID is required", "danger")
            return redirect(url_for("ads_manager.create_fb_campaign"))

        # Lấy thông tin tài khoản quảng cáo từ database
        ad_account = FacebookAdAccount.query.filter_by(
            facebook_ad_account_id=ad_account_id
        ).first()
        if not ad_account:
            flash("Facebook Ad Account not found", "danger")
            return redirect(url_for("ads_manager.create_fb_campaign"))

        # Khởi tạo GraphAPI với access_token
        graph = GraphAPI(access_token=facebook_account.access_token)

        # Lấy dữ liệu từ request
        campaign_name = request.form.get("campaign_name")
        objective = request.form.get("objective", "CONVERSIONS")
        status = request.form.get("status", "PAUSED")

        try:
            # Tạo chiến dịch quảng cáo trên Facebook
            campaign = graph.put_object(
                parent_object=f"act_{ad_account.facebook_ad_account_id}/campaigns",
                connection_name="",
                name=campaign_name,
                objective=objective,
                status=status,
            )

            # Lưu thông tin chiến dịch vào database
            new_campaign = FacebookCampaign(
                facebook_campaign_id=campaign["id"],
                name=campaign_name,
                objective=objective,
                status=status,
                created_time=datetime.now(),
                user_id=user_id,
                facebook_account_id=facebook_account.id,
            )
            db.session.add(new_campaign)
            db.session.commit()

            flash("Facebook campaign created successfully!", "success")
            return redirect(url_for("ads_manager.list_fb_campaigns"))

        except Exception as e:
            flash(f"Error creating Facebook campaign: {e}", "danger")
            return redirect(url_for("ads_manager.create_fb_campaign"))

    # Render trang tạo chiến dịch với danh sách tài khoản quảng cáo
    return render_template("create_campaign.html", ad_accounts=ad_accounts)


# Route hiển thị danh sách chiến dịch quảng cáo
@ads_manager_bp.route("/campaign_fb/list", methods=["GET"])
def list_fb_campaigns():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    # Lấy thông tin chiến dịch từ cơ sở dữ liệu
    campaigns = FacebookCampaign.query.filter_by(user_id=user_id).all()

    # Render danh sách chiến dịch
    return render_template("facebook_campaign_list.html", campaigns=campaigns)
