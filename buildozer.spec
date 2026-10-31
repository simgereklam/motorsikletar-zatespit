[app]
title = Efe Moto Diag
package.name = efemoto
package.domain = org.efe
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,js,css
version = 1.0

# ÇÖZÜM: eventlet kaldırıldı, Android mimarisiyle uyumlu bağımlılıklar bırakıldı
requirements = python3,flask,flask-socketio,python-socketio,obd,pyserial

orientation = portrait
fullscreen = 0

# Android izinleri (Android 12+ Bluetooth tarama ve bağlantı izinleri optimize edildi)
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, ACCESS_FINE_LOCATION

# WebView arayüzü için bootstrap tanımı
p4a.bootstrap = webview
