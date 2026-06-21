import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../core/theme.dart';
import '../models/movie.dart';
import '../services/movie_service.dart';
import '../widgets/bottom_nav.dart';
import '../widgets/custom_button.dart';
import '../widgets/film_grain.dart';

class WatchlistScreen extends StatefulWidget {
  const WatchlistScreen({super.key});

  @override
  State<WatchlistScreen> createState() => _WatchlistScreenState();
}

class _WatchlistScreenState extends State<WatchlistScreen> {
  List<Movie> _items = [];
  bool _loading = true;
  String? _contentFilter;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final items = await MovieService.getWatchlist();
    if (!mounted) return;
    setState(() {
      _items = items;
      _loading = false;
    });
  }

  List<Movie> get _filtered {
    if (_contentFilter == null) return _items;
    return _items.where((m) => m.contentType == _contentFilter).toList();
  }

  Future<void> _remove(int movieId) async {
    await MovieService.removeFromWatchlist(movieId);
    await _load();
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _filtered;

    return Scaffold(
      backgroundColor: AppTheme.background,
      bottomNavigationBar: const KineFlixBottomNav(currentIndex: 2),
      body: Stack(
        children: [
          const FilmGrain(),
          SafeArea(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 16, 20, 12),
                  child: Text('Listelerim', style: AppTheme.displayTitle(size: 40)),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Row(
                    children: [
                      _chip('Tümü', null),
                      const SizedBox(width: 8),
                      _chip('Filmler', 'Movie'),
                      const SizedBox(width: 8),
                      _chip('Diziler', 'TV Show'),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: _loading
                      ? const Center(
                          child: CircularProgressIndicator(
                            color: AppTheme.primary,
                          ),
                        )
                      : filtered.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  const Icon(
                                    Icons.bookmark_border,
                                    size: 64,
                                    color: AppTheme.onSurfaceVariant,
                                  ),
                                  const SizedBox(height: 16),
                                  const Text(
                                    'Listeniz henüz boş',
                                    style: TextStyle(
                                      color: AppTheme.onSurfaceVariant,
                                    ),
                                  ),
                                  const SizedBox(height: 24),
                                  SizedBox(
                                    width: 200,
                                    child: PrimaryButton(
                                      label: 'Film Keşfet',
                                      onPressed: () => context.go('/home'),
                                    ),
                                  ),
                                ],
                              ),
                            )
                          : ListView.separated(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 20,
                                vertical: 8,
                              ),
                              itemCount: filtered.length,
                              separatorBuilder: (_, __) =>
                                  const SizedBox(height: 12),
                              itemBuilder: (context, index) {
                                final movie = filtered[index];
                                return _WatchlistTile(
                                  movie: movie,
                                  onRemove: () => _remove(movie.id),
                                  onTap: () =>
                                      context.push('/movies/${movie.id}'),
                                );
                              },
                            ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _chip(String label, String? value) {
    final selected = _contentFilter == value;
    return ChoiceChip(
      label: Text(label),
      selected: selected,
      selectedColor: AppTheme.primary.withValues(alpha: 0.2),
      labelStyle: TextStyle(
        color: selected ? AppTheme.primary : AppTheme.onSurfaceVariant,
      ),
      onSelected: (_) => setState(() => _contentFilter = value),
    );
  }
}

class _WatchlistTile extends StatelessWidget {
  final Movie movie;
  final VoidCallback onRemove;
  final VoidCallback onTap;

  const _WatchlistTile({
    required this.movie,
    required this.onRemove,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppTheme.surfaceContainer,
          border: Border.all(
            color: AppTheme.outlineVariant.withValues(alpha: 0.5),
          ),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            SizedBox(
              width: 56,
              height: 84,
              child: movie.posterUrl != null
                  ? CachedNetworkImage(
                      imageUrl: movie.posterUrl!,
                      fit: BoxFit.cover,
                    )
                  : const Icon(Icons.movie_outlined),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    movie.title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: AppTheme.onSurface,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${movie.releaseYear ?? ''} • ${movie.displayGenre}',
                    style: const TextStyle(
                      color: AppTheme.onSurfaceVariant,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            IconButton(
              onPressed: onRemove,
              icon: const Icon(Icons.delete_outline, color: AppTheme.error),
            ),
          ],
        ),
      ),
    );
  }
}
