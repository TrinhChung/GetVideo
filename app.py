from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from yt_list import get_playlist_info_and_video_details
from youtube import download_video, download_video_facebook, download_video_by_url
from dotenv import load_dotenv
import os

load_dotenv()

PASSWORD_DB = os.getenv("PASSWORD_DB")  # Token truy cập của bạn
# Tạo ứng dụng Flask
app = Flask(__name__)

# Cấu hình kết nối MySQL
app.config["MYSQL_HOST"] = "localhost"  # Máy chủ MySQL (localhost cho máy tính cá nhân)
app.config["MYSQL_USER"] = "root"  # Tên người dùng MySQL
app.config["MYSQL_PASSWORD"] = PASSWORD_DB  # Mật khẩu người dùng MySQL
app.config["MYSQL_DB"] = "video"  # Tên cơ sở dữ liệu MySQL

# Khởi tạo đối tượng MySQL
mysql = MySQL(app)

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")  # Truyền dữ liệu cho template

@app.route("/batch", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Lấy video từ cơ sở dữ liệu khi nhấn nút "Lấy Video"
        get_playlist_info_and_video_details(
            request.form["playlist_url"], mysql.connection
        )
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM videos")  # Giả sử bạn có bảng 'videos'
        videos = cur.fetchall()  # Lấy tất cả dữ liệu
        cur.close()
        return render_template(
            "index.html", videos=videos
        )  # Truyền dữ liệu cho template

    # Nếu là GET request, hiển thị trang ban đầu (có thể lấy danh sách video)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM videos")  # Lấy dữ liệu video từ bảng videos
    videos = cur.fetchall()  # Lấy tất cả dữ liệu
    cur.close()
    return render_template("index.html", videos=videos)  # Truyền dữ liệu cho template


@app.route("/download/<video_id>", methods=["POST"])
def download_video_route(video_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM videos WHERE id = %s", (video_id,))
    video = cur.fetchone()

    if video and video[3] == "No":
        try:
            # Gọi hàm download_video để tải video
            download_video(video_id)
            # Sau khi tải video, cập nhật trạng thái thành 'Yes'
            cur.execute(
                "UPDATE videos SET crawled = %s WHERE id = %s", ("Yes", video_id)
            )
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("index"))
        except Exception as e:
            cur.close()
            return render_template(
                "error.html", error_message=f"Đã xảy ra lỗi khi tải video: {e}"
            )

    cur.close()
    return redirect(url_for("index"))


@app.route("/download_all", methods=["POST"])
def download_all_videos():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM videos WHERE crawled = 'No'"
    )  # Lọc video có trạng thái 'No'
    videos_to_download = cur.fetchall()

    for video in videos_to_download:
        try:
            # Gọi hàm download_video để tải từng video
            download_video(video[0])  # video[1] là tiêu đề video
            # Cập nhật trạng thái thành 'Yes'
            cur.execute(
                "UPDATE videos SET crawled = %s WHERE id = %s", ("Yes", video[0])
            )
        except Exception as e:
           print(f"Đã xảy ra lỗi: {e}")

    mysql.connection.commit()
    cur.close()
    return redirect(url_for("index"))


@app.route("/download-url", methods=["GET", "POST"])
def download_from_url():
    if request.method == "POST":
        video_url = request.form.get("video_url")
        if video_url:
            try:
                # Cấu hình yt_dlp
                download_video_by_url(video_url)

                # Trả file về cho người dùng
                return render_template("downloadFromUrl.html")
            except Exception as e:
                return render_template("error.html", error_message=e)

    return render_template("downloadFromUrl.html")


@app.route("/download-facebook-url", methods=["POST"])
def download_from_facebook_url():
    if request.method == "POST":
        video_url = request.form.get("video_url")
        if video_url:
            try:
                # Cấu hình yt_dlp
                download_video_facebook(video_url)

                # Trả file về cho người dùng
                return render_template("downloadFromUrl.html")
            except Exception as e:
                return render_template("error.html", error_message=e)

    return render_template("downloadFromUrl.html")


# Route hiển thị danh sách tài khoản Facebook tại đường dẫn /account_fb/
@app.route("/account_fb/")
def account_fb():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, email, access_token FROM facebook_accounts")
    accounts = cursor.fetchall()
    cursor.close()
    return render_template("account_fb.html", accounts=accounts)


# Route để xử lý form thêm tài khoản tại /account_fb/add_account
@app.route("/account_fb/add_account", methods=["POST"])
def add_fb_account():
    if request.method == "POST":
        email = request.form["email"]
        access_token = request.form["access_token"]
        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO facebook_accounts (email, access_token) VALUES (%s, %s)",
                (email, access_token),
            )
            mysql.connection.commit()
            print("Facebook account added successfully!", "success")
        except Exception as e:
            print(f"Error: {e}", "danger")
        finally:
            cursor.close()
        return redirect(url_for("account_fb"))


# Route để xóa tài khoản Facebook tại /account_fb/delete_account/<id>
@app.route("/account_fb/delete_account/<int:id>", methods=["GET", "POST"])
def delete_fb_account(id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM facebook_accounts WHERE id = %s", (id,))
        mysql.connection.commit()
        print("Facebook account deleted successfully!", "success")
    except Exception as e:
        print(f"Error: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for("account_fb"))


if __name__ == "__main__":
    app.run(debug=True)  # Chạy ứng dụng Flask
