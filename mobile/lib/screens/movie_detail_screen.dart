import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../core/theme.dart';
import '../models/movie.dart';
import '../services/movie_service.dart';
import '../utils/url_utils.dart';
import '../widgets/custom_button.dart';
import '../widgets/film_grain.dart';
import '../widgets/movie_card.dart';

class MovieDetailScreen extends StatefulWidget {
  final int movieId;

  const MovieDetailScreen({super.key, required this.movieId});

  @override
  State<MovieDetailScreen> createState() => _MovieDetailScreenState();
}

class _MovieDetailScreenState extends State<MovieDetailScreen> {
  Movie? _movie;
  List<Movie> _similar = [];
  List<Map<String, dynamic>> _reviews = [];
  String? _whyReason;
  String? _aiReview;
  int? _aiReviewCount;
  bool _loading = true;
  bool _whyLoading = false;
  bool _aiLoading = false;
  bool _recLoading = false;
  bool _actionLoading = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);

    final movie = await MovieService.getMovieDetail(widget.movieId);
    final reviews = await MovieService.getReviews(widget.movieId);

    if (!mounted) return;

    setState(() {
      _movie = movie;
      _reviews = reviews;
      _loading = false;
    });

    _loadSimilar();
    _loadAiReview();
    _loadWhyFromHistory();
  }

  Future<void> _loadWhyFromHistory() async {
    final history = await MovieService.getWatchHistory();
    Movie? source;
    for (final movie in history) {
      if (movie.id != widget.movieId) {
        source = movie;
        break;
      }
    }
    if (source == null || !mounted) return;
    await _loadWhyReason(source.id);
  }

  Future<void> _loadSimilar() async {
    setState(() => _recLoading = true);

    List<Movie> similar = [];
    for (var attempt = 0; attempt < 20; attempt++) {
      similar = await MovieService.getRecommendations(widget.movieId);
      if (similar.isNotEmpty) break;
      await Future.delayed(const Duration(seconds: 3));
      if (!mounted) return;
    }

    if (!mounted) return;
    setState(() {
      _similar = similar;
      _recLoading = false;
    });
  }

  Future<void> _loadWhyReason(int sourceId) async {
    setState(() => _whyLoading = true);
    final reason = await MovieService.getRecommendationReason(
      sourceId,
      widget.movieId,
    );
    if (!mounted) return;
    setState(() {
      _whyReason = reason;
      _whyLoading = false;
    });
  }

  Future<void> _loadAiReview() async {
    setState(() => _aiLoading = true);
    final data = await MovieService.getAiReview(widget.movieId);
    if (!mounted) return;
    setState(() {
      if (data != null &&
          data['has_reviews'] == true &&
          data['ai_review'] != null) {
        _aiReview = data['ai_review'] as String?;
        _aiReviewCount = data['review_count'] as int?;
      }
      _aiLoading = false;
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

  Future<void> _playTrailer() async {
    final url = await MovieService.getTrailer(widget.movieId);
    if (url != null) {
      await openUrl(url);
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Fragman bulunamadı')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        backgroundColor: AppTheme.background,
        body: Stack(
          children: [
            const FilmGrain(),
            const Center(
              child: CircularProgressIndicator(color: AppTheme.primary),
            ),
          ],
        ),
      );
    }

    if (_movie == null) {
      return Scaffold(
        backgroundColor: AppTheme.background,
        appBar: AppBar(),
        body: const Center(
          child: Text('Film bulunamadı', style: TextStyle(color: AppTheme.error)),
        ),
      );
    }

    final movie = _movie!;

    return Scaffold(
      backgroundColor: AppTheme.background,
      body: Stack(
        children: [
          const FilmGrain(),
          CustomScrollView(
            slivers: [
              SliverAppBar(
                pinned: true,
                backgroundColor: AppTheme.background,
                leading: IconButton(
                  icon: const Icon(Icons.arrow_back, color: AppTheme.primary),
                  onPressed: () => context.pop(),
                ),
              ),
              SliverToBoxAdapter(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (movie.posterUrl != null)
                      AspectRatio(
                        aspectRatio: 2 / 3,
                        child: CachedNetworkImage(
                          imageUrl: movie.posterUrl!,
                          fit: BoxFit.cover,
                          width: double.infinity,
                        ),
                      ),
                    Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            movie.displayGenre.toUpperCase(),
                            style: const TextStyle(
                              color: AppTheme.primary,
                              fontSize: 12,
                              letterSpacing: 1.5,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            movie.title,
                            style: AppTheme.headlineTitle(size: 36),
                          ),
                          if (movie.displayTagline.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            Text(
                              '"${movie.displayTagline}"',
                              style: const TextStyle(
                                color: AppTheme.onSurfaceVariant,
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ],
                          const SizedBox(height: 12),
                          Text(
                            '${movie.releaseYear ?? ''} • ${movie.displayGenre}',
                            style: const TextStyle(
                              color: AppTheme.onSurfaceVariant,
                            ),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            movie.displayOverview,
                            style: const TextStyle(
                              color: AppTheme.onSurfaceVariant,
                              height: 1.5,
                            ),
                          ),
                          if (movie.director != null) ...[
                            const SizedBox(height: 16),
                            Text(
                              'Yönetmen: ${movie.director}',
                              style: const TextStyle(color: AppTheme.onSurface),
                            ),
                          ],
                          if (movie.actors != null) ...[
                            const SizedBox(height: 8),
                            Text(
                              'Oyuncular: ${movie.actors}',
                              style: const TextStyle(
                                color: AppTheme.onSurfaceVariant,
                              ),
                            ),
                          ],
                          const SizedBox(height: 20),
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
                          const SizedBox(height: 12),
                          GhostButton(
                            label: 'Fragmanı İzle',
                            icon: Icons.play_circle_outline,
                            onPressed: _playTrailer,
                          ),
                          if (_whyLoading || _whyReason != null) ...[
                            const SizedBox(height: 20),
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                border: const Border(
                                  left: BorderSide(
                                    color: AppTheme.primary,
                                    width: 2,
                                  ),
                                ),
                                color: AppTheme.surfaceContainer,
                              ),
                              child: _whyLoading
                                  ? const Text(
                                      'AI analizi yapılıyor...',
                                      style: TextStyle(
                                        color: AppTheme.onSurfaceVariant,
                                      ),
                                    )
                                  : Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        const Text(
                                          '✨ Neden Önerildi?',
                                          style: TextStyle(
                                            color: AppTheme.primary,
                                            fontSize: 12,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          _whyReason!,
                                          style: const TextStyle(
                                            color: AppTheme.onSurfaceVariant,
                                            fontSize: 13,
                                          ),
                                        ),
                                      ],
                                    ),
                            ),
                          ],
                          if (_aiLoading || _aiReview != null) ...[
                            const SizedBox(height: 20),
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: AppTheme.surfaceContainer,
                                border: Border.all(
                                  color: AppTheme.primary.withValues(alpha: 0.3),
                                ),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: _aiLoading
                                  ? Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        const Text(
                                          '🤖 AI Eleştirmen Değerlendirmesi',
                                          style: TextStyle(
                                            color: AppTheme.primary,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        const SizedBox(height: 12),
                                        const LinearProgressIndicator(
                                          color: AppTheme.primary,
                                        ),
                                        const SizedBox(height: 8),
                                        const Text(
                                          'AI analizi yapılıyor...',
                                          style: TextStyle(
                                            color: AppTheme.onSurfaceVariant,
                                            fontSize: 12,
                                          ),
                                        ),
                                      ],
                                    )
                                  : Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        const Text(
                                          '🤖 AI Eleştirmen Değerlendirmesi',
                                          style: TextStyle(
                                            color: AppTheme.primary,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        const SizedBox(height: 8),
                                        Text(
                                          _aiReview!,
                                          style: const TextStyle(
                                            color: AppTheme.onSurface,
                                            height: 1.5,
                                          ),
                                        ),
                                        if (_aiReviewCount != null) ...[
                                          const SizedBox(height: 8),
                                          Text(
                                            '📊 $_aiReviewCount eleştirmen yorumu analiz edildi',
                                            style: const TextStyle(
                                              color: AppTheme.onSurfaceVariant,
                                              fontSize: 11,
                                            ),
                                          ),
                                        ],
                                      ],
                                    ),
                            ),
                          ],
                          const SizedBox(height: 28),
                          Text(
                            'ELEŞTİRMEN YORUMLARI',
                            style: AppTheme.headlineTitle(size: 24),
                          ),
                          const SizedBox(height: 12),
                          if (_reviews.isEmpty)
                            const Text(
                              'Henüz yorum yok',
                              style: TextStyle(
                                color: AppTheme.onSurfaceVariant,
                              ),
                            )
                          else
                            ..._reviews.map(
                              (review) => Container(
                                margin: const EdgeInsets.only(bottom: 12),
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: AppTheme.surface,
                                  border: Border.all(
                                    color: AppTheme.outlineVariant
                                        .withValues(alpha: 0.5),
                                  ),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  review['review_text'] ?? '',
                                  style: const TextStyle(
                                    color: AppTheme.onSurfaceVariant,
                                    fontSize: 13,
                                  ),
                                ),
                              ),
                            ),
                          const SizedBox(height: 28),
                          Text(
                            'BENZER FİLMLER',
                            style: AppTheme.headlineTitle(size: 24),
                          ),
                          const SizedBox(height: 12),
                          if (_recLoading)
                            const Padding(
                              padding: EdgeInsets.symmetric(vertical: 24),
                              child: Center(
                                child: CircularProgressIndicator(
                                  color: AppTheme.primary,
                                ),
                              ),
                            )
                          else if (_similar.isEmpty)
                            const Text(
                              'Benzer film bulunamadı',
                              style: TextStyle(
                                color: AppTheme.onSurfaceVariant,
                              ),
                            )
                          else
                            SizedBox(
                              height: 220,
                              child: ListView.separated(
                                scrollDirection: Axis.horizontal,
                                itemCount: _similar.length,
                                separatorBuilder: (_, __) =>
                                    const SizedBox(width: 12),
                                itemBuilder: (context, index) => SizedBox(
                                  width: 120,
                                  child: MovieCard(movie: _similar[index]),
                                ),
                              ),
                            ),
                          const SizedBox(height: 32),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
