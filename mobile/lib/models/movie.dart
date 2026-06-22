class Movie {
  final int id;
  final String title;
  final String? overview;
  final String? overviewTr;
  final String? genres;
  final String? posterUrl;
  final int? releaseYear;
  final double? letterboxdRating;
  final String? contentType;
  final String? director;
  final String? actors;
  final String? tagline;
  final String? taglineTr;
  final double? positivePct;

  Movie({
    required this.id,
    required this.title,
    this.overview,
    this.overviewTr,
    this.genres,
    this.posterUrl,
    this.releaseYear,
    this.letterboxdRating,
    this.contentType,
    this.director,
    this.actors,
    this.tagline,
    this.taglineTr,
    this.positivePct,
  });

  factory Movie.fromJson(Map<String, dynamic> json) {
    return Movie(
      id: json['id'] ?? 0,
      title: json['title'] ?? '',
      overview: json['overview'],
      overviewTr: json['overview_tr'],
      genres: json['genres'],
      posterUrl: json['poster_url'],
      releaseYear: json['release_year'],
      letterboxdRating: (json['letterboxd_rating'] as num?)?.toDouble(),
      contentType: json['content_type'],
      director: json['director'],
      actors: json['actors'],
      tagline: json['tagline'],
      taglineTr: json['tagline_tr'],
      positivePct: (json['positive_pct'] as num?)?.toDouble(),
    );
  }

  String get displayOverview => overviewTr ?? overview ?? '';
  String get displayTagline => taglineTr ?? tagline ?? '';
  String get displayGenre => genres?.split(',').first.trim() ?? '';
  double get displayRating => letterboxdRating ?? 0;
  bool get isMovie => contentType == 'Movie';
}
