Canvas Flask Video Downloader App
Ứng dụng Flask này cho phép người dùng tải video từ YouTube và Facebook thông qua việc nhập URL video. Người dùng chỉ cần nhập URL của video vào ô input và nhấn nút để tải video về máy tính của họ.

# Tạo môi trường ảo
```bash
python -m venv myenv
```
# Kích hoạt môi trường ảo
# Trên Windows
```bash
myenv\Scripts\activate
```

# Seed DBDB
```bash
python dump.py
```

# Run App
```bash
python app.py
```

# Trên macOS/Linux
```bash
source myenv/bin/activate
```

```bash
pip freeze > requirements.txt
```

```bash
pip install -r requirements.txt
```
# Run Telegram bot
```bash
python telegram_bot/runbot.py
```