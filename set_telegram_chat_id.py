# File: set_telegram_chat_id.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from accounts.models import User

# ضع هنا chat_id المراد إضافته لكل المستخدمين
DEFAULT_CHAT_ID = "883270785"

def set_chat_id_for_all_users(chat_id=DEFAULT_CHAT_ID, update_existing=False):
    users = User.objects.all()
    for user in users:
        if not user.telegram_chat_id or update_existing:
            user.telegram_chat_id = chat_id
            user.save()
            print(f"✅ Set chat_id to: {user.email}")
        else:
            print(f"⚠️ Already has chat_id and not updated: {user.email}")

if __name__ == "__main__":
    # تغيير update_existing=True لتحديث جميع المستخدمين حتى لو لديهم chat_id
    set_chat_id_for_all_users(update_existing=False)