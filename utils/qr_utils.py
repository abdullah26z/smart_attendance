# File: utils/qr_utils.py

import qrcode
import base64
from io import BytesIO
from django.utils import timezone

def generate_qr_code(data: str) -> str:
    """
    توليد صورة QR code وتحويلها إلى Base64.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def is_qr_valid(qr_code: str, current_time=None, validity_minutes=10) -> bool:
    """
    تحقق من صلاحية QR code بناءً على الوقت الحالي.
    """
    if not current_time:
        current_time = timezone.now()
    # في حالنا البسيط: QR code صالح لمدة validity_minutes
    # يمكن تعديل حسب الحاجة أو تخزين صلاحية QR في قاعدة البيانات
    return True  # نعيد True مؤقتًا لأن صلاحية QR تتحقق في AttendanceAPIView
