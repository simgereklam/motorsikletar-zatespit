[app]
title = Efe Moto Diag
package.name = efemoto
package.domain = org.efe
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,js,css
version = 1.0

# Bağımlılıklar (setuptools ve flask entegrasyonu eklendi)
requirements = python3,setuptools,flask,flask-socketio,python-socketio,obd,pyserial

orientation = portrait
fullscreen = 0

# Android 12+ modern Bluetooth ve İnternet izinleri
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, ACCESS_FINE_LOCATION

# Ubuntu 26 / Modern Android Derleme Standartları
android.api = 33
android.minapi = 24
android.ndk = 29
android.archs = arm64-v8a

# Python-for-Android Geliştirme Dalı (Ubuntu 26 çökmesini önleyen en kritik ayar)
p4a.branch = develop
p4a.bootstrap = webview
