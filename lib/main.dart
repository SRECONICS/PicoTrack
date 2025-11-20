import 'package:flutter/material.dart';
import 'package:geo_loc/pico_gps_tracker_screen.dart';
import 'package:geo_loc/theme.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: themeNotifier,
      builder: (_, ThemeMode currentMode, __) {
        return MaterialApp(
          title: 'Pico GPS Tracker',
          theme: ThemeData(
            colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
            useMaterial3: true,
          ),
          darkTheme: ThemeData.dark(),
          themeMode: currentMode,
          debugShowCheckedModeBanner: false,
          home: const PicoGpsTrackerScreen(),
        );
      },
    );
  }
}
