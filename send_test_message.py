import os
import requests
from dotenv import load_dotenv

# يحمل القيم من ملف .env إن وُجد
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # لا قيمة افتراضية هنا
CHAT_ID = os.getenv("CHAT_ID", "883270785")   # يمكن ترك chat_id ثابت أو وضعه أيضاً في env

if not TELEGRAM_TOKEN:
    raise SystemExit("ERROR: TELEGRAM_TOKEN not set in environment")

resp = requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": "✅ اختبار ناجح من نظام الحضور!"}
)

print(resp.json())
