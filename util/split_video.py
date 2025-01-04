from moviepy.editor import VideoFileClip  # Dùng để làm việc với video
import os
import re


def clean_title(title):
    """
    Làm sạch tiêu đề video: loại bỏ các từ hoặc cụm từ không cần thiết và định dạng video ở cuối.
    """
    # Loại bỏ định dạng video ở cuối (vd: .mp4, .avi, .mkv, ...), case-insensitive
    title = re.sub(r"\.(mp4|avi|mkv|mov|flv|wmv|webm)$", "", title, flags=re.IGNORECASE)
    
    # Loại bỏ các đoạn chứa '[Review Phim]' hoặc những gì nằm sau dấu '|'
    title = re.sub(r"\[.*?\]", "", title)  # Xóa phần trong dấu []
    title = re.sub(r"\|.*", "", title)  # Xóa phần sau dấu '|'

    # Loại bỏ các ký tự đặc biệt không cần thiết (ngoại trừ dấu cách và chữ cái, số)
    title = re.sub(r"[^\w\s]", "", title)  # Xóa ký tự đặc biệt
    title = title.strip()  # Loại bỏ khoảng trắng thừa ở đầu và cuối

    return title


def split_video(
    video_path, segment_duration_sec, output_prefix="output_part", codec="libx264"
):
    """
    Chia video thành các phần nhỏ và lưu vào thư mục cố định.

    Parameters:
        video_path (str): Đường dẫn tới video cần cắt.
        segment_duration_sec (int): Thời gian của mỗi phần (tính bằng giây).
        output_prefix (str): Tiền tố của tên các file xuất ra.
        codec (str): Bộ mã hóa video để sử dụng khi xuất file (mặc định là "libx264").
    """
    output_dir = r"C:\Users\chung\Videos\Splited"  # Đường dẫn thư mục cố định

    # Kiểm tra và tạo thư mục nếu chưa tồn tại
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Đọc video
    video = VideoFileClip(video_path)

    # Lấy tên file từ đường dẫn video
    video_title = os.path.basename(video_path)

    # Làm sạch tên video
    clean_video_title = clean_title(video_title)
    print(clean_video_title)

    # Xác định thời gian bắt đầu và kết thúc
    start_time = 0
    end_time = segment_duration_sec
    i = 1

    # Lặp qua video và cắt thành các phần nhỏ
    while end_time <= video.duration:
        subclip = video.subclip(start_time, end_time)  # Cắt đoạn video
        subclip.write_videofile(
            os.path.join(output_dir, f"{clean_video_title}_Phần_{i}.mp4"), codec=codec
        )  # Lưu phần nhỏ vào thư mục
        i += 1
        start_time = end_time
        end_time += segment_duration_sec

    # Nếu video còn lại một đoạn nhỏ cuối cùng
    if start_time < video.duration:
        subclip = video.subclip(start_time, video.duration)
        subclip.write_videofile(
            os.path.join(output_dir, f"{clean_video_title}_Phần_{i}.mp4"), codec=codec
        )

    print(f"Video đã được chia thành các phần nhỏ và lưu tại {output_dir}!")

# Ví dụ sử dụng hàm
video_paths = [
    r"C:\Users\chung\Videos\Film\Youtube\[Review Phim] Cửu Long Thành Trại - Siêu Phẩm Hành Động Xã Hội Đen 2024.mp4",
]

# Chạy hàm cho từng video
for video_path in video_paths:
    segment_duration_sec = 10 * 60  # Cắt video thành các phần 10 phút
    split_video(video_path, segment_duration_sec)
