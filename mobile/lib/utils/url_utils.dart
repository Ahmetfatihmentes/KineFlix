import 'package:url_launcher/url_launcher.dart';

Future<void> openUrl(String url) async {
  final uri = Uri.parse(url);
  if (await canLaunchUrl(uri)) {
    await launchUrl(uri, mode: LaunchMode.externalApplication);
  }
}

String justWatchUrl(String movieTitle) {
  return 'https://www.justwatch.com/tr/search?q=${Uri.encodeComponent(movieTitle)}';
}
