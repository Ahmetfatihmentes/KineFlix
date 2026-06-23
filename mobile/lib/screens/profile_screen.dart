import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';

import '../core/constants.dart';
import '../core/theme.dart';
import '../models/movie.dart';
import '../services/auth_service.dart';
import '../services/movie_service.dart';
import '../widgets/bottom_nav.dart';
import '../widgets/custom_button.dart';
import '../widgets/film_grain.dart';
import '../widgets/movie_card.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _user;
  List<Movie> _history = [];
  List<Movie> _watchlist = [];
  List<Movie> _likedMovies = [];
  bool _loading = true;
  bool _avatarUploading = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);

    final results = await Future.wait<dynamic>([
      AuthService.getMe(),
      MovieService.getWatchHistory(),
      MovieService.getWatchlist(),
      MovieService.getLikedMovies(),
    ]);

    if (!mounted) return;

    setState(() {
      _user = results[0] as Map<String, dynamic>?;
      _history = results[1] as List<Movie>;
      _watchlist = results[2] as List<Movie>;
      _likedMovies = results[3] as List<Movie>;
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

  Future<void> _handleAvatarUpload() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 80,
      maxWidth: 512,
    );
    if (picked == null || !mounted) return;

    setState(() => _avatarUploading = true);
    final ok = await AuthService.uploadAvatar(picked.path);
    if (!mounted) return;

    if (ok) {
      await _load();
    } else {
      setState(() => _avatarUploading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Fotoğraf yüklenemedi')),
        );
      }
    }
  }

  Future<void> _logout() async {
    await AuthService.logout();
    if (mounted) context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    final email = _user?['email'] as String? ?? '';
    final fullName = _user?['full_name'] as String?;
    final displayName =
        (fullName != null && fullName.isNotEmpty) ? fullName : email;
    final initial = email.isNotEmpty ? email[0].toUpperCase() : '?';
    final avatarUrl = _user?['avatar_url'] as String?;
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
                      // Avatar + isim
                      Row(
                        children: [
                          GestureDetector(
                            onTap: _avatarUploading
                                ? null
                                : _handleAvatarUpload,
                            child: Stack(
                              children: [
                                CircleAvatar(
                                  radius: 36,
                                  backgroundColor: AppTheme.primary,
                                  backgroundImage: avatarUrl != null
                                      ? CachedNetworkImageProvider(
                                          '${AppConstants.baseUrl}$avatarUrl',
                                        )
                                      : null,
                                  child: avatarUrl == null
                                      ? Text(
                                          initial,
                                          style: const TextStyle(
                                            color: AppTheme.onPrimary,
                                            fontSize: 28,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        )
                                      : null,
                                ),
                                Positioned(
                                  bottom: 0,
                                  right: 0,
                                  child: Container(
                                    padding: const EdgeInsets.all(4),
                                    decoration: const BoxDecoration(
                                      color: AppTheme.primary,
                                      shape: BoxShape.circle,
                                    ),
                                    child: _avatarUploading
                                        ? const SizedBox(
                                            width: 10,
                                            height: 10,
                                            child: CircularProgressIndicator(
                                              strokeWidth: 1.5,
                                              color: AppTheme.onPrimary,
                                            ),
                                          )
                                        : const Icon(
                                            Icons.camera_alt,
                                            size: 12,
                                            color: AppTheme.onPrimary,
                                          ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  displayName,
                                  style: const TextStyle(
                                    color: AppTheme.onSurface,
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                if (fullName != null && fullName.isNotEmpty)
                                  Text(
                                    email,
                                    style: const TextStyle(
                                      color: AppTheme.onSurfaceVariant,
                                      fontSize: 13,
                                    ),
                                  ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 28),
                      // İstatistik kartları
                      Row(
                        children: [
                          _stat('${_history.length}', 'Film İzlendi'),
                          _stat('${_watchlist.length}', 'Listede'),
                          _stat('${topGenres.length}', 'Tür Keşfedildi'),
                        ],
                      ),
                      const SizedBox(height: 28),
                      // Favori türler
                      Text(
                        'FAVORİ TÜRLER',
                        style: AppTheme.headlineTitle(size: 22),
                      ),
                      const SizedBox(height: 12),
                      if (topGenres.isEmpty)
                        const Text(
                          'Henüz yeterli veri yok',
                          style:
                              TextStyle(color: AppTheme.onSurfaceVariant),
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
                      // Beğendiklerim
                      if (_likedMovies.isNotEmpty) ...[
                        const SizedBox(height: 28),
                        Text(
                          'BEĞENDİKLERİM',
                          style: AppTheme.headlineTitle(size: 22),
                        ),
                        const SizedBox(height: 12),
                        SizedBox(
                          height: 220,
                          child: ListView.separated(
                            scrollDirection: Axis.horizontal,
                            itemCount: _likedMovies.length.clamp(0, 12),
                            separatorBuilder: (_, __) =>
                                const SizedBox(width: 10),
                            itemBuilder: (context, index) {
                              final movie = _likedMovies[index];
                              return Stack(
                                children: [
                                  SizedBox(
                                    width: 120,
                                    child: MovieCard(movie: movie),
                                  ),
                                  Positioned(
                                    top: 8,
                                    right: 8,
                                    child: Container(
                                      padding: const EdgeInsets.all(4),
                                      decoration: BoxDecoration(
                                        color: Colors.black
                                            .withValues(alpha: 0.6),
                                        borderRadius: BorderRadius.circular(4),
                                      ),
                                      child: Icon(
                                        Icons.favorite,
                                        color: Colors.red.shade400,
                                        size: 14,
                                      ),
                                    ),
                                  ),
                                ],
                              );
                            },
                          ),
                        ),
                      ],
                      const SizedBox(height: 24),
                      GhostButton(
                        label: 'İstatistiklerim',
                        icon: Icons.bar_chart,
                        onPressed: () => context.push('/stats'),
                      ),
                      const SizedBox(height: 16),
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
