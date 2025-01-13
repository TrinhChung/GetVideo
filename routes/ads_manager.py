# Import các thư viện và model cần thiết
from flask import Blueprint, flash, redirect, url_for, session, render_template, request
from models.facebook_account import FacebookAccount
from models.facebook_campaign import FacebookCampaign
from models.facebook_ad_account import FacebookAdAccount
from datetime import datetime
from database_init import db
from Form.create_campaign import FacebookCampaignForm, CampaignForm  # Import form
import requests
from util.ads import create_facebook_campaign, fetch_facebook_campaigns


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
    form = FacebookCampaignForm()

    # Đổ dữ liệu vào select field (chuyển ID sang str)
    form.ad_account_id.choices = [
        (str(acc.facebook_ad_account_id), acc.name) for acc in ad_accounts
    ]

    if form.validate_on_submit():
        # Lấy access_token của người dùng từ database
        facebook_account = FacebookAccount.query.filter_by(user_id=user_id).first()
        if not facebook_account:
            flash("Facebook account not found", "danger")
            return redirect(url_for("facebook.add_fb_account"))

        # Lấy ad_account_id từ form
        ad_account_id = form.ad_account_id.data
        ad_account = FacebookAdAccount.query.filter_by(
            facebook_ad_account_id=ad_account_id
        ).first()
        if not ad_account:
            flash("Facebook Ad Account not found", "danger")
            return redirect(url_for("ads_manager.create_fb_campaign"))

        # Prepare data for the request
        access_token = facebook_account.access_token
        campaign_data = {
            "name": form.campaign_name.data,
            "objective": form.objective.data,
            "status": form.status.data,
            "special_ad_categories": f"['{form.special_ad_categories.data}']",
        }

        try:
            campaign = create_facebook_campaign(
                ad_account.facebook_ad_account_id, campaign_data, access_token
            )

            # Save campaign data to the database
            new_campaign = FacebookCampaign(
                facebook_campaign_id=campaign["id"],
                name=form.campaign_name.data,
                objective=form.objective.data,
                status=form.status.data,
                special_ad_categories=form.special_ad_categories.data,
                created_time=datetime.now(),
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                user_id=user_id,
                facebook_account_id=facebook_account.id,
                facebook_ad_account_id= ad_account.id,
            )
            db.session.add(new_campaign)
            db.session.commit()

            flash("Facebook campaign created successfully!", "success")
            return redirect(url_for("ads_manager.list_fb_campaigns"))
        except Exception as e:
            flash(f"Error creating Facebook campaign: {e}", "danger")
            return redirect(url_for("ads_manager.create_fb_campaign"))

    # Render trang tạo chiến dịch với danh sách tài khoản quảng cáo
    return render_template("create_campaign.html", form=form, ad_accounts=ad_accounts)


# Route hiển thị danh sách chiến dịch quảng cáo
@ads_manager_bp.route("/campaign_fb/list", methods=["GET"])
def list_fb_campaigns():
    user_id = session.get("user_id")
    form = CampaignForm()

    if not user_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    # Lấy thông tin chiến dịch từ cơ sở dữ liệu
    campaigns = FacebookCampaign.query.filter_by(user_id=user_id).all()

    # Render danh sách chiến dịch
    return render_template(
        "facebook_campaign_list.html", campaigns=campaigns, form=form
    )


# Route đồng bộ chiến dịch với Facebook
@ads_manager_bp.route("/campaign_fb/sync", methods=["POST"])
def sync_campaigns():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    facebook_account = FacebookAccount.query.filter_by(user_id=user_id).first()
    if not facebook_account:
        flash("Facebook account not found", "danger")
        return redirect(url_for("facebook.add_fb_account"))

    access_token = facebook_account.access_token

    facebook_ad_accounts = FacebookAdAccount.query.filter_by(user_id=user_id).all()

    if not facebook_ad_accounts:
        flash("No Facebook Ad Accounts found for the user", "danger")
        return redirect(url_for("ads_manager.list_fb_campaigns"))

    for ad_account in facebook_ad_accounts:
        try:
            campaigns = fetch_facebook_campaigns(
                ad_account.facebook_ad_account_id, access_token
            )
        except Exception as e:
            flash(
                f"Error fetching campaigns from Facebook for account {ad_account.name}: {e}",
                "danger",
            )
            continue

        for campaign in campaigns:
            existing_campaign = FacebookCampaign.query.filter_by(
                facebook_campaign_id=campaign["id"]
            ).first()

            if existing_campaign:
                existing_campaign.name = campaign.get("name", existing_campaign.name)
                existing_campaign.objective = campaign.get(
                    "objective", existing_campaign.objective
                )
                existing_campaign.status = campaign.get(
                    "status", existing_campaign.status
                )
                existing_campaign.created_time = campaign.get(
                    "created_time", existing_campaign.created_time
                )
                existing_campaign.start_time = campaign.get(
                    "start_time", existing_campaign.start_time
                )
                existing_campaign.end_time = campaign.get(
                    "end_time", existing_campaign.end_time
                )
                existing_campaign.special_ad_categories = campaign.get(
                    "special_ad_categories", existing_campaign.special_ad_categories
                )

                db.session.commit()
                flash(
                    f"Campaign {existing_campaign.name} updated successfully!",
                    "success",
                )
            else:
                new_campaign = FacebookCampaign(
                    facebook_campaign_id=campaign["id"],
                    name=campaign.get("name"),
                    objective=campaign.get("objective"),
                    status=campaign.get("status"),
                    created_time=campaign.get("created_time"),
                    start_time=campaign.get("start_time"),
                    end_time=campaign.get("end_time"),
                    user_id=user_id,
                    facebook_account_id=campaign.get("account_id"),
                    special_ad_categories=campaign.get("special_ad_categories", ""),
                    facebook_ad_account_id=ad_account.id,
                )
                db.session.add(new_campaign)
                db.session.commit()
                flash(f"Campaign {new_campaign.name} created successfully!", "success")

    return redirect(url_for("ads_manager.list_fb_campaigns"))


# Route xóa các chiến dịch đã chọn
@ads_manager_bp.route("/campaign_fb/delete_selected", methods=["POST"])
def delete_selected_campaigns():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    selected_campaign_ids = request.form.getlist("selected_campaigns")
    if not selected_campaign_ids:
        flash("No campaigns selected", "danger")
        return redirect(url_for("ads_manager.list_fb_campaigns"))

    # Xóa chiến dịch đã chọn
    for campaign_id in selected_campaign_ids:
        campaign = FacebookCampaign.query.filter_by(
            facebook_campaign_id=campaign_id, user_id=user_id
        ).first()
        if campaign:
            db.session.delete(campaign)
    db.session.commit()

    flash("Selected campaigns deleted successfully!", "success")
    return redirect(url_for("ads_manager.list_fb_campaigns"))


# Route chỉnh sửa chiến dịch
@ads_manager_bp.route("/campaign_fb/modify/<campaign_id>", methods=["GET", "POST"])
def modify_campaign(campaign_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    campaign = FacebookCampaign.query.filter_by(
        facebook_campaign_id=campaign_id, user_id=user_id
    ).first()
    if not campaign:
        flash("Campaign not found", "danger")
        return redirect(url_for("ads_manager.list_fb_campaigns"))

    form = FacebookCampaignForm(obj=campaign)

    if form.validate_on_submit():
        campaign.name = form.campaign_name.data
        campaign.objective = form.objective.data
        campaign.status = form.status.data
        campaign.special_ad_categories = form.special_ad_categories.data
        campaign.start_time = form.start_time.data
        campaign.end_time = form.end_time.data

        db.session.commit()

        flash("Campaign updated successfully!", "success")
        return redirect(url_for("ads_manager.list_fb_campaigns"))

    return render_template("modify_campaign.html", form=form, campaign=campaign)
