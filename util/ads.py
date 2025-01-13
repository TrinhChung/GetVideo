# util/ads.py

import requests


def create_facebook_campaign(ad_account_id, campaign_data, access_token):
    try:
        url = f"https://graph.facebook.com/v21.0/act_{ad_account_id}/campaigns"
        campaign_data["access_token"] = access_token
        response = requests.post(url, data=campaign_data)

        if response.status_code == 200:
            return (
                response.json()
            )  # Return the campaign data if the request is successful
        else:
            raise Exception(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request to Facebook API failed: {e}")


def fetch_facebook_campaigns(ad_account_id, access_token):
    try:
        url = f"https://graph.facebook.com/v21.0/act_{ad_account_id}/campaigns?fields=start_time,objective,name,status,created_time,stop_time,special_ad_categories"
        params = {"access_token": access_token}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            raise Exception(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request to Facebook API failed: {e}")
