import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../core/theme.dart';
import '../services/auth_service.dart';
import '../widgets/custom_button.dart';
import '../widgets/custom_text_field.dart';
import '../widgets/film_grain.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmController = TextEditingController();
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _confirmController.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    if (_passwordController.text != _confirmController.text) {
      setState(() => _error = 'Şifreler eşleşmiyor');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    final email = _emailController.text.trim();
    final password = _passwordController.text;

    final registerResult = await AuthService.register(email, password);
    if (!mounted) return;

    if (registerResult['success'] != true) {
      setState(() {
        _loading = false;
        _error = registerResult['message'] as String?;
      });
      return;
    }

    final loginResult = await AuthService.login(email, password);
    if (!mounted) return;

    if (loginResult['success'] == true) {
      context.go('/onboarding');
      return;
    }

    setState(() {
      _loading = false;
      _error = loginResult['message'] as String?;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: Stack(
        children: [
          const FilmGrain(),
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 32),
                  Text('Kayıt Ol', style: AppTheme.displayTitle(size: 48)),
                  const SizedBox(height: 8),
                  const Text(
                    'KineFlix hesabı oluştur',
                    style: TextStyle(color: AppTheme.onSurfaceVariant),
                  ),
                  const SizedBox(height: 40),
                  KineFlixTextField(
                    label: 'E-posta',
                    controller: _emailController,
                    keyboardType: TextInputType.emailAddress,
                    prefixIcon: Icons.mail_outline,
                  ),
                  const SizedBox(height: 20),
                  KineFlixTextField(
                    label: 'Şifre',
                    controller: _passwordController,
                    isPassword: true,
                    prefixIcon: Icons.lock_outline,
                  ),
                  const SizedBox(height: 20),
                  KineFlixTextField(
                    label: 'Şifre Onayı',
                    controller: _confirmController,
                    isPassword: true,
                    prefixIcon: Icons.lock_outline,
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 16),
                    Text(
                      _error!,
                      style: const TextStyle(color: AppTheme.error),
                    ),
                  ],
                  const SizedBox(height: 32),
                  PrimaryButton(
                    label: 'Kayıt Ol',
                    loading: _loading,
                    onPressed: _register,
                  ),
                  const SizedBox(height: 24),
                  Center(
                    child: TextButton(
                      onPressed: () => context.go('/login'),
                      child: const Text(
                        'Zaten hesabın var mı? Giriş yap',
                        style: TextStyle(color: AppTheme.primary),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
