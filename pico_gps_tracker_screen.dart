import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:geo_loc/theme.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

class PicoGpsTrackerScreen extends StatefulWidget {
  const PicoGpsTrackerScreen({super.key});

  @override
  State<PicoGpsTrackerScreen> createState() => _PicoGpsTrackerScreenState();
}

class _PicoGpsTrackerScreenState extends State<PicoGpsTrackerScreen> {
  final TextEditingController _ipController =
      TextEditingController(text: ' ');
  final MapController _mapController = MapController();
  final List<LatLng> _pathHistory = [];
  Timer? _timer;
  LatLng _currentLocation = LatLng(10.8505, 76.2711); // Default location
  bool isConnected = false;
  String statusText = "Disconnected";

  void _startTracking() {
    setState(() {
      statusText = "Connecting...";
    });
    _timer?.cancel(); // Cancel any existing timer
    _timer = Timer.periodic(const Duration(seconds: 3), (timer) async {
      try {
        final response = await http
            .get(Uri.parse('http://${_ipController.text}/data'))
            .timeout(const Duration(seconds: 2));
        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          if (data['lat'] != null && data['lng'] != null) {
            final newPosition =
                LatLng(data['lat'].toDouble(), data['lng'].toDouble());
            setState(() {
              isConnected = true;
              statusText = "Connected! Last update: ${DateTime.now().toLocal()}";
              _currentLocation = newPosition;
              _pathHistory.add(newPosition);
              _mapController.move(_currentLocation, 15.0);
            });
          }
        }
      } catch (e) {
        // Handle connection errors
        setState(() {
          isConnected = false;
          statusText = "Error: Connection failed.";
        });
        _timer?.cancel();
        print('Error fetching data: $e');
      }
    });
  }

  void _stopTracking() {
    _timer?.cancel();
    setState(() {
      isConnected = false;
      statusText = "Disconnected";
      _pathHistory.clear();
    });
  }

  void _showIpAddressDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Enter Pico W IP Address'),
          content: TextField(
            controller: _ipController,
            decoration: const InputDecoration(
              labelText: 'Pico W IP Address',
              border: OutlineInputBorder(),
            ),
            keyboardType: TextInputType.number,
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    _ipController.dispose();
    _mapController.dispose();
    super.dispose();
  }

  Widget _buildRoundButton(IconData icon, VoidCallback onPressed) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        shape: const CircleBorder(),
        padding: const EdgeInsets.all(16),
      ),
      child: Icon(icon),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PicoTrack'),
        actions: [
          PopupMenuButton(
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'dark_mode',
                child: Text('Dark Mode'),
              ),
            ],
            onSelected: (value) {
              if (value == 'dark_mode') {
                themeNotifier.value =
                    themeNotifier.value == ThemeMode.light
                        ? ThemeMode.dark
                        : ThemeMode.light;
              }
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildRoundButton(Icons.settings_input_component, _showIpAddressDialog),
                _buildRoundButton(Icons.map, () {}),
                _buildRoundButton(Icons.history, () {}),
                _buildRoundButton(Icons.bar_chart, () {}),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: isConnected ? null : _startTracking,
                  child: const Text('Connect'),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: isConnected ? _stopTracking : null,
                  child: const Text('Stop'),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8.0),
            child: Text(
              statusText,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
          Expanded(
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: _currentLocation,
                initialZoom: 15.0,
              ),
              children: [
                TileLayer(
                  urlTemplate:
                      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                  subdomains: const ['a', 'b', 'c'],
                ),
                if (_pathHistory.isNotEmpty)
                  PolylineLayer(
                    polylines: [
                      Polyline(
                        points: _pathHistory,
                        color: Colors.blue,
                        strokeWidth: 4.0,
                      ),
                    ],
                  ),
                MarkerLayer(
                  markers: [
                    Marker(
                      width: 80.0,
                      height: 80.0,
                      point: _currentLocation,
                      child: const Icon(
                        Icons.location_pin,
                        color: Colors.red,
                        size: 40.0,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
