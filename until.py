from urllib.parse import urlparse, parse_qs

def extract_facebook_video_id(url):
    """
    Trích xuất ID video từ URL Facebook.
    :param url: URL video Facebook (ví dụ: https://www.facebook.com/watch/?v=919627969714758)
    :return: ID của video nếu tìm thấy, ngược lại trả về None.
    """
    try:
        # Phân tích URL
        parsed_url = urlparse(url)
        # Trích xuất các tham số truy vấn
        query_params = parse_qs(parsed_url.query)
        # Lấy giá trị tham số `v`
        video_id = query_params.get("v", [None])[0]
        return video_id
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return None
