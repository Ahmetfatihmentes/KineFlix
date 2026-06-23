class AppConstants {
  static const String baseUrl = 'http://192.168.1.196:8000';
  static const String tokenKey = 'kineflix_token';
  static const String userEmailKey = 'kineflix_user';
  static const String userIdKey = 'kineflix_user_id';

  static const Map<String, String> genreMap = {
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
    'Western': 'Western',
    'Family': 'Aile',
    'History': 'Tarih',
    'Biography': 'Biyografi',
    'Sport': 'Spor',
    'Musical': 'Müzikal',
    'TV Movie': 'TV Filmi',
    'Crime TV Shows': 'Suç Dizisi',
    'TV Dramas': 'Drama Dizisi',
    'TV Thrillers': 'Gerilim Dizisi',
    'TV Comedies': 'Komedi Dizisi',
    'Anime Series': 'Anime',
    'Reality TV': 'Gerçeklik TV',
    'Talk Shows': 'Talk Show',
    'Kids': 'Çocuk',
    'International': 'Uluslararası',
  };

  static String translateGenre(String genre) {
    return genreMap[genre.trim()] ?? genre.trim();
  }
}
