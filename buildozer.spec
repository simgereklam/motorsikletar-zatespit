
[app]

title = Efe Moto Diag

package.name = efemoto
package.domain = org.efe

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,html,js,css,json

version = 1.0

requirements = python3,kivy,pyjnius,setuptools,flask,flask-socketio,python-socketio,obd,pyserial

orientation = portrait
fullscreen = 1

android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION

android.api = 33
android.minapi = 24

android.archs = arm64-v8a

p4a.bootstrap = sdl2

android.accept_sdk_license = True

android.allow_backup = False

android.enable_androidx = True

[buildozer]

log_level = 2
warn_on_root = 1
