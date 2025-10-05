import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:qr_flutter/qr_flutter.dart';

// ---------------- CONFIG ----------------
final String apiUrl = 'http://10.0.2.2:8000/api/';

void main() {
  runApp(const SmartAttendanceApp());
}

// ---------------- APP ----------------
class SmartAttendanceApp extends StatefulWidget {
  const SmartAttendanceApp({super.key});
  @override
  _SmartAttendanceAppState createState() => _SmartAttendanceAppState();
}

class _SmartAttendanceAppState extends State<SmartAttendanceApp> {
  ThemeMode _themeMode = ThemeMode.dark;
  Locale _locale = const Locale('en');

  void toggleTheme() {
    setState(() {
      _themeMode =
          _themeMode == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
    });
  }

  void switchLocale() {
    setState(() {
      _locale = _locale.languageCode == 'en' ? const Locale('ar') : const Locale('en');
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Attendance',
      themeMode: _themeMode,
      theme: ThemeData.light()
          .copyWith(primaryColor: Colors.indigo, scaffoldBackgroundColor: Colors.grey[100]),
      darkTheme: ThemeData.dark()
          .copyWith(primaryColor: Colors.indigo, scaffoldBackgroundColor: Colors.black),
      locale: _locale,
      home: LaunchPage(toggleTheme: toggleTheme, switchLocale: switchLocale),
      debugShowCheckedModeBanner: false,
    );
  }
}

// ---------------- LAUNCH PAGE ----------------
class LaunchPage extends StatefulWidget {
  final VoidCallback toggleTheme;
  final VoidCallback switchLocale;
  const LaunchPage({super.key, required this.toggleTheme, required this.switchLocale});
  @override
  _LaunchPageState createState() => _LaunchPageState();
}

class _LaunchPageState extends State<LaunchPage> {
  String? _token;
  Map<String, dynamic>? _user;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadSession();
  }

  Future<void> _loadSession() async {
    final prefs = await SharedPreferences.getInstance();
    final t = prefs.getString('access');
    final u = prefs.getString('user');
    setState(() {
      _token = t;
      _user = u != null ? jsonDecode(u) : null;
      _loading = false;
    });
  }

  void _onLogin(Map<String, dynamic> user, String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access', token);
    await prefs.setString('user', jsonEncode(user));
    setState(() {
      _token = token;
      _user = user;
    });
  }

  void _onLogout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access');
    await prefs.remove('user');
    setState(() {
      _token = null;
      _user = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (_token == null || _user == null) {
      return LoginRegisterPage(
          onLogin: _onLogin, toggleTheme: widget.toggleTheme, switchLocale: widget.switchLocale);
    } else {
      final role = _user!['role'] ?? 'student';
      if (role == 'lecturer' || role == 'admin') {
        return LecturerHome(
            token: _token!,
            user: _user!,
            onLogout: _onLogout,
            toggleTheme: widget.toggleTheme,
            switchLocale: widget.switchLocale);
      } else {
        return StudentHome(
            token: _token!,
            user: _user!,
            onLogout: _onLogout,
            toggleTheme: widget.toggleTheme,
            switchLocale: widget.switchLocale);
      }
    }
  }
}

// ---------------- LOGIN / REGISTER ----------------
class LoginRegisterPage extends StatefulWidget {
  final Function(Map<String, dynamic>, String) onLogin;
  final VoidCallback toggleTheme;
  final VoidCallback switchLocale;
  const LoginRegisterPage(
      {super.key, required this.onLogin, required this.toggleTheme, required this.switchLocale});
  @override
  _LoginRegisterPageState createState() => _LoginRegisterPageState();
}

class _LoginRegisterPageState extends State<LoginRegisterPage> {
  bool _isRegister = false;
  bool _loading = false;
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _fullname = TextEditingController();
  String _role = 'student';

  void _showMsg(String msg) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));

  Future<void> _login() async {
    setState(() => _loading = true);
    try {
      final url = Uri.parse('${apiUrl}login/');
      final resp = await http.post(url,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'email': _email.text.trim(), 'password': _password.text.trim()}));
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        final token = data['access'] ?? '';
        final user = data['user'] ?? {};
        widget.onLogin(user, token);
        _showMsg('Logged in');
      } else {
        final body = jsonDecode(resp.body);
        final err = body['non_field_errors'] != null ? body['non_field_errors'][0] : resp.body;
        _showMsg('Login failed: $err');
      }
    } catch (e) {
      _showMsg('Error: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _register() async {
    setState(() => _loading = true);
    try {
      final url = Uri.parse('${apiUrl}register/');
      final resp = await http.post(url,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'email': _email.text.trim(),
            'password': _password.text.trim(),
            'full_name': _fullname.text.trim(),
            'role': _role,
          }));
      if (resp.statusCode == 201) {
        _showMsg('Registered. Now login.');
        setState(() {
          _isRegister = false;
        });
      } else {
        final body = jsonDecode(resp.body);
        _showMsg('Register failed: ${body.toString()}');
      }
    } catch (e) {
      _showMsg('Error: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Smart Attendance'),
        actions: [
          IconButton(icon: Icon(isDark ? Icons.wb_sunny : Icons.nightlight_round), onPressed: widget.toggleTheme),
          IconButton(icon: const Icon(Icons.language), onPressed: widget.switchLocale),
        ],
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  if (_isRegister)
                    TextField(controller: _fullname, decoration: const InputDecoration(labelText: 'Full name')),
                  TextField(controller: _email, decoration: const InputDecoration(labelText: 'Email')),
                  const SizedBox(height: 8),
                  TextField(controller: _password, decoration: const InputDecoration(labelText: 'Password'), obscureText: true),
                  const SizedBox(height: 12),
                  if (_isRegister)
                    Row(children: [
                      const Text('Role:'),
                      const SizedBox(width: 12),
                      DropdownButton<String>(
                        value: _role,
                        items: const [
                          DropdownMenuItem(child: Text('Student'), value: 'student'),
                          DropdownMenuItem(child: Text('Lecturer'), value: 'lecturer'),
                        ],
                        onChanged: (v) => setState(() => _role = v ?? 'student'),
                      )
                    ]),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _loading ? null : (_isRegister ? _register : _login),
                    child: _loading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : Text(_isRegister ? 'Register' : 'Login'),
                  ),
                  TextButton(
                    onPressed: () => setState(() => _isRegister = !_isRegister),
                    child: Text(_isRegister ? 'Have an account? Login' : 'Create account'),
                  )
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ---------------- Lecturer Home ----------------
class LecturerHome extends StatefulWidget {
  final String token;
  final Map<String, dynamic> user;
  final VoidCallback onLogout;
  final VoidCallback toggleTheme;
  final VoidCallback switchLocale;

  const LecturerHome({
    super.key,
    required this.token,
    required this.user,
    required this.onLogout,
    required this.toggleTheme,
    required this.switchLocale,
  });

  @override
  _LecturerHomeState createState() => _LecturerHomeState();
}

class _LecturerHomeState extends State<LecturerHome> {
  List<dynamic> _lectures = [];
  bool _loading = true;
  final _lectureName = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchLectures();
  }

  Future<void> _fetchLectures() async {
    setState(() => _loading = true);
    try {
      final url = Uri.parse('http://10.0.2.2:8000/api/attendance/lecture_qr/');
      final resp = await http.get(url, headers: {'Authorization': 'Bearer ${widget.token}'});
      if (resp.statusCode == 200) {
        setState(() {
          _lectures = jsonDecode(resp.body);
        });
      }
    } catch (e) {
      print('Error fetching lectures: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _createLecture() async {
    if (_lectureName.text.trim().isEmpty) return;
    setState(() => _loading = true);
    try {
      final url = Uri.parse('http://10.0.2.2:8000/api/attendance/lecture_qr/');
      final resp = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${widget.token}'
        },
        body: jsonEncode({'name': _lectureName.text.trim(), 'start_time': DateTime.now().toIso8601String(), 'end_time': DateTime.now().add(const Duration(hours: 2)).toIso8601String()}),
      );
      if (resp.statusCode == 201) {
        _lectureName.clear();
        _fetchLectures();
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Lecture created')));
      } else {
        final body = jsonDecode(resp.body);
        _showMsg('Create failed: $body');
      }
    } catch (e) {
      _showMsg('Error: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  void _showMsg(String msg) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));

  void _showQRCode(String qrCode, String lectureName) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ShowQrPage(payload: qrCode, title: 'QR - $lectureName'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Lecturer Dashboard'),
        actions: [
          IconButton(icon: const Icon(Icons.logout), onPressed: widget.onLogout),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _fetchLectures,
              child: ListView(
                padding: const EdgeInsets.all(12),
                children: [
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: [
                          Expanded(
                            child: TextField(
                              controller: _lectureName,
                              decoration: const InputDecoration(labelText: 'Lecture Name'),
                            ),
                          ),
                          IconButton(icon: const Icon(Icons.add), onPressed: _createLecture)
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  ..._lectures.map((lecture) {
                    final qr = lecture['qr_code'] ?? '';
                    final code = lecture['referral_code'] ?? '';
                    final name = lecture['name'] ?? 'Lecture';
                    return Card(
                      child: ListTile(
                        title: Text(name),
                        subtitle: Text('Referral code: $code'),
                        trailing: IconButton(
                          icon: const Icon(Icons.qr_code),
                          onPressed: () => _showQRCode(qr, name),
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),
    );
  }
}

// ---------------- QR Show Page ----------------
class ShowQrPage extends StatelessWidget {
  final String payload;
  final String title;
  const ShowQrPage({super.key, required this.payload, required this.title});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: Center(
        child: QrImageView(
          data: payload,
          version: QrVersions.auto,
          size: 260.0,
        ),
      ),
    );
  }
}

// ---------------- Student Home ----------------
class StudentHome extends StatefulWidget {
  final String token;
  final Map<String, dynamic> user;
  final VoidCallback onLogout;
  final VoidCallback toggleTheme;
  final VoidCallback switchLocale;

  const StudentHome({
    super.key,
    required this.token,
    required this.user,
    required this.onLogout,
    required this.toggleTheme,
    required this.switchLocale,
  });

  @override
  _StudentHomeState createState() => _StudentHomeState();
}

class _StudentHomeState extends State<StudentHome> {
  List<dynamic> _courses = [];
  List<dynamic> _attendance = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchCoursesAndAttendance();
  }

  Future<void> _fetchCoursesAndAttendance() async {
    setState(() => _loading = true);
    try {
      final cResp = await http.get(
        Uri.parse('$apiUrl/student/courses/'),
        headers: {'Authorization': 'Bearer ${widget.token}'},
      );
      final aResp = await http.get(
        Uri.parse('$apiUrl/attendance/history/'),
        headers: {'Authorization': 'Bearer ${widget.token}'},
      );

      if (cResp.statusCode == 200) _courses = jsonDecode(cResp.body);
      if (aResp.statusCode == 200) _attendance = jsonDecode(aResp.body);
    } catch (e) {
      print('Error fetching data: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  void _showMsg(String msg) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));

  void _scanQRCode() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => QRScanPage(token: widget.token)),
    );
  }

  Future<void> _markAttendanceForCourse(String qrCode) async {
    try {
      final resp = await http.post(
        Uri.parse('$apiUrl/attendance/mark/'),
        headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ${widget.token}'},
        body: jsonEncode({'qr_code': qrCode}),
      );

      if (resp.statusCode == 201 || resp.statusCode == 200) {
        _showMsg('Attendance marked');
        _fetchCoursesAndAttendance();
      } else {
        final body = jsonDecode(resp.body);
        _showMsg('Failed: ${body.toString()}');
      }
    } catch (e) {
      _showMsg('Error: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Student Dashboard'),
        actions: [
          IconButton(icon: const Icon(Icons.language), onPressed: widget.switchLocale),
          IconButton(
            icon: Icon(Theme.of(context).brightness == Brightness.dark
                ? Icons.wb_sunny
                : Icons.nightlight_round),
            onPressed: widget.toggleTheme,
          ),
          IconButton(icon: const Icon(Icons.logout), onPressed: widget.onLogout),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _scanQRCode,
        icon: const Icon(Icons.qr_code_scanner),
        label: const Text('Scan QR'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _fetchCoursesAndAttendance,
              child: ListView(
                padding: const EdgeInsets.all(12),
                children: [
                  Card(
                    child: ListTile(
                      title: Text(widget.user['full_name'] ?? widget.user['email'] ?? 'You'),
                      subtitle: Text('Role: ${widget.user['role'] ?? 'student'}'),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text('My Courses', style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 8),
                  ..._courses.map((course) => Card(
                        child: ListTile(
                          title: Text(course['name'] ?? 'Course'),
                          subtitle: Text('Referral: ${course['referral_code'] ?? '-'}'),
                          trailing: IconButton(
                            icon: const Icon(Icons.qr_code),
                            onPressed: () => _markAttendanceForCourse(course['qr_code'] ?? ''),
                          ),
                        ),
                      )),
                  const SizedBox(height: 12),
                  Text('Attendance History', style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 8),
                  ..._attendance.map((a) => ListTile(
                        title: Text(a['course_name'] ?? ''),
                        subtitle: Text(a['timestamp'] ?? ''),
                        trailing: Text(a['status'] ?? 'present'),
                      )),
                ],
              ),
            ),
    );
  }
}

// ---------------- QR Scan Page ----------------
class QRScanPage extends StatefulWidget {
  final String token;
  const QRScanPage({super.key, required this.token});
  
  @override
  _QRScanPageState createState() => _QRScanPageState();
}
  
class _QRScanPageState extends State<QRScanPage> {
  final MobileScannerController cameraController = MobileScannerController();
  bool _processing = false;
  
  void _showMsg(String msg) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));

  Future<void> _markAttendance(String qrCode) async {
    if (_processing) return;
    setState(() => _processing = true);
    try {
      final url = Uri.parse('http://10.0.2.2:8000/api/attendance/mark/');
      final resp = await http.post(
        url,
        headers: {
          'Authorization': 'Bearer ${widget.token}',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'qr_code': qrCode}),
      );
      if (resp.statusCode == 201 || resp.statusCode == 200) {
        _showMsg('Attendance marked!');
        Navigator.pop(context);
      } else {
        final body = jsonDecode(resp.body);
        _showMsg('Failed: $body');
      }
    } catch (e) {
      _showMsg('Error: $e');
    } finally {
      setState(() => _processing = false);
    }
  }
    
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan QR to Mark Attendance')),
      body: MobileScanner(
        controller: cameraController,
        onDetect: (capture) {
          for (final barcode in capture.barcodes) {
            final raw = barcode.rawValue;
            if (raw != null) _markAttendance(raw);
          }
        },
      ),
    );
  }
    
  @override
  void dispose() {
    cameraController.dispose();
    super.dispose();
  }
}