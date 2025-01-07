from apscheduler.schedulers.background import BackgroundScheduler
from cronjob.post_auto import post_video_schedule,job_function

    
# Khởi tạo APScheduler
scheduler = BackgroundScheduler()

# Đăng ký job chạy mỗi 30 phút
#scheduler.add_job(post_video_schedule, 'interval', minutes=30)

#scheduler.add_job(job_function, 'interval', seconds=30)


