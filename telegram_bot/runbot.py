import asyncio
import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
from dump import get_pages  # Đảm bảo hàm get_pages được định nghĩa để lấy danh sách page

# Load các biến môi trường từ file .env
load_dotenv()

TOKEN_TELEGRAM_BOT = os.getenv("TOKEN_TELEGRAM_BOT")

# Biến toàn cục lưu trạng thái người dùng
user_data = {}


# Hàm xử lý khi nhận lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Lấy danh sách page từ cơ sở dữ liệu hoặc file
    pages = get_pages()  # Hàm get_pages trả về danh sách tuple (page_id, page_name, ...)
    if not pages:
        await update.message.reply_text("Không có page nào để chọn.")
        return

    # Tạo từ điển ánh xạ tên page -> page_id
    context.user_data["page_mapping"] = {page[1]: page[0] for page in pages}

    # Tạo bàn phím với danh sách các tên page
    keyboard = [[page[1]] for page in pages]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False
    )

    await update.message.reply_text(
        "Chọn page bạn muốn đính kèm:",
        reply_markup=reply_markup,
    )


# Hàm xử lý lựa chọn loại page
async def select_link_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    selected_page_name = update.message.text

    # Lấy page_id từ page_mapping
    page_mapping = context.user_data.get("page_mapping", {})
    selected_page_id = page_mapping.get(selected_page_name)

    if not selected_page_id:
        await update.message.reply_text("Page không hợp lệ, vui lòng chọn lại.")
        return

    # Lưu trạng thái lựa chọn page (sử dụng page_id)
    user_data[user_id] = selected_page_id
    await update.message.reply_text(f"Bạn đã chọn page: {selected_page_name}")


# Hàm xử lý link gửi đến
async def handle_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    link = update.message.text

    # Kiểm tra loại page đã chọn
    selected_page_id = user_data.get(user_id, None)
    if not selected_page_id:
        await update.message.reply_text("Hãy chọn page trước khi gửi link.")
        return

    # Xác minh định dạng link
    if "http" in link or "www" in link:
        await update.message.reply_text(
            f"Đã nhận link cho page ID {selected_page_id}: {link}"
        )
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

    # Đăng ký handler để xử lý lựa chọn loại page
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, select_link_type)
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
