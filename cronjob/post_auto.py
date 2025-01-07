import logging
from datetime import datetime, timedelta
from models.stack_post import StackPost
from util.post_fb import create_video_post
from database_init import db

# Cấu hình logger
logger = logging.getLogger(__name__)

# Hàm cần chạy định kỳ mỗi 30 phút
def post_video_schedule():
    # Lấy thời gian hiện tại trừ đi 30 phút
    time_limit = datetime.utcnow() - timedelta(minutes=30)

    # Tìm các bài đăng có trạng thái "pending" và thời gian đăng nhỏ hơn hoặc bằng 30 phút trước
    stack_posts = StackPost.query.filter(
        StackPost.status == "pending",
        StackPost.time <= time_limit
    ).all()

    logger.info(f"Đã tìm thấy {len(stack_posts)} bài đăng.")

    for stack_post in stack_posts:
        # Kiểm tra nếu đã có video_id được đăng, tránh đăng lại
        if not stack_post.posted_video_id:
            try:
                # Lấy thông tin của page từ StackPost
                page = Page.query.filter_by(page_id=stack_post.page_id).first()

                if not page:
                    logger.error(f"Không tìm thấy thông tin Page với page_id {stack_post.page_id}")
                    continue

                # Lấy access_token và page_id từ Page
                access_token = page.access_token
                page_id = page.page_id

                # Gọi hàm create_video_post để đăng bài
                create_video_post(
                    page_id=page_id,
                    access_token=access_token,
                    video_path="path_to_video_file_here",  # Thay thế với đường dẫn video thực tế
                    message=stack_post.title  # Hoặc bất kỳ thông điệp nào bạn muốn
                )

                # Cập nhật trạng thái bài đăng thành "completed" và lưu lại video_id
                stack_post.status = "completed"
                stack_post.posted_video_id = "video_id_here"  # Gán video_id sau khi thành công
                db.session.commit()

                logger.info(f"Bài đăng với ID {stack_post.id} đã được đăng thành công.")
            except Exception as e:
                logger.error(f"Đã xảy ra lỗi khi đăng bài với ID {stack_post.id}: {e}")

def job_function():
    logger.info("App Dang chay")