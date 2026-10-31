[app]
title = Efe Moto Diag
package.name = efemoto
package.domain = org.efe
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,js,css
version = 1.0

# Sadece gerekli en kararlı paketler bırakıldı
requirements = python3,kivy,pyjnius,setuptools,flask,flask-socketio,python-socketio,obd,pyserial

orientation = portrait
fullscreen = 1

# Android İzinleri
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, ACCESS_FINE_LOCATION

android.api = 33
android.minapi = 24
android.archs = arm64-v8a

# ÇÖZÜM: Hata vermeyen kesin ve kararlı ana şablon
p4a.bootstrap = sdl2
