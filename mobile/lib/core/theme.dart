import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color background = Color(0xFF0f131d);
  static const Color surface = Color(0xFF1b2029);
  static const Color surfaceContainer = Color(0xFF221f19);
  static const Color primary = Color(0xFFe6c364);
  static const Color primaryContainer = Color(0xFFc9a84c);
  static const Color onPrimary = Color(0xFF3d2e00);
  static const Color onSurface = Color(0xFFe9e1d7);
  static const Color onSurfaceVariant = Color(0xFFd0c5b2);
  static const Color outlineVariant = Color(0xFF4d4637);
  static const Color error = Color(0xFFffb4ab);

  static TextStyle displayTitle({double size = 48}) {
    return GoogleFonts.bebasNeue(
      fontSize: size,
      color: primary,
      letterSpacing: 2,
    );
  }

  static TextStyle headlineTitle({double size = 32}) {
    return GoogleFonts.bebasNeue(
      fontSize: size,
      color: onSurface,
      letterSpacing: 1.5,
    );
  }

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: background,
      colorScheme: const ColorScheme.dark(
        surface: surface,
        primary: primary,
        onPrimary: onPrimary,
        onSurface: onSurface,
        error: error,
      ),
      textTheme: GoogleFonts.plusJakartaSansTextTheme(
        ThemeData.dark().textTheme,
      ).apply(bodyColor: onSurface, displayColor: onSurface),
      appBarTheme: const AppBarTheme(
        backgroundColor: background,
        foregroundColor: primary,
        elevation: 0,
        centerTitle: false,
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: surface,
        selectedItemColor: primary,
        unselectedItemColor: onSurfaceVariant,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
      ),
    );
  }
}
