import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;

import '../core/constants.dart';
import '../core/theme.dart';
import '../services/auth_service.dart';
import '../widgets/custom_button.dart';
import '../widgets/film_grain.dart';

const _genres = [
  'Aksiyon',
  'Dram',
  'Komedi',
  'Gerilim',
  'Bilim Kurgu',
  'Romantik',
  'Korku',
  'Belgesel',
  'Animasyon',
];

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final Set<String> _selected = {};
  bool _loading = false;
  String? _error;

  Future<void> _submit() async {
    if (_selected.isEmpty) {
      setState(() => _error = 'Lütfen en az bir tür seçin.');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final token = await AuthService.getToken();
      final response = await http.post(
        Uri.parse('${AppConstants.baseUrl}/users/preferences'),
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
        body: jsonEncode({'genres': _selected.toList()}),
      );

      if (!mounted) return;

      if (response.statusCode == 200 || response.statusCode == 201) {
        context.go('/home');
        return;
      }

      final body = jsonDecode(utf8.decode(response.bodyBytes));
      setState(() {
        _loading = false;
        _error = body['detail']?.toString() ?? 'Bir hata oluştu.';
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = 'Bağlantı hatası. Lütfen tekrar deneyin.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: Stack(
        children: [
          const FilmGrain(),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 48),
                  Text('KineFlix', style: AppTheme.displayTitle(size: 40)),
                  const SizedBox(height: 12),
                  Text(
                    'Hangi türleri seviyorsunuz?',
                    style: AppTheme.headlineTitle(size: 24),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'En az bir tür seçin. Öneriler buna göre şekillenecek.',
                    style: TextStyle(
                      color: AppTheme.onSurfaceVariant,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 32),
                  Expanded(
                    child: Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: _genres.map((genre) {
                        final selected = _selected.contains(genre);
                        return GestureDetector(
                          onTap: () => setState(() {
                            if (selected) {
                              _selected.remove(genre);
                            } else {
                              _selected.add(genre);
                            }
                          }),
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 180),
                            padding: const EdgeInsets.symmetric(
                              horizontal: 20,
                              vertical: 12,
                            ),
                            decoration: BoxDecoration(
                              color: selected
                                  ? AppTheme.primary.withOpacity(0.15)
                                  : AppTheme.surface,
                              border: Border.all(
                                color: selected
                                    ? AppTheme.primary
                                    : AppTheme.outlineVariant,
                                width: selected ? 1.5 : 1,
                              ),
                              borderRadius: BorderRadius.circular(32),
                            ),
                            child: Text(
                              genre,
                              style: TextStyle(
                                color: selected
                                    ? AppTheme.primary
                                    : AppTheme.onSurfaceVariant,
                                fontWeight: selected
                                    ? FontWeight.w600
                                    : FontWeight.normal,
                                fontSize: 14,
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 12),
                    Text(
                      _error!,
                      style: const TextStyle(color: AppTheme.error, fontSize: 13),
                    ),
                  ],
                  const SizedBox(height: 16),
                  PrimaryButton(
                    label: 'Devam Et',
                    loading: _loading,
                    onPressed: _submit,
                  ),
                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
