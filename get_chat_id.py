# File: get_chat_id.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # يقرأ .env في نفس المجلد إذا موجود
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise SystemExit("ERROR: TELEGRAM_TOKEN not set in environment or .env")

BASE = f"https://api.telegram.org/bot{TOKEN}"

def get_updates(offset=None):
    params = {}
    if offset:
        params['offset'] = offset
    r = requests.get(f"{BASE}/getUpdates", params=params, timeout=10)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    data = get_updates()
    results = data.get("result", [])
    if not results:
        print("No updates found. ❗")
        print("→ افتح المحادثة مع البوت في Telegram وأرسل /start ثم شغّل هذا السكربت مرة أخرى.")
    else:
        print(f"Found {len(results)} update(s).")
        for i, u in enumerate(results, 1):
            msg = u.get("message") or u.get("edited_message") or u.get("channel_post")
            if not msg:
                continue
            chat = msg.get("chat", {})
            chat_id = chat.get("id")
            chat_type = chat.get("type")
            first = chat.get("first_name")
            username = chat.get("username")
            print(f"[{i}] chat_id: {chat_id}  type: {chat_type}  name: {first}  username: {username}")
        # آخر chat_id
        last_msg = results[-1].get("message") or results[-1].get("edited_message") or results[-1].get("channel_post")
        last_chat_id = last_msg.get("chat", {}).get("id")
        print("\nUse this chat_id (last):", last_chat_id)
        # طباعة الـ raw JSON مختصر (اختياري)
        # import json; print(json.dumps(data, indent=2, ensure_ascii=False))
