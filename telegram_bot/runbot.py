import asyncio
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
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

# Biến toàn cục lưu trạng thái người dùng
user_data = {}


# Hàm xử lý khi nhận lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [["YouTube Link", "Facebook Link"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False
    )

    await update.message.reply_text(
        "Chọn loại link bạn muốn đính kèm:",
        reply_markup=reply_markup,
    )


# Hàm xử lý lựa chọn loại link
async def select_link_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "YouTube Link":
        user_data[user_id] = "youtubelink"
        await update.message.reply_text("Bạn đã chọn đính kèm link YouTube.")
    elif text == "Facebook Link":
        user_data[user_id] = "facebooklink"
        await update.message.reply_text("Bạn đã chọn đính kèm link Facebook.")
    else:
        await update.message.reply_text(
            "Lựa chọn không hợp lệ. Vui lòng chọn loại link từ menu."
        )


# Hàm xử lý link gửi đến
async def handle_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    link = update.message.text

    # Kiểm tra loại link đã chọn
    link_type = user_data.get(user_id, None)
    if not link_type:
        await update.message.reply_text("Hãy chọn loại link trước khi gửi.")
        return

    # Xác minh định dạng link
    if link_type == "youtubelink" and ("youtube.com" in link or "youtu.be" in link):
        await update.message.reply_text(f"Đã nhận YouTube Link: {link}")
    elif link_type == "facebooklink" and "facebook.com" in link:
        await update.message.reply_text(f"Đã nhận Facebook Link: {link}")
    else:
        await update.message.reply_text("Link không đúng định dạng, vui lòng thử lại.")


# Hàm khởi tạo bot Telegram
def initial_bot_telegram():
    if not TOKEN_TELEGRAM_BOT:
        raise ValueError("TOKEN_TELEGRAM_BOT chưa được cấu hình trong file .env")

    # Tạo ứng dụng Telegram bot
    application = Application.builder().token(TOKEN_TELEGRAM_BOT).build()

    # Đăng ký handler cho lệnh /start
    application.add_handler(CommandHandler("start", start))

    # Đăng ký handler để xử lý lựa chọn loại link
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^(YouTube Link|Facebook Link)$"),
            select_link_type,
        )
    )

    # Đăng ký handler để xử lý link
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_links)
    )

    return application


# Hàm chạy bot
def run_bot():
    application = initial_bot_telegram()

    # Chạy bot trong event loop hiện tại
    asyncio.run(application.run_polling())


if __name__ == "__main__":
    run_bot()
