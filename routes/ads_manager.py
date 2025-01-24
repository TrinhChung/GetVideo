# Import các thư viện và model cần thiết
from flask import Blueprint, flash, redirect, url_for, session, render_template, request
from models.facebook_account import FacebookAccount
from models.facebook_campaign import FacebookCampaign
from models.facebook_ad_account import FacebookAdAccount
from datetime import datetime
from database_init import db
from Form.create_campaign import FacebookCampaignForm, CampaignForm  # Import form
from util.ads import create_facebook_campaign
from flask_paginate import Pagination, get_page_parameter
from util.post_fb import (
    sync_facebook_campaigns,
)
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Đọc file .env

ads_manager_bp = Blueprint("ads_manager", __name__)


# Route tạo chiến dịch quảng cáo
@ads_manager_bp.route("/campaign_fb/create", methods=["GET", "POST"])
def create_fb_campaign():
    # Lấy user_id từ session
    facebook_account_id = session.get("facebook_user_id")
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    # Lấy danh sách tài khoản quảng cáo Facebook của người dùng
    ad_accounts = FacebookAdAccount.query.filter_by(
        facebook_account_id=facebook_account_id
    ).all()
    form = FacebookCampaignForm()

    # Đổ dữ liệu vào select field (chuyển ID sang str)
    form.ad_account_id.choices = [
        (str(acc.facebook_ad_account_id), acc.name) for acc in ad_accounts
    ]

    if form.validate_on_submit():
        # Lấy access_token của người dùng từ database
        facebook_account = FacebookAccount.query.filter_by(
            id=facebook_account_id
        ).first()
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
    facebook_account_id = session.get("facebook_user_id")
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10  # Số mục hiển thị trên mỗi trang
    form = CampaignForm()

    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    # Lấy danh sách tài khoản quảng cáo của người dùng
    facebook_ad_accounts = FacebookAdAccount.query.filter_by(
        facebook_account_id=facebook_account_id
    ).all()

    # Lọc theo tài khoản quảng cáo nếu có
    ad_account_filter = request.args.get("ad_account_filter")
    query = FacebookCampaign.query.filter_by(facebook_account_id=facebook_account_id)

    if ad_account_filter:
        query = query.filter(
            FacebookCampaign.facebook_ad_account_id == ad_account_filter
        )

    # Lấy danh sách chiến dịch phân trang
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    campaigns = pagination.items

    # Render danh sách chiến dịch
    return render_template(
        "facebook_campaign_list.html",
        campaigns=campaigns,
        form=form,
        facebook_ad_accounts=facebook_ad_accounts,
        pagination=pagination,
    )


# Route đồng bộ chiến dịch với Facebook
@ads_manager_bp.route("/campaign_fb/sync", methods=["POST"])
def sync_campaigns():
    facebook_account_id = session.get("facebook_user_id")
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    message, success = sync_facebook_campaigns(facebook_account_id)

    flash(message, "success" if success else "danger")

    return redirect(url_for("ads_manager.list_fb_campaigns"))


# Route xóa các chiến dịch đã chọn
@ads_manager_bp.route("/campaign_fb/delete_selected", methods=["POST"])
def delete_selected_campaigns():
    facebook_account_id = session.get("facebook_user_id")
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    selected_campaign_ids = request.form.getlist("selected_campaigns")
    if not selected_campaign_ids:
        flash("No campaigns selected", "danger")
        return redirect(url_for("ads_manager.list_fb_campaigns"))

    # Xóa chiến dịch đã chọn
    for campaign_id in selected_campaign_ids:
        campaign = FacebookCampaign.query.filter_by(
            facebook_campaign_id=campaign_id, facebook_account_id=facebook_account_id
        ).first()
        if campaign:
            db.session.delete(campaign)
    db.session.commit()

    flash("Selected campaigns deleted successfully!", "success")
    return redirect(url_for("ads_manager.list_fb_campaigns"))


# Route chỉnh sửa chiến dịch
@ads_manager_bp.route("/campaign_fb/modify/<campaign_id>", methods=["GET", "POST"])
def modify_campaign(campaign_id):
    facebook_account_id = session.get("facebook_user_id")
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    campaign = FacebookCampaign.query.filter_by(
        facebook_campaign_id=campaign_id, facebook_account_id=facebook_account_id
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

@ads_manager_bp.route('/ads/<account_id>')
def view_ads(account_id):
    # Check if user is logged in
    facebook_account_id = session.get("facebook_user_id")
    if not facebook_account_id:
        flash("You need to log in to use this function", "danger")
        return redirect(url_for("auth.login"))

    # Retrieve access token from database based on facebook_user_id
    facebook_account = FacebookAccount.query.filter_by(id=facebook_account_id).first()
    if not facebook_account:
        flash("Facebook account not found", "danger")
        return redirect(url_for("auth.login"))

    access_token = facebook_account.access_token

    access_token_marketing = os.getenv("ACCESS_TOKEN_MARKETING")

    # Construct API URL to fetch ads for the selected ad account with extended fields
    url = f"https://graph.facebook.com/v21.0/act_{account_id}/ads"
    params = {
        "fields": (
            "id,adset_id,name,status,"
            "insights{impressions,clicks,spend,cpm,cpc,cpp,ctr,frequency,date_start,date_stop}"
        ),
        "access_token": access_token_marketing,
    }

    # Make API call and handle response
    response = requests.get(url, params=params)

    if response.status_code != 200:
        try:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'Unknown error occurred')
        except Exception:
            error_message = 'Unknown error occurred'
        print(error_message)
        flash(f"Login session expired, please log in again", "danger")
        return redirect(url_for("auth.login"))

    ads_data = response.json()
    ads = ads_data.get('data', [])

    ad_id_list = []
    adset_id_list = []

    for ad in ads_data.get("data", []):
        ad_id_list.append(ad["id"])
        adset_id_list.append(ad.get("adset_id", "N/A"))

    print(f"Số lượng quảng cáo: {len(ad_id_list)}")
    print(f"Số lượng nhóm quảng cáo: {len(adset_id_list)}")

    isContinue = True;

    # for i in range(1,400):
    #     if isContinue == True:
    #         print(i)
    #         isContinue = get_facebook_insights(account_id, access_token)

    # for i in range(1, 10):
    #      if isContinue == True:
    #         print(i * (len(ad_id_list) + len(adset_id_list)))
    # isContinue = fetch_facebook_ad_details(ad_id_list, adset_id_list, access_token_marketing)
    #         #fetch_facebook_ad_details(ad_id_list, adset_id_list, access_token)

    # Render template with detailed insights
    return render_template('ads_detail.html', account_id=account_id, ads=ads)
