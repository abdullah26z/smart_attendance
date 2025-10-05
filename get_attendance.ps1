# File: attendance.ps1

# إعدادات المستخدم
$email = "3booody.om@gmail.com"
$password = "3B00dy_26"
$api_base = "http://127.0.0.1:8000/api"

$headers = @{ "Content-Type" = "application/json" }

# تسجيل الدخول للحصول على access token
$body = "{ `"email`": `"$email`", `"password`": `"$password`" }"
$response = Invoke-RestMethod -Uri "$api_base/login/" -Method POST -Headers $headers -Body $body
$token = $response.access
$user_role = $response.user.role
$headers_auth = @{ "Authorization" = "Bearer $token" }

function Show-StudentAttendance {
    param($headers_auth)
    $response_history = Invoke-RestMethod -Uri "$api_base/attendance/history/" -Method GET -Headers $headers_auth
    $sorted_history = $response_history | Sort-Object -Property timestamp -Descending
    $sorted_history | Format-Table `
        @{Name="Email";Expression={if ($_.user.email) {$_.user.email} else {"-"}}} ,
        @{Name="Lecture";Expression={if ($_.lecture -is [string]) {$_.lecture} elseif ($_.lecture.title) {$_.lecture.title} else {"-"}}} ,
        @{Name="Status";Expression={$_.status}} ,
        @{Name="Time";Expression={$_.timestamp}} -AutoSize
}

function Show-LecturerAttendance {
    param($headers_auth)
    $response_lectures = Invoke-RestMethod -Uri "$api_base/attendance/all_lectures/" -Method GET -Headers $headers_auth
    foreach ($lecture in $response_lectures | Sort-Object start_time -Descending) {
        $title = if ($lecture.title) { $lecture.title } else { "-" }
        $start_time = if ($lecture.start_time) { $lecture.start_time } else { "-" }
        $qr_expires_at = if ($lecture.qr_expires_at) { $lecture.qr_expires_at } else { "-" }
        Write-Host "`n🎓 Lecture: $title  |  Start: $start_time  |  QR expires: $qr_expires_at"
        Write-Host "---------------------------------------------------------"
        if (-not $lecture.PSObject.Properties.Match("attendances") -or $lecture.attendances.Count -eq 0) {
            Write-Host "⚠️ No attendance recorded yet."
        } else {
            $lecture.attendances | Sort-Object timestamp -Descending | Format-Table `
                @{Name="Student Email";Expression={if ($_.user.email) {$_.user.email} else {"-"}}}, `
                @{Name="Status";Expression={$_.status}}, `
                @{Name="Time";Expression={$_.timestamp}} -AutoSize
        }
    }
}

if ($user_role -eq "student") {
    Show-StudentAttendance -headers_auth $headers_auth
} elseif ($user_role -eq "lecturer") {
    Show-LecturerAttendance -headers_auth $headers_auth
} else {
    Write-Host "⚠️ Role not supported for this script: $user_role"
}
