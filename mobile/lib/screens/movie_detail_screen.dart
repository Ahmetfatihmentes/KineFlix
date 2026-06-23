import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/constants.dart';
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
  List<Map<String, dynamic>> _userReviews = [];
  String? _whyReason;
  String? _aiReview;
  int? _aiReviewCount;
  bool _loading = true;
  bool _whyLoading = false;
  bool _aiLoading = false;
  bool _recLoading = false;
  bool _actionLoading = false;
  bool _watched = false;
  bool _liked = false;
  bool _likeLoading = false;
  int _currentUserId = 0;
  final TextEditingController _reviewController = TextEditingController();
  bool _reviewSubmitting = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _reviewController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() => _loading = true);

    final prefs = await SharedPreferences.getInstance();
    _currentUserId = prefs.getInt(AppConstants.userIdKey) ?? 0;

    final results = await Future.wait<dynamic>([
      MovieService.getMovieDetail(widget.movieId),
      MovieService.getReviews(widget.movieId),
      MovieService.getLikeStatus(widget.movieId),
      MovieService.getUserReviews(widget.movieId),
    ]);

    if (!mounted) return;

    final likeStatus = results[2] as Map<String, dynamic>?;

    setState(() {
      _movie = results[0] as Movie?;
      _reviews = results[1] as List<Map<String, dynamic>>;
      _liked = likeStatus?['liked'] as bool? ?? false;
      _userReviews = results[3] as List<Map<String, dynamic>>;
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
    for (var attempt = 0; attempt < 10; attempt++) {
      similar = await MovieService.getRecommendations(widget.movieId);
      if (similar.isNotEmpty) break;
      await Future.delayed(const Duration(seconds: 5));
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
    if (_watched) {
      await MovieService.removeFromWatchHistory(movie.id);
    } else {
      await MovieService.addToWatchHistory(movie.id);
    }
    if (mounted) {
      setState(() {
        _watched = !_watched;
        _actionLoading = false;
      });
    }
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

  Future<void> _handleLike() async {
    setState(() => _likeLoading = true);
    final nowLiked = await MovieService.toggleLike(widget.movieId);
    if (!mounted) return;
    setState(() {
      _liked = nowLiked;
      _likeLoading = false;
    });
  }

  Future<void> _handleReviewSubmit() async {
    final text = _reviewController.text.trim();
    if (text.isEmpty) return;

    setState(() => _reviewSubmitting = true);
    final review = await MovieService.addUserReview(widget.movieId, text);
    if (!mounted) return;

    if (review != null) {
      _reviewController.clear();
      final updated = await MovieService.getUserReviews(widget.movieId);
      if (!mounted) return;
      setState(() {
        _userReviews = updated;
        _reviewSubmitting = false;
      });
    } else {
      setState(() => _reviewSubmitting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Yorum gönderilemedi')),
      );
    }
  }

  Future<void> _handleReviewDelete(int reviewId) async {
    final ok = await MovieService.deleteUserReview(reviewId);
    if (!mounted) return;
    if (ok) {
      setState(() {
        _userReviews.removeWhere((r) => r['id'] == reviewId);
      });
    }
  }

  Widget _sentimentBadge(String? sentiment) {
    if (sentiment == null) return const SizedBox.shrink();
    final isPositive = sentiment == 'positive';
    final isNegative = sentiment == 'negative';
    final label = isPositive ? 'Olumlu' : isNegative ? 'Olumsuz' : 'Nötr';
    final color = isPositive
        ? Colors.green.shade600
        : isNegative
            ? Colors.red.shade400
            : Colors.grey.shade500;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color, width: 0.5),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 11,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        backgroundColor: AppTheme.background,
        body: Stack(
          children: [
            FilmGrain(),
            Center(
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
                          // İzle + Listeye Ekle
                          Row(
                            children: [
                              Expanded(
                                child: GhostButton(
                                  label: _watched ? 'İzlendi' : 'İzle',
                                  icon: _watched ? Icons.check : Icons.add,
                                  onPressed: _actionLoading ? null : () => _watch(movie),
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
                          // Fragman + Beğen
                          Row(
                            children: [
                              Expanded(
                                child: GhostButton(
                                  label: 'Fragmanı İzle',
                                  icon: Icons.play_circle_outline,
                                  onPressed: _playTrailer,
                                ),
                              ),
                              const SizedBox(width: 12),
                              GestureDetector(
                                onTap: _likeLoading ? null : _handleLike,
                                child: Container(
                                  width: 52,
                                  height: 52,
                                  decoration: BoxDecoration(
                                    border: Border.all(
                                      color: _liked
                                          ? Colors.red.shade400
                                          : AppTheme.outlineVariant,
                                    ),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Center(
                                    child: _likeLoading
                                        ? const SizedBox(
                                            width: 18,
                                            height: 18,
                                            child: CircularProgressIndicator(
                                              strokeWidth: 2,
                                              color: AppTheme.primary,
                                            ),
                                          )
                                        : Icon(
                                            _liked
                                                ? Icons.favorite
                                                : Icons.favorite_border,
                                            color: _liked
                                                ? Colors.red.shade400
                                                : AppTheme.onSurfaceVariant,
                                            size: 22,
                                          ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                          // Neden Önerildi
                          if (_whyLoading || _whyReason != null) ...[
                            const SizedBox(height: 20),
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(12),
                              decoration: const BoxDecoration(
                                border: Border(
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
                          // AI Eleştirmen
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
                                  ? const Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          '🤖 AI Eleştirmen Değerlendirmesi',
                                          style: TextStyle(
                                            color: AppTheme.primary,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        SizedBox(height: 12),
                                        LinearProgressIndicator(
                                          color: AppTheme.primary,
                                        ),
                                        SizedBox(height: 8),
                                        Text(
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
                          // Kullanıcı Yorumları
                          const SizedBox(height: 28),
                          Text(
                            'KULLANICI YORUMLARI',
                            style: AppTheme.headlineTitle(size: 24),
                          ),
                          const SizedBox(height: 12),
                          Container(
                            decoration: BoxDecoration(
                              color: AppTheme.surface,
                              border: Border.all(
                                color: AppTheme.outlineVariant
                                    .withValues(alpha: 0.5),
                              ),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: TextField(
                              controller: _reviewController,
                              maxLines: 3,
                              style: const TextStyle(color: AppTheme.onSurface),
                              decoration: const InputDecoration(
                                hintText:
                                    'Bu film hakkında ne düşünüyorsunuz?',
                                hintStyle: TextStyle(
                                  color: AppTheme.onSurfaceVariant,
                                  fontSize: 13,
                                ),
                                border: InputBorder.none,
                                contentPadding: EdgeInsets.all(12),
                              ),
                            ),
                          ),
                          const SizedBox(height: 8),
                          PrimaryButton(
                            label: 'Yorum Gönder',
                            icon: Icons.send,
                            loading: _reviewSubmitting,
                            onPressed: _handleReviewSubmit,
                          ),
                          const SizedBox(height: 12),
                          if (_userReviews.isEmpty)
                            const Text(
                              'Henüz kullanıcı yorumu yok',
                              style: TextStyle(
                                color: AppTheme.onSurfaceVariant,
                              ),
                            )
                          else
                            ..._userReviews.map((review) {
                              final reviewId = review['id'] as int?;
                              final userId = review['user_id'] as int?;
                              final isOwner = userId == _currentUserId;
                              final sentiment = review['sentiment'] as String?;
                              return Container(
                                margin: const EdgeInsets.only(bottom: 10),
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: AppTheme.surface,
                                  border: Border.all(
                                    color: AppTheme.outlineVariant
                                        .withValues(alpha: 0.5),
                                  ),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        _sentimentBadge(sentiment),
                                        const Spacer(),
                                        if (isOwner && reviewId != null)
                                          GestureDetector(
                                            onTap: () =>
                                                _handleReviewDelete(reviewId),
                                            child: const Icon(
                                              Icons.delete_outline,
                                              color: AppTheme.onSurfaceVariant,
                                              size: 18,
                                            ),
                                          ),
                                      ],
                                    ),
                                    if (sentiment != null)
                                      const SizedBox(height: 6),
                                    Text(
                                      review['review_text'] as String? ?? '',
                                      style: const TextStyle(
                                        color: AppTheme.onSurfaceVariant,
                                        fontSize: 13,
                                        height: 1.4,
                                      ),
                                    ),
                                  ],
                                ),
                              );
                            }),
                          // Eleştirmen Yorumları
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
                          // Benzer Filmler
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
