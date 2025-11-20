# PicoTrack 🛰️
### Real-time IoT GPS Tracking System

![Flutter](https://img.shields.io/badge/Flutter-3.0-02569B?logo=flutter)
![Raspberry Pi](https://img.shields.io/badge/Hardware-Pico_W-C51A4A?logo=raspberry-pi)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/license-MIT-green)

**PicoTrack** is a full-stack IoT solution that provides real-time location monitoring. It consists of a hardware node (Raspberry Pi Pico W + NEO-6M GPS) that captures coordinates and transmits them via a JSON API to a cross-platform Flutter mobile application.

---

### ⚠️ Technical Note
> **Regarding Package Name:** The internal Flutter package and root directory are named **`geo_loc`**. This was the initial development codename. The project has since been rebranded to **PicoTrack**, but the package structure retains the original namespace to preserve dependency integrity.

---

### 📸 Screenshots
| Mobile App View | Hardware Setup |
|:---:|:---:|
| *(Place your app screenshot here)* | *(Place your hardware photo here)* |
| *Real-time tracking interface* | *Pico W wired to NEO-6M* |

---

### 🔌 Hardware Setup
The backend runs on a **Raspberry Pi Pico W**. Below is the wiring configuration for the **NEO-6M GPS Module**.

| GPS Module Pin | Pico W Pin | Function |
| :--- | :--- | :--- |
| **VCC** | VBUS (5V) | Power |
| **GND** | GND | Ground |
| **TX** | GP1 (UART0 RX) | Data Transmit |
| **RX** | GP0 (UART0 TX) | Data Receive |

> **Note:** The GPS module communicates via UART at a baudrate of `9600`.

---

### 📡 API Reference
The Pico W acts as a local web server. The Flutter app fetches data from these endpoints:

#### Get Live Location
```http
GET /data
