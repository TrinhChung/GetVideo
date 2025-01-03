import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os
from dotenv import load_dotenv

# Load các biến môi trường từ file .env
load_dotenv()

TOKEN_TELEGRAM_BOT = os.getenv("TOKEN_TELEGRAM_BOT")


# Hàm xử lý khi nhận lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Chào bạn! Bot đã sẵn sàng nhận tin nhắn.")


# Hàm xử lý tin nhắn gửi đến bot
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text  # Lấy nội dung tin nhắn
    print(f"Nhận tin nhắn: {text}")  # In tin nhắn ra console
    await update.message.reply_text(f"Bạn vừa gửi: {text}")  # Trả lời lại tin nhắn


# Hàm khởi tạo bot Telegram
def initial_bot_telegram():
    # Kiểm tra token
    if not TOKEN_TELEGRAM_BOT:
        raise ValueError("TOKEN_TELEGRAM_BOT chưa được cấu hình trong file .env")

    # Tạo ứng dụng Telegram bot
    application = Application.builder().token(TOKEN_TELEGRAM_BOT).build()

    # Đăng ký handler cho lệnh /start
    application.add_handler(CommandHandler("start", start))

    # Đăng ký handler để xử lý tin nhắn văn bản
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    return application


# Hàm chạy bot trong event loop
def run_bot():
    # Tạo ứng dụng bot
    application = initial_bot_telegram()

    # Tạo event loop mới cho bot
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)  # Gán event loop mới cho thread hiện tại

    # Chạy bot trong event loop
    loop.run_until_complete(
        application.run_polling()
    )  # Sử dụng run_until_complete thay vì run_polling trực tiếp
