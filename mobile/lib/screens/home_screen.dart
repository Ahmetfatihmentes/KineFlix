import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../core/theme.dart';
import '../models/movie.dart';
import '../services/movie_service.dart';
import '../utils/url_utils.dart';
import '../widgets/bottom_nav.dart';
import '../widgets/custom_button.dart';
import '../widgets/film_grain.dart';
import '../widgets/movie_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  static const _moods = [
    ('Aksiyon', 'Action'),
    ('Korku', 'Horror'),
    ('Drama', 'Drama'),
    ('Bilim Kurgu', 'Science Fiction'),
    ('Komedi', 'Comedy'),
    ('Gerilim', 'Thriller'),
  ];

  Movie? _featured;
  String? _recReason;
  String? _selectedMood;
  List<Movie> _movies = [];
  bool _loading = true;
  bool _actionLoading = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load({String? genreQuery}) async {
    setState(() => _loading = true);

    final personalized = await MovieService.getPersonalizedRecommendation();
    Movie? featured;
    String? reason;

    if (personalized != null && personalized['recommended_movie'] != null) {
      featured = Movie.fromJson(
        personalized['recommended_movie'] as Map<String, dynamic>,
      );
      final sourceId = personalized['source_movie_id'];
      if (sourceId != null) {
        reason = await MovieService.getRecommendationReason(
          sourceId as int,
          featured.id,
        );
      }
    }

    final movies = genreQuery != null
        ? await MovieService.searchMovies(genreQuery)
        : await MovieService.searchMovies('a');

    if (!mounted) return;

    setState(() {
      _featured = featured ?? (movies.isNotEmpty ? movies.first : null);
      _recReason = reason;
      _movies = movies.take(12).toList();
      _loading = false;
    });
  }

  Future<void> _watch(Movie movie) async {
    setState(() => _actionLoading = true);
    await MovieService.addToWatchHistory(movie.id);
    await openUrl(justWatchUrl(movie.title));
    if (mounted) setState(() => _actionLoading = false);
  }

  Future<void> _addToList(Movie movie) async {
    setState(() => _actionLoading = true);
    await MovieService.addToWatchlist(movie.id);
    if (mounted) {
      setState(() => _actionLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Listeye eklendi')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      bottomNavigationBar: const KineFlixBottomNav(currentIndex: 0),
      body: Stack(
        children: [
          const FilmGrain(),
          SafeArea(
            child: _loading
                ? const Center(
                    child: CircularProgressIndicator(color: AppTheme.primary),
                  )
                : RefreshIndicator(
                    color: AppTheme.primary,
                    onRefresh: () => _load(genreQuery: _selectedMood),
                    child: ListView(
                      padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
                      children: [
                        Text('KineFlix', style: AppTheme.displayTitle(size: 40)),
                        const SizedBox(height: 20),
                        SizedBox(
                          height: 40,
                          child: ListView.separated(
                            scrollDirection: Axis.horizontal,
                            itemCount: _moods.length,
                            separatorBuilder: (_, __) => const SizedBox(width: 8),
                            itemBuilder: (context, index) {
                              final mood = _moods[index];
                              final selected = _selectedMood == mood.$2;
                              return FilterChip(
                                label: Text(mood.$1),
                                selected: selected,
                                selectedColor:
                                    AppTheme.primary.withValues(alpha: 0.2),
                                checkmarkColor: AppTheme.primary,
                                labelStyle: TextStyle(
                                  color: selected
                                      ? AppTheme.primary
                                      : AppTheme.onSurfaceVariant,
                                ),
                                side: BorderSide(
                                  color: selected
                                      ? AppTheme.primary
                                      : AppTheme.outlineVariant,
                                ),
                                onSelected: (_) {
                                  setState(() {
                                    _selectedMood =
                                        selected ? null : mood.$2;
                                  });
                                  _load(genreQuery: selected ? null : mood.$2);
                                },
                              );
                            },
                          ),
                        ),
                        const SizedBox(height: 24),
                        if (_featured != null) _buildFeatured(_featured!),
                        const SizedBox(height: 28),
                        Text(
                          'POPÜLER',
                          style: AppTheme.headlineTitle(size: 24),
                        ),
                        const SizedBox(height: 16),
                        GridView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          gridDelegate:
                              const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 2,
                            childAspectRatio: 0.55,
                            crossAxisSpacing: 12,
                            mainAxisSpacing: 12,
                          ),
                          itemCount: _movies.length,
                          itemBuilder: (context, index) =>
                              MovieCard(movie: _movies[index]),
                        ),
                      ],
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeatured(Movie movie) {
    return GestureDetector(
      onTap: () => context.push('/movies/${movie.id}'),
      child: Container(
        decoration: BoxDecoration(
          color: AppTheme.surfaceContainer,
          border: Border.all(
            color: AppTheme.outlineVariant.withValues(alpha: 0.5),
          ),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (movie.posterUrl != null)
              AspectRatio(
                aspectRatio: 16 / 9,
                child: CachedNetworkImage(
                  imageUrl: movie.posterUrl!,
                  fit: BoxFit.cover,
                ),
              ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'SANA ÖZEL',
                    style: TextStyle(
                      color: AppTheme.primary,
                      fontSize: 11,
                      letterSpacing: 1.5,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(movie.title, style: AppTheme.headlineTitle(size: 28)),
                  const SizedBox(height: 4),
                  Text(
                    '${movie.releaseYear ?? ''} • ${movie.displayGenre}',
                    style: const TextStyle(color: AppTheme.onSurfaceVariant),
                  ),
                  if (_recReason != null) ...[
                    const SizedBox(height: 12),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        border: Border(
                          left: BorderSide(color: AppTheme.primary, width: 2),
                        ),
                        color: AppTheme.surface,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            '✨ Neden Önerildi?',
                            style: TextStyle(
                              color: AppTheme.primary,
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _recReason!,
                            style: const TextStyle(
                              color: AppTheme.onSurfaceVariant,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: PrimaryButton(
                          label: 'İzle',
                          icon: Icons.play_arrow,
                          loading: _actionLoading,
                          onPressed: () => _watch(movie),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: GhostButton(
                          label: 'Listeye Ekle',
                          icon: Icons.add,
                          onPressed: _actionLoading
                              ? null
                              : () => _addToList(movie),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
