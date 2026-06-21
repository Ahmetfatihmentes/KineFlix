import 'package:go_router/go_router.dart';

import '../screens/history_screen.dart';
import '../screens/home_screen.dart';
import '../screens/login_screen.dart';
import '../screens/movie_detail_screen.dart';
import '../screens/profile_screen.dart';
import '../screens/register_screen.dart';
import '../screens/search_screen.dart';
import '../screens/splash_screen.dart';
import '../screens/watchlist_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(path: '/', builder: (c, s) => const SplashScreen()),
    GoRoute(path: '/login', builder: (c, s) => const LoginScreen()),
    GoRoute(path: '/register', builder: (c, s) => const RegisterScreen()),
    GoRoute(path: '/home', builder: (c, s) => const HomeScreen()),
    GoRoute(
      path: '/movies/:id',
      builder: (c, s) => MovieDetailScreen(
        movieId: int.parse(s.pathParameters['id']!),
      ),
    ),
    GoRoute(path: '/search', builder: (c, s) => const SearchScreen()),
    GoRoute(path: '/watchlist', builder: (c, s) => const WatchlistScreen()),
    GoRoute(path: '/history', builder: (c, s) => const HistoryScreen()),
    GoRoute(path: '/profile', builder: (c, s) => const ProfileScreen()),
  ],
);
