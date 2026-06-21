import 'package:flutter_test/flutter_test.dart';

import 'package:kineflix_mobile/screens/login_screen.dart';
import 'package:flutter/material.dart';

void main() {
  testWidgets('Login screen renders', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: LoginScreen()),
    );
    expect(find.text('Giriş Yap'), findsOneWidget);
  });
}
