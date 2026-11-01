[app]
title = Efe Moto Diag
package.name = efemoto
package.domain = org.efe
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,obd,pyserial
orientation = portrait
fullscreen = 0

# Android izinleri
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, BLUETOOTH, BLUETOOTH_ADMIN

# Kivy uygulaması olduğu için bootstrap'i kivy yapıyoruz
p4a.bootstrap = sdl2
