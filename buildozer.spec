[app]
title = Efe Moto Diag
package.name = efemoto
package.domain = org.efe
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,js,css
version = 1.0
requirements = python3,flask,flask-socketio,python-socketio,eventlet,obd,pyserial
orientation = portrait
fullscreen = 0

# Android izinleri
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT

# WebView arayüzü için
p4a.bootstrap = webview
