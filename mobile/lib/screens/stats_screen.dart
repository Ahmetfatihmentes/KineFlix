import 'package:flutter/material.dart';

import '../core/theme.dart';
import '../models/movie.dart';
import '../services/auth_service.dart';
import '../services/movie_service.dart';
import '../widgets/film_grain.dart';

const Map<String, String> _kGenreMap = {
  'Action': 'Aksiyon',
  'Adventure': 'Macera',
  'Animation': 'Animasyon',
  'Comedy': 'Komedi',
  'Crime': 'Suç',
  'Documentary': 'Belgesel',
  'Drama': 'Dram',
  'Fantasy': 'Fantastik',
  'Horror': 'Korku',
  'Music': 'Müzik',
  'Mystery': 'Gizem',
  'Romance': 'Romantik',
  'Science Fiction': 'Bilim Kurgu',
  'Thriller': 'Gerilim',
  'War': 'Savaş',
  'Family': 'Aile',
  'Crime TV Shows': 'Suç Dizisi',
  'TV Dramas': 'Drama Dizisi',
  'TV Thrillers': 'Gerilim Dizisi',
  'TV Comedies': 'Komedi Dizisi',
  'International TV Shows': 'Uluslararası Dizi',
  'Anime Series': 'Anime',
  'Reality TV': 'Gerçeklik TV',
};

class StatsScreen extends StatefulWidget {
  const StatsScreen({super.key});

  @override
  State<StatsScreen> createState() => _StatsScreenState();
}

class _StatsScreenState extends State<StatsScreen> {
  Map<String, dynamic>? _user;
  List<Movie> _history = [];
  List<Movie> _watchlist = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final results = await Future.wait([
        AuthService.getMe(),
        MovieService.getWatchHistory(),
        MovieService.getWatchlist(),
      ]);
      if (!mounted) return;
      setState(() {
        _user = results[0] as Map<String, dynamic>?;
        _history = results[1] as List<Movie>;
        _watchlist = results[2] as List<Movie>;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _error = 'İstatistikler yüklenemedi.';
        _loading = false;
      });
    }
  }

  List<MapEntry<String, int>> _topGenres() {
    final counts = <String, int>{};
    for (final movie in _history) {
      final genres = movie.genres?.split(',') ?? [];
      for (final g in genres) {
        final genre = g.trim();
        if (genre.isNotEmpty) {
          counts[genre] = (counts[genre] ?? 0) + 1;
        }
      }
    }
    final sorted = counts.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    return sorted.take(6).toList();
  }

  int _uniqueGenreCount() {
    final genres = <String>{};
    for (final movie in _history) {
      final parts = movie.genres?.split(',') ?? [];
      for (final g in parts) {
        final genre = g.trim();
        if (genre.isNotEmpty) genres.add(genre);
      }
    }
    return genres.length;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text(
          'İSTATİSTİKLERİM',
          style: AppTheme.displayTitle(size: 22),
        ),
        backgroundColor: AppTheme.background,
        foregroundColor: AppTheme.primary,
        elevation: 0,
      ),
      body: Stack(
        children: [
          const FilmGrain(),
          _buildBody(),
        ],
      ),
    );
  }

  Widget _buildBody() {
    if (_loading) {
      return const Center(
        child: CircularProgressIndicator(color: AppTheme.primary),
      );
    }

    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                _error!,
                style: const TextStyle(color: AppTheme.error),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              TextButton(
                onPressed: _load,
                child: const Text(
                  'Tekrar Dene',
                  style: TextStyle(color: AppTheme.primary),
                ),
              ),
            ],
          ),
        ),
      );
    }

    final email = _user?['email'] as String? ?? '';
    final initial = email.isNotEmpty ? email[0].toUpperCase() : '?';
    final topGenres = _topGenres();
    final maxCount = topGenres.isNotEmpty ? topGenres.first.value : 1;

    return RefreshIndicator(
      color: AppTheme.primary,
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _buildAvatar(initial, email),
          const SizedBox(height: 28),
          _buildStatBoxes(),
          const SizedBox(height: 32),
          _buildSectionTitle('FAVORİ TÜRLER'),
          const SizedBox(height: 16),
          if (topGenres.isEmpty)
            const Padding(
              padding: EdgeInsets.only(bottom: 16),
              child: Text(
                'Henüz yeterli veri yok.',
                style: TextStyle(color: AppTheme.onSurfaceVariant),
              ),
            )
          else
            ...topGenres.map((entry) => _buildGenreBar(
                  entry.key,
                  entry.value / maxCount,
                  entry.value,
                )),
          const SizedBox(height: 8),
        ],
      ),
    );
  }

  Widget _buildAvatar(String initial, String email) {
    return Row(
      children: [
        CircleAvatar(
          radius: 36,
          backgroundColor: AppTheme.primary,
          child: Text(
            initial,
            style: const TextStyle(
              color: AppTheme.onPrimary,
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Text(
            email,
            style: const TextStyle(
              color: AppTheme.onSurface,
              fontSize: 15,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }

  Widget _buildStatBoxes() {
    return Row(
      children: [
        _statBox('${_history.length}', 'Film\nİzlendi'),
        _statBox('${_watchlist.length}', 'Listede'),
        _statBox('${_uniqueGenreCount()}', 'Tür\nKeşfedildi'),
      ],
    );
  }

  Widget _statBox(String value, String label) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 4),
        padding: const EdgeInsets.symmetric(vertical: 18),
        decoration: BoxDecoration(
          color: AppTheme.surfaceContainer,
          border: Border.all(
            color: AppTheme.outlineVariant.withValues(alpha: 0.5),
          ),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Text(
              value,
              style: const TextStyle(
                color: AppTheme.primary,
                fontSize: 26,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              label,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: AppTheme.onSurfaceVariant,
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Row(
      children: [
        Text(title, style: AppTheme.headlineTitle(size: 20)),
        const SizedBox(width: 12),
        const Expanded(
          child: Divider(color: AppTheme.outlineVariant, thickness: 0.5),
        ),
      ],
    );
  }

  Widget _buildGenreBar(String genre, double fraction, int count) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                (_kGenreMap[genre.trim()] ?? genre.trim()).toUpperCase(),
                style: const TextStyle(
                  color: AppTheme.onSurfaceVariant,
                  fontSize: 12,
                  letterSpacing: 0.5,
                ),
              ),
              Text(
                '$count film',
                style: const TextStyle(
                  color: AppTheme.primary,
                  fontSize: 12,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: fraction,
              minHeight: 8,
              backgroundColor:
                  AppTheme.outlineVariant.withValues(alpha: 0.3),
              valueColor:
                  const AlwaysStoppedAnimation<Color>(AppTheme.primary),
            ),
          ),
        ],
      ),
    );
  }
}
