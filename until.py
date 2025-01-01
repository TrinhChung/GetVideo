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


def extract_playlist_id(url):
    """
    Trích xuất ID playlist từ URL YouTube.
    Args:
        url: URL của playlist YouTube (ví dụ: https://www.youtube.com/playlist?list=PLE4UtJLkLkg9lAIX3PqBmpVT-NiuXfgx9)
    Returns:
        ID của playlist nếu tìm thấy, ngược lại trả về None
    """
    try:
        # Phân tích URL
        parsed_url = urlparse(url)
        # Trích xuất các tham số truy vấn
        query_params = parse_qs(parsed_url.query)
        # Lấy giá trị tham số 'list'
        playlist_id = query_params.get("list", [None])[0]
        return playlist_id
    except Exception as e:
        print(f"Đã xảy ra lỗi khi trích xuất playlist ID: {e}")
        return None
