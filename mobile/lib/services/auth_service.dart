import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../core/constants.dart';

class AuthService {
  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('${AppConstants.baseUrl}/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(AppConstants.tokenKey, data['access_token']);
        await prefs.setString(AppConstants.userEmailKey, data['email'] ?? email);
        await prefs.setInt(AppConstants.userIdKey, data['user_id'] ?? 0);
        return {'success': true};
      }

      final error = jsonDecode(utf8.decode(response.bodyBytes));
      return {
        'success': false,
        'message': error['detail'] ?? 'Giriş başarısız',
      };
    } catch (_) {
      return {
        'success': false,
        'message': 'Bağlantı hatası. Backend çalışıyor mu?',
      };
    }
  }

  static Future<Map<String, dynamic>> register(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('${AppConstants.baseUrl}/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return {'success': true};
      }

      final error = jsonDecode(utf8.decode(response.bodyBytes));
      return {
        'success': false,
        'message': error['detail'] ?? 'Kayıt başarısız',
      };
    } catch (_) {
      return {'success': false, 'message': 'Bağlantı hatası'};
    }
  }

  static Future<Map<String, dynamic>?> getMe() async {
    final headers = await _headers();
    try {
      final res = await http.get(
        Uri.parse('${AppConstants.baseUrl}/auth/me'),
        headers: headers,
      );
      if (res.statusCode == 200) {
        return jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
      }
    } catch (_) {}
    return null;
  }

  static Future<Map<String, String>> _headers() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConstants.tokenKey);
  }

  static Future<String?> getUserEmail() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConstants.userEmailKey);
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  static Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }
}
