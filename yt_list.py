import yt_dlp

# Lưu thông tin vào bảng playlist và videos
def save_playlist_and_videos_to_mysql(
    connection, playlist_id, playlist_title, video_data
):
    cursor = connection.cursor()

    print("Đang lưu thông tin playlist và video...")

    # Lưu thông tin playlist vào bảng playlist
    cursor.execute(
        "INSERT INTO playlist (id, title) VALUES (%s, %s) ON DUPLICATE KEY UPDATE title=%s",
        (playlist_id, playlist_title, playlist_title),
    )

    # Lưu thông tin video vào bảng videos
    for video in video_data:
        cursor.execute(
            "INSERT INTO videos (id, title, playlist_id, crawled) VALUES (%s, %s, %s, %s)",
            (
                video["id"],
                video["title"],
                playlist_id,
                "No",
            ),  # 'Yes' đánh dấu đã crawl
        )

    # Commit và đóng kết nối
    connection.commit()
    cursor.close()

    print(f"Thông tin playlist và video đã được lưu vào MySQL.")


# Hàm lấy thông tin playlist và video từ URL
def get_playlist_info_and_video_details(playlist_url,connection):
    if connection is None:
        print("Không thể kết nối đến MySQL.")
        return

    # Cài đặt các tùy chọn để lấy thông tin về playlist
    ydl_opts = {
        "extract_flat": True,  # Lấy danh sách video mà không tải video
        "quiet": False,  # Hiển thị thông tin trong quá trình lấy dữ liệu
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Lấy thông tin playlist
            info_dict = ydl.extract_info(playlist_url, download=False)

            if "entries" in info_dict:
                # Lấy thông tin playlist
                playlist_id = info_dict.get("id", "Unknown ID")
                playlist_title = info_dict.get("title", "Unknown Title")

                # Lấy thông tin video trong playlist
                video_data = []
                for video in info_dict["entries"]:
                    video_id = video["id"]
                    video_title = video["title"]
                    video_data.append({"id": video_id, "title": video_title})

                # Lưu thông tin vào MySQL
                save_playlist_and_videos_to_mysql(
                    connection, playlist_id, playlist_title, video_data
                )

            else:
                print("Không tìm thấy video trong playlist.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

# Ví dụ sử dụng
playlist_url = "https://www.youtube.com/playlist?list=PLE4UtJLkLkg9lAIX3PqBmpVT-NiuXfgx9"  # Thay thế bằng URL danh sách phát của bạn
