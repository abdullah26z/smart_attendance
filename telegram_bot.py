# File: attendance_bot.py
import os, csv
from datetime import datetime, timedelta
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
import qrcode

# ---------------------------
# إعداد البيئة
# ---------------------------
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ATTENDANCE_FILE = "attendance_log.csv"

# ---------------------------
# توليد صورة QR من الكود
# ---------------------------
def qr_code_to_image(qr_content):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio

# ---------------------------
# قراءة CSV
# ---------------------------
def read_last_attendance():
    try:
        with open(ATTENDANCE_FILE, newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            return reader[-1] if reader else None
    except FileNotFoundError:
        return None

# ---------------------------
# أوامر البوت
# ---------------------------
async def last_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    att = read_last_attendance()
    if att:
        message = (
            f"✅ آخر حضور:\n"
            f"التاريخ: {att['datetime']}\n"
            f"الحالة: {att['status']}\n"
            f"QR: {att['qr_code']}\n"
            f"انتهاء صلاحية QR: {att['qr_expires_at']}"
        )
        await update.message.reply_text(message)
        qr_img = qr_code_to_image(att["qr_code"])
        await update.message.reply_photo(photo=InputFile(qr_img, filename="qr.png"))
    else:
        await update.message.reply_text("لا يوجد حضور مسجل حتى الآن.")

async def attendance_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(ATTENDANCE_FILE, newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
        if reader:
            lines = [f"{att['datetime']} - {att['status']} - QR: {att['qr_code']}" for att in reader[-10:]]
            message = "📜 آخر 10 حضور:\n" + "\n".join(lines)
        else:
            message = "لا يوجد سجل حضور."
    except FileNotFoundError:
        message = "لا يوجد سجل حضور."
    await update.message.reply_text(message)

async def attendance_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(ATTENDANCE_FILE, newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
        total = len(reader)
        today = sum(1 for att in reader if datetime.strptime(att["datetime"], "%Y-%m-%d %H:%M:%S").date() == datetime.now().date())
        last7 = sum(1 for att in reader if datetime.strptime(att["datetime"], "%Y-%m-%d %H:%M:%S") >= datetime.now() - timedelta(days=7))
        message = f"📊 إحصائيات الحضور:\nإجمالي الحضور: {total}\nالحضور اليوم: {today}\nالحضور آخر 7 أيام: {last7}"
    except FileNotFoundError:
        message = "لا يوجد سجل حضور."
    await update.message.reply_text(message)

# ---------------------------
# تشغيل البوت
# ---------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("attendance", last_attendance))
    app.add_handler(CommandHandler("history", attendance_history))
    app.add_handler(CommandHandler("stats", attendance_stats))
    print("🤖 Telegram bot with QR ready...")
    app.run_polling()
