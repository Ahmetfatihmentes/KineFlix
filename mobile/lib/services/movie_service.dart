import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../core/constants.dart';
import '../models/movie.dart';
import 'auth_service.dart';

class MovieService {
  static Future<Map<String, String>> _headers() async {
    final token = await AuthService.getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  static Future<List<Movie>> searchMovies(
    String query, {
    String? contentType,
  }) async {
    final headers = await _headers();
    var url =
        '${AppConstants.baseUrl}/movies/search?query=${Uri.encodeComponent(query)}';
    if (contentType != null) {
      url += '&content_type=${Uri.encodeComponent(contentType)}';
    }

    try {
      final res = await http.get(Uri.parse(url), headers: headers);
      if (res.statusCode == 200) {
        final List data = jsonDecode(utf8.decode(res.bodyBytes));
        return data.map((e) => Movie.fromJson(e)).toList();
      }
    } catch (e) {
      debugPrint('MovieService.searchMovies hatası: $e');
    }
    return [];
  }

  static Future<Movie?> getMovieDetail(int id) async {
    final headers = await _headers();
    try {
      final res = await http.get(
        Uri.parse('${AppConstants.baseUrl}/movies/$id'),
        headers: headers,
      );
      if (res.statusCode == 200) {
        return Movie.fromJson(jsonDecode(utf8.decode(res.bodyBytes)));
      }
    } catch (e) {
      debugPrint('MovieService.getMovieDetail hatası: $e');
    }
    return null;
  }

  static Future<List<Movie>> getRecommendations(int movieId) async {
    final headers = await _headers();
    try {
      final res = await http.get(
        Uri.parse('${AppConstants.baseUrl}/movies/$movieId/recommendations'),
        headers: headers,
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(utf8.decode(res.bodyBytes));
        if (data is List) {
          return data.map((e) => Movie.fromJson(e)).toList();
        }
        if (data is Map && data['status'] == 'loading') {
          return [];
        }
      }
    } catch (e) {
      debugPrint('MovieService.getRecommendations hatası: $e');
    }
    return [];
  }

  static Future<String?> getRecommendationReason(
    int sourceId,
    int recommendedId, {
    bool short = false,
  }) async {
    final headers = await _headers();
    try {
      final res = await http.get(
        Uri.parse(
          '${AppConstants.baseUrl}/movies/$sourceId/recommendation-reason'
          '?recommended_id=$recommendedId&short=$short',
        ),
        headers: headers,
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(utf8.decode(res.bodyBytes));
        return data['reason'];
      }
    } catch (e) {
      debugPrint('MovieService.getRecommendationReason hatası: $e');
    }
    return null;
  }

  static Future<Map<String, dynamic>?> getAiReview(int movieId) async {
    final headers = await _headers();
    try {
      final res = await http.get(
        Uri.parse('${AppConstants.baseUrl}/movies/$movieId/ai-review'),
        headers: headers,
      );
      if (res.statusCode == 200) {
        return jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
      }
    } catch (e) {
      debugPrint('MovieService.getAiReview hatası: $e');
    }
    return null;
  }

  static Future<List<Movie>> getWatchlist() async {
    final headers = await _headers();
    try {
      final res = await http.get(
        Uri.parse('${AppConstants.baseUrl}/watchlist/'),
        headers: headers,
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(utf8.decode(res.bodyBytes));
        if (data is List) {
          return data.map((e) => Movie.fromJson(e)).toList();
        }
      }
    } catch (e) {
      debugPrint('MovieService.getWatchlist hatası: $e');
    }
    return [];
  }

  static Future<List<Movie>> getWatchHistory() async {
    final headers = await _headers();
    try {
      final res = await http.get(
        Uri.parse('${AppConstants.baseUrl}/watch-history/'),
        headers: headers,
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(utf8.decode(res.bodyBytes));
        if (data is List) {
          return data.map((e) => Movie.fromJson(e)).toList();
        }
      }
    } catch (e) {
      debugPrint('MovieService.getWatchHistory hatası: $e');
    }
    return [];
  }

  static Future<bool> addToWatchlist(int movieId) async {
    final headers = await _headers();
    try {
      final res = await http.post(
        Uri.parse('${AppConstants.baseUrl}/watchlist/'),
        headers: headers,
        body: jsonEncode({'movie_id': movieId}),
      );
      return res.statusCode == 201 || res.statusCode == 200;
    } catch (e) {
      debugPrint('MovieService.addToWatchlist hatası: $e');
      return false;
    }
  }

  static Future<bool> removeFromWatchlist(int movieId) async {
    final headers = await _headers();
    try {
      final res = await http.delete(
        Uri.parse('${AppConstants.baseUrl}/watchlist/$movieId'),
        headers: headers,
      );
      return res.statusCode == 200;
    } catch (e) {
      debugPrint('MovieService.removeFromWatchlist hatası: $e');
      return false;
    }
  }

  static Future<bool> addToWatchHistory(int movieId) async {
    final headers = await _headers();
    try {
      final res = await http.post(
        Uri.parse('${AppConstants.baseUrl}/watch-history/'),
        headers: headers,
        body: jsonEncode({'movie_id': movieId}),
      );
      return res.statusCode == 201 || res.statusCode == 200;
    } catch (e) {
      debugPrint('MovieService.addToWatchHistory hatası: $e');
      return false;
    }
  }

  static Future<Map<String, dynamic>?> getPersonalizedRecommendation() async {
    final headers = await _headers();
    try {
      final res = await http.get(
        Uri.parse('${AppConstants.baseUrl}/recommendations/personalized'),
        headers: headers,
      );
      if (res.statusCode == 200) {
        return jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
      }
    } catch (e) {
      debugPrint('MovieService.getPersonalizedRecommendation hatası: $e');
    }
    return null;
  }

  static Future<String?> getTrailer(int movieId) async {
    final headers = await _headers();
    try {
      final res = await http.get(
        Uri.parse('${AppConstants.baseUrl}/movies/$movieId/trailer'),
        headers: headers,
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(utf8.decode(res.bodyBytes));
        return data['youtube_url'] as String?;
      }
    } catch (e) {
      debugPrint('MovieService.getTrailer hatası: $e');
    }
    return null;
  }

  static Future<List<Map<String, dynamic>>> getReviews(int movieId) async {
    final headers = await _headers();
    try {
      final res = await http.get(
        Uri.parse('${AppConstants.baseUrl}/movies/$movieId/reviews'),
        headers: headers,
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(utf8.decode(res.bodyBytes));
        if (data is List) {
          return List<Map<String, dynamic>>.from(data);
        }
      }
    } catch (e) {
      debugPrint('MovieService.getReviews hatası: $e');
    }
    return [];
  }
}
