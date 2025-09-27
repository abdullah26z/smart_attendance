import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_telegram_message(chat_id, text):
    """إرسال رسالة إلى مستخدم على تليجرام"""
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return None

def get_updates(offset=None):
    """جلب التحديثات من البوت (للتعامل مع رسائل /start)"""
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 10, "offset": offset}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return None
