import requests
from flask import request, g
from database_init import db
from models.app_env import AppEnv


def parse_env_text(env_text):
    """Chuyển ENV dạng text thành dict."""
    env_dict = {}
    if not env_text:
        return env_dict
    for line in env_text.strip().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            env_dict[key.strip()] = value.strip()
    return env_dict


def get_env_before_request(api_base_url="http://127.0.0.1:4000"):
    """
    Lấy env theo domain từ DB hoặc API, lưu vào g.
    Nếu chưa có trong DB thì gọi API backend và lưu lại.
    """
    # 1. Xác định domain
    x_forwarded_host = request.headers.get("X-Forwarded-Host")
    if x_forwarded_host:
        parts = [p.strip() for p in x_forwarded_host.split(",")]
        domain = parts[-1]
    else:
        host_header = request.headers.get("Host")
        domain = host_header.split(":")[0] if host_header else "localhost"

    env_dict = None

    # 2. Kiểm tra DB trước
    record = AppEnv.query.filter_by(domain=domain).first()
    if record:
        env_dict = {
            "APP_ID": record.app_id,
            "APP_SECRET": record.app_secret,
            "SECRET_KEY": record.secret_key,
            "FLASK_ENV": record.flask_env,
            "PASSWORD_DB": record.password_db,
            "NAME_DB": record.name_db,
            "USER_DB": record.user_db,
            "ADDRESS_DB": record.address_db,
            "APP_NAME": record.app_name,
            "EMAIL": record.email,
            "ADDRESS": record.address,
            "PHONE_NUMBER": record.phone_number,
            "DNS_WEB": record.dns_web,
            "COMPANY_NAME": record.company_name,
            "TAX_NUMBER": record.tax_number,
        }
        g.client_domain = domain
        g.client_env = env_dict
        return

    # 3. Nếu chưa có, gọi API backend
    url = f"{api_base_url}/api/deployed_app"
    headers_with_forwarded = {"X-Client-Domain": domain}
    print(url)

    try:
        resp = requests.get(url, headers=headers_with_forwarded, timeout=5)
        resp.raise_for_status()
        json_data = resp.json()

        env_text = json_data.get("env") if isinstance(json_data, dict) else None
        env_dict = parse_env_text(env_text)

        # 4. Lưu vào DB
        record = AppEnv(domain=domain)
        record.app_id = env_dict.get("APP_ID")
        record.app_secret = env_dict.get("APP_SECRET")
        record.secret_key = env_dict.get("SECRET_KEY")
        record.flask_env = env_dict.get("FLASK_ENV")
        record.password_db = env_dict.get("PASSWORD_DB")
        record.name_db = env_dict.get("NAME_DB")
        record.user_db = env_dict.get("USER_DB")
        record.address_db = env_dict.get("ADDRESS_DB")
        record.app_name = env_dict.get("APP_NAME")
        record.email = env_dict.get("EMAIL")
        record.address = env_dict.get("ADDRESS")
        record.phone_number = env_dict.get("PHONE_NUMBER")
        record.dns_web = env_dict.get("DNS_WEB")
        record.company_name = env_dict.get("COMPANY_NAME")
        record.tax_number = env_dict.get("TAX_NUMBER")

        db.session.add(record)
        db.session.commit()

    except requests.RequestException as e:
        print(f"❌ Lỗi khi gọi backend: {e}")
        env_dict = None

    # 5. Lưu vào g để các route dùng chung
    g.client_domain = domain
    g.client_env = env_dict
