import 'dart:async';

import 'package:flutter/material.dart';

import '../core/constants.dart';
import '../core/theme.dart';
import '../models/movie.dart';
import '../services/movie_service.dart';
import '../widgets/bottom_nav.dart';
import '../widgets/film_grain.dart';
import '../widgets/movie_card.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  static const _genres = [
    'Action',
    'Drama',
    'Science Fiction',
    'Thriller',
    'Comedy',
    'Romance',
    'Adventure',
    'Documentary',
  ];

  final _controller = TextEditingController();
  Timer? _debounce;
  List<Movie> _results = [];
  bool _loading = false;
  String? _contentFilter;
  String? _genreFilter;

  @override
  void dispose() {
    _debounce?.cancel();
    _controller.dispose();
    super.dispose();
  }

  void _onSearchChanged(String value) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      _search(value);
    });
  }

  Future<void> _search(String query) async {
    if (query.trim().isEmpty && _genreFilter == null) {
      setState(() => _results = []);
      return;
    }

    setState(() => _loading = true);

    final searchQuery = _genreFilter ?? query;
    final results = await MovieService.searchMovies(
      searchQuery,
      contentType: _contentFilter,
    );

    if (!mounted) return;
    setState(() {
      _results = results;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      bottomNavigationBar: const KineFlixBottomNav(currentIndex: 1),
      body: Stack(
        children: [
          const FilmGrain(),
          SafeArea(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 16, 20, 12),
                  child: Text('Ara', style: AppTheme.displayTitle(size: 40)),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: TextField(
                    controller: _controller,
                    onChanged: _onSearchChanged,
                    style: const TextStyle(color: AppTheme.onSurface),
                    decoration: InputDecoration(
                      hintText: 'Film veya dizi ara...',
                      hintStyle:
                          const TextStyle(color: AppTheme.onSurfaceVariant),
                      prefixIcon: const Icon(Icons.search,
                          color: AppTheme.onSurfaceVariant),
                      filled: true,
                      fillColor: AppTheme.surface,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(4),
                        borderSide: BorderSide(
                          color: AppTheme.outlineVariant.withValues(alpha: 0.5),
                        ),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(4),
                        borderSide: BorderSide(
                          color: AppTheme.outlineVariant.withValues(alpha: 0.5),
                        ),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(4),
                        borderSide:
                            const BorderSide(color: AppTheme.primary),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Row(
                    children: [
                      _filterChip('Tümü', null),
                      const SizedBox(width: 8),
                      _filterChip('Filmler', 'Movie'),
                      const SizedBox(width: 8),
                      _filterChip('Diziler', 'TV Show'),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                SizedBox(
                  height: 36,
                  child: ListView.separated(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    scrollDirection: Axis.horizontal,
                    itemCount: _genres.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 8),
                    itemBuilder: (context, index) {
                      final genre = _genres[index];
                      final selected = _genreFilter == genre;
                      return FilterChip(
                        label: Text(AppConstants.translateGenre(genre)),
                        selected: selected,
                        selectedColor: AppTheme.primary.withValues(alpha: 0.2),
                        labelStyle: TextStyle(
                          color: selected
                              ? AppTheme.primary
                              : AppTheme.onSurfaceVariant,
                          fontSize: 12,
                        ),
                        onSelected: (_) {
                          setState(() {
                            _genreFilter = selected ? null : genre;
                          });
                          _search(_controller.text);
                        },
                      );
                    },
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
                      : _results.isEmpty
                          ? Center(
                              child: Text(
                                _controller.text.isEmpty
                                    ? 'Ne aramak istersiniz?'
                                    : 'Sonuç bulunamadı',
                                style: const TextStyle(
                                  color: AppTheme.onSurfaceVariant,
                                ),
                              ),
                            )
                          : GridView.builder(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 20,
                                vertical: 8,
                              ),
                              gridDelegate:
                                  const SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: 2,
                                childAspectRatio: 0.55,
                                crossAxisSpacing: 12,
                                mainAxisSpacing: 12,
                              ),
                              itemCount: _results.length,
                              itemBuilder: (context, index) =>
                                  MovieCard(movie: _results[index]),
                            ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _filterChip(String label, String? value) {
    final selected = _contentFilter == value;
    return ChoiceChip(
      label: Text(label),
      selected: selected,
      selectedColor: AppTheme.primary.withValues(alpha: 0.2),
      labelStyle: TextStyle(
        color: selected ? AppTheme.primary : AppTheme.onSurfaceVariant,
      ),
      onSelected: (_) {
        setState(() => _contentFilter = value);
        _search(_controller.text);
      },
    );
  }
}
