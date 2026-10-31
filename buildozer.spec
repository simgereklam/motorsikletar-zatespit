[app]
title = Efe Moto Diag
package.name = efemoto
package.domain = org.efe
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,js,css
version = 1.0

# Kararlı bağımlılıklar
requirements = python3,setuptools,flask,flask-socketio,python-socketio,obd,pyserial

orientation = portrait
fullscreen = 0

# Android 12+ modern Bluetooth ve İnternet izinleri
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, ACCESS_FINE_LOCATION

android.api = 33
android.minapi = 24
android.archs = arm64-v8a
p4a.bootstrap = webview
