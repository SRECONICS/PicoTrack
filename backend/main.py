import network
import time
import socket
from machine import UART, Pin
import _thread
import json # Make sure json is imported

# ----------------------------------------------------
# --- 1. CONFIGURATION ---
# ----------------------------------------------------

# --- Wi-Fi ---
# ⚠️ UPDATE THESE WITH YOUR WI-FI DETAILS
WIFI_SSID = "xxxxxxxxxxxxx"
WIFI_PASSWORD = "xxxxxxxxxx"

# --- GPS ---
# This uses UART 0 on pins GP0 (TX) and GP1 (RX)
# Your NEO-6M TX pin goes to the Pico's RX pin (GP1)
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

# (Your global gps_data dictionary goes here)
gps_data = {
    "lat": 0.000,
    "lng": 0.000,             #add a default location here
    "status": "No Lock"
}

# ----------------------------------------------------
# --- 2. GPS PARSING THREAD ---
# ----------------------------------------------------
# This function runs on the Pico's second core
def gps_reader_thread():
    print("Starting GPS reader thread on Core 1...")
    global gps_data
    
    while True:
        if uart.any():
            line = uart.readline()
            if line:
                try:
                    line_str = line.decode('utf-8')
                    
                    if line_str.startswith('$GPRMC'):
                        parts = line_str.split(',')
                        
                        if parts[2] == 'A':
                            # --- Latitude (DDMM.MMMM) ---
                            lat_raw = parts[3]
                            lat_dir = parts[4]
                            lat_deg = float(lat_raw[:2])
                            lat_min = float(lat_raw[2:])
                            lat_dd = lat_deg + (lat_min / 60)
                            if lat_dir == 'S':
                                lat_dd *= -1

                            # --- Longitude (DDDMM.MMMM) ---
                            lng_raw = parts[5]
                            lng_dir = parts[6]
                            lng_deg = float(lng_raw[:3])
                            lng_min = float(lng_raw[3:])
                            lng_dd = lng_deg + (lng_min / 60)
                            if lng_dir == 'W':
                                lng_dd *= -1
                            
                            gps_data["lat"] = lat_dd
                            gps_data["lng"] = lng_dd
                            gps_data["status"] = "Locked"
                        
                        else:
                            gps_data["status"] = "No Lock"

                except Exception as e:
                    print(f"GPS parse error: {e}")
        
        time.sleep(0.5)

# ----------------------------------------------------
# --- 3. WEB PAGE (HTML/JS) ---
# ----------------------------------------------------
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Pico W GPS Tracker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        #map { height: 90vh; }
        #title { padding: 10px; background: #333; color: white; text-align: center; }
        #status { padding: 10px; text-align: center; }
    </style>
</head>
<body>
    <div id="title">
        <h2>Pico W Live GPS Tracker</h2>
    </div>
    <div id="status">
        Status: <span id="gps_status">Connecting...</span>
    </div>
    <div id="map"></div>

    <script>
        var map = L.map('map').setView([10.85, 76.27], 15);
        var marker = L.marker([10.85, 76.27]).addTo(map);
        var firstUpdate = true;
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);
        
        async function updatePosition() {
            try {
                const response = await fetch('/data');
                const data = await response.json();
                
                const newPos = [data.lat, data.lng];
                marker.setLatLng(newPos);
                document.getElementById('gps_status').innerText = data.status;
                
                if (firstUpdate && data.status === "Locked") {
                    map.setView(newPos, 17);
                    firstUpdate = false;
                }
            } catch (e) {
                console.error("Failed to fetch data", e);
                document.getElementById('gps_status').innerText = "Error (Check Console)";
            }
        }
        
        setInterval(updatePosition, 3000);
    </script>
</body>
</html>
"""

# ----------------------------------------------------
# --- 5. WI-FI CONNECTION (ORIGINAL / DYNAMIC IP) ---
# ----------------------------------------------------
print("Connecting to Wi-Fi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# NO STATIC IP. Just connecting.
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

# Wait for connection
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print("  ...waiting for connection")
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('Network connection failed')
else:
    ip = wlan.ifconfig()[0]
    print(f"✅ Connected on http://{ip}") # This IP will change every time!

# ----------------------------------------------------
# --- 6. START GPS THREAD ---
# ----------------------------------------------------
_thread.start_new_thread(gps_reader_thread, ())

# ----------------------------------------------------
# --- 7. MAIN WEB SERVER ---
# ----------------------------------------------------
print("Starting web server...")
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(5)

while True:
    try:
        cl, client_addr = s.accept()
        request = cl.recv(1024).decode('utf-8')
        
        if "GET /data" in request:
            # --- API ENDPOINT (for your Flutter app) ---
            cl.send('HTTP/1.1 200 OK\r\n')
            cl.send('Content-Type: application/json\r\n')
            cl.send('Access-Control-Allow-Origin: *\r\n')
            cl.send('Connection: close\r\n\r\n')
            response_json = json.dumps(gps_data)
            cl.send(response_json)
            
        elif "GET / " in request:
            # --- WEB PAGE ENDPOINT (for your browser) ---
            cl.send('HTTP/1.1 200 OK\r\n')
            cl.send('Content-Type: text/html\r\n')
            cl.send('Connection: close\r\n\r\n')
            cl.sendall(html_page)
            
        else:
            # 404 Not Found
            cl.send('HTTP/1.1 404 Not Found\r\n')
            cl.send('Connection: close\r\n\r\n')
        
        cl.close()
        
    except OSError as e:
        cl.close()
        print('Connection closed')
    except Exception as e:
        print(f"Server error: {e}")