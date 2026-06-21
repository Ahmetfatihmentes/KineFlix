import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../core/theme.dart';
import '../models/movie.dart';
import '../services/auth_service.dart';
import '../services/movie_service.dart';
import '../widgets/bottom_nav.dart';
import '../widgets/custom_button.dart';
import '../widgets/film_grain.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _user;
  List<Movie> _history = [];
  List<Movie> _watchlist = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);

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
  }

  Map<String, int> _genreCounts() {
    final counts = <String, int>{};
    for (final movie in _history) {
      final genre = movie.displayGenre;
      if (genre.isNotEmpty) {
        counts[genre] = (counts[genre] ?? 0) + 1;
      }
    }
    return counts;
  }

  Future<void> _logout() async {
    await AuthService.logout();
    if (mounted) context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    final email = _user?['email'] as String? ??
        '';
    final initial = email.isNotEmpty ? email[0].toUpperCase() : '?';
    final genreCounts = _genreCounts();
    final topGenres = genreCounts.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return Scaffold(
      backgroundColor: AppTheme.background,
      bottomNavigationBar: const KineFlixBottomNav(currentIndex: 3),
      body: Stack(
        children: [
          const FilmGrain(),
          SafeArea(
            child: _loading
                ? const Center(
                    child: CircularProgressIndicator(color: AppTheme.primary),
                  )
                : ListView(
                    padding: const EdgeInsets.all(20),
                    children: [
                      Text('Profil', style: AppTheme.displayTitle(size: 40)),
                      const SizedBox(height: 24),
                      Row(
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
                                fontSize: 16,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 28),
                      Row(
                        children: [
                          _stat('${_history.length}', 'Film İzlendi'),
                          _stat('${_watchlist.length}', 'Listede'),
                          _stat('${topGenres.length}', 'Tür Keşfedildi'),
                        ],
                      ),
                      const SizedBox(height: 28),
                      Text(
                        'FAVORİ TÜRLER',
                        style: AppTheme.headlineTitle(size: 22),
                      ),
                      const SizedBox(height: 12),
                      if (topGenres.isEmpty)
                        const Text(
                          'Henüz yeterli veri yok',
                          style: TextStyle(color: AppTheme.onSurfaceVariant),
                        )
                      else
                        ...topGenres.take(5).map((entry) {
                          final max = topGenres.first.value;
                          final width = entry.value / max;
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 10),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  entry.key,
                                  style: const TextStyle(
                                    color: AppTheme.onSurfaceVariant,
                                    fontSize: 12,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                FractionallySizedBox(
                                  widthFactor: width,
                                  child: Container(
                                    height: 8,
                                    decoration: BoxDecoration(
                                      color: AppTheme.primary,
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          );
                        }),
                      const SizedBox(height: 24),
                      GhostButton(
                        label: 'Geçmişi Gör',
                        icon: Icons.history,
                        onPressed: () => context.push('/history'),
                      ),
                      const SizedBox(height: 16),
                      PrimaryButton(
                        label: 'Çıkış Yap',
                        icon: Icons.logout,
                        onPressed: _logout,
                      ),
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  Widget _stat(String value, String label) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 4),
        padding: const EdgeInsets.symmetric(vertical: 16),
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
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
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
}
