# إعدادات المستخدم
$email = "3booody.om@gmail.com"
$password = "3B00dy_26"
$api_base = "http://127.0.0.1:8000/api"

# إعداد headers
$headers = @{ "Content-Type" = "application/json" }

# تسجيل الدخول للحصول على access token
$body = "{ `"email`": `"$email`", `"password`": `"$password`" }"
$response = Invoke-RestMethod -Uri "$api_base/login/" -Method POST -Headers $headers -Body $body
$token = $response.access

# استخدام token لطلب سجل الحضور
$headers_auth = @{ "Authorization" = "Bearer $token" }
$response_history = Invoke-RestMethod -Uri "$api_base/attendance/history/" -Method GET -Headers $headers_auth

# ترتيب حسب timestamp نزولي
$sorted_history = $response_history | Sort-Object -Property timestamp -Descending

# عرض النتائج في جدول مرتب مع ترميز UTF8
$sorted_history | Format-Table @{Name="Email";Expression={$_.user.email}}, 
                              @{Name="Lecture";Expression={if ($_.lecture -is [string]) {$_.lecture} else {$_.lecture.title}}}, 
                              @{Name="Status";Expression={$_.status}}, 
                              @{Name="Time";Expression={$_.timestamp}} -AutoSize
