import requests

# ---------------------------
# إعدادات السيرفر
# ---------------------------
API_URL = "http://127.0.0.1:8000"

# بيانات الدكتور
DOCTOR_EMAIL = "3booody.om@gmail.com"
DOCTOR_PASSWORD = "3B00dy_26"

# بيانات الطالب (يمكنك إنشاء حساب طالب آخر)
STUDENT_EMAIL = "student@example.com"
STUDENT_PASSWORD = "password123"

# ---------------------------
# دوال تسجيل الدخول
# ---------------------------
def login(email, password):
    url = f"{API_URL}/api/login/"
    data = {"email": email, "password": password}
    resp = requests.post(url, json=data)
    if resp.status_code == 200:
        token = resp.json().get("access")
        print(f"[{email}] Login successful")
        return token
    else:
        print(f"[{email}] Login failed:", resp.text)
        return None

# ---------------------------
# إنشاء محاضرة (Doctor)
# ---------------------------
def create_lecture(token, name, start_time, end_time):
    url = f"{API_URL}/api/attendance/lecture_qr/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": name,
        "start_time": start_time,
        "end_time": end_time
    }
    resp = requests.post(url, json=data, headers=headers)
    if resp.status_code == 201:
        lecture = resp.json().get("lecture")
        print(f"Lecture created: {lecture['name']} (QR: {lecture['qr_code']})")
        return lecture
    else:
        print("Lecture creation failed:", resp.text)
        return None

# ---------------------------
# تسجيل الحضور (Student)
# ---------------------------
def mark_attendance(token, lecture_id):
    url = f"{API_URL}/api/attendance/mark/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "lecture": lecture_id,
        "status": "present"
    }
    resp = requests.post(url, json=data, headers=headers)
    if resp.status_code == 201:
        att = resp.json().get("attendance")
        print(f"Attendance marked for lecture {att['lecture']} at {att['timestamp']}")
    else:
        print("Attendance failed:", resp.text)

# ---------------------------
# تشغيل السكريبت
# ---------------------------
if __name__ == "__main__":
    # تسجيل دخول الدكتور وإنشاء المحاضرة
    doctor_token = login(DOCTOR_EMAIL, DOCTOR_PASSWORD)
    if doctor_token:
        lecture = create_lecture(
            doctor_token,
            name="محاضرة الذكاء الاصطناعي",
            start_time="2025-09-23T10:00:00Z",
            end_time="2025-09-23T12:00:00Z"
        )

        if lecture:
            # تسجيل دخول الطالب وتسجيل حضوره
            student_token = login(STUDENT_EMAIL, STUDENT_PASSWORD)
            if student_token:
                mark_attendance(student_token, lecture_id=lecture['id'])
