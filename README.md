# PicoTrack 🛰️
### Real-time IoT GPS Tracking System

![Flutter](https://img.shields.io/badge/Flutter-3.0-02569B?logo=flutter)
![Raspberry Pi](https://img.shields.io/badge/Hardware-Pico_W-C51A4A?logo=raspberry-pi)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/license-MIT-green)

**PicoTrack** is a full-stack IoT solution that provides real-time location monitoring. It consists of a hardware node (Raspberry Pi Pico W + NEO-6M GPS) that captures coordinates and transmits them via a JSON API to a cross-platform Flutter mobile application.

This project is a starting point for a Flutter application.
---

A few resources to get you started if this is your first Flutter project:
### ⚠️ Technical Note
> **Regarding Package Name:** The internal Flutter package and root directory are named **`geo_loc`**. This was the initial development codename. The project has since been rebranded to **PicoTrack**, but the package structure retains the original namespace to preserve dependency integrity.

### 🔋 Features
* **Real-Time Tracking:** Live updates of GPS coordinates on an interactive map.
* **Hardware Integration:** Custom MicroPython firmware running on Raspberry Pi Pico W.
* **Dual-Core Processing:** Dedicated core for GPS NMEA parsing to ensure non-blocking Wi-Fi transmission.
* **Cross-Platform:** Mobile app built with Flutter (Android/iOS).
* **Self-Hosted API:** The hardware acts as its own web server, serving data directly to the app.

### 🛠️ Tech Stack
* **Mobile:** Flutter, Dart, Google Maps / Leaflet
* **Hardware:** Raspberry Pi Pico W, NEO-6M GPS Module
* **Firmware:** MicroPython
* **Communication:** REST API (JSON over HTTP)

### 📂 Project Structure
* `lib/` - Main Flutter application source code.
* `firmware/` - MicroPython scripts for the Raspberry Pi Pico W.
