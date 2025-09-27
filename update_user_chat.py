# File: update_user_chat.py
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from accounts.models import User

def set_chat(email, chat_id):
    try:
        user = User.objects.get(email=email)
        user.telegram_chat_id = str(chat_id)
        user.save()
        print(f"✅ Set telegram_chat_id for {email} = {chat_id}")
    except User.DoesNotExist:
        print("❌ User not found:", email)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python update_user_chat.py user_email chat_id")
        sys.exit(1)
    set_chat(sys.argv[1], sys.argv[2])
