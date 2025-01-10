# Sử dụng Python 3.10 làm base image
FROM python:3.10-slim

# Đặt thư mục làm việc
WORKDIR /app

# Cài đặt các gói cần thiết cho hệ thống, bao gồm pkg-config và các thư viện MySQL
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt thư viện `watchdog` cho Flask hot reload
RUN pip install watchdog

# Sao chép các tệp cần thiết vào container
COPY . /app

# Cài đặt các thư viện Python từ file requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt môi trường runtime
ENV FLASK_ENV=development

# Thiết lập cổng chạy ứng dụng
EXPOSE 5000

# Lệnh chạy ứng dụng Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
