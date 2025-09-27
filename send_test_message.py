import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8265770793:AAFl2Riw0294kAh0CAW5oc0wfE986leQnFw")
CHAT_ID = "883270785"

resp = requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": "✅ اختبار ناجح من نظام الحضور!"}
)

print(resp.json())
