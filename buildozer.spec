[app]

# (str) Title of your application
title = Efe Moto Diag

# (str) Package name
package.name = efemoto

# (str) Package domain (needed for android packaging)
package.domain = org.efe

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,html,js,css

# (str) Application version
version = 1.0

# (list) Application requirements
# CRITICAL: eventlet kaldırıldı; obd ve pyserial kütüphanelerinin Android'de sorunsuz 
# derlenebilmesi için 'setuptools' bağımlılığı eklendi.
requirements = python3,setuptools,flask,flask-socketio,python-socketio,obd,pyserial

# (str) Supported orientations
orientation = portrait

# (bool) Use fullscreen mode or not
fullscreen = 0

# =============================================================================
# Android Specific Configurations
# =============================================================================

# (list) Permissions
# CRITICAL: Android 12 ve üzeri güncel telefonlarda OBD2 Bluetooth cihazlarını 
# tarayabilmeniz ve bağlanabilmeniz için gerekli tüm modern izinler eklendi.
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, ACCESS_FINE_LOCATION

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 24

# (list) Supported architectures
# İlk derlemede hata payını en aza indirmek için sadece modern 64-bit mimari hedeflendi.
android.archs = arm64-v8a

# (str) The Android bootstrap type to use
# Flask/Web arayüzünüzün çalışması için WebView altyapısı aktiftir.
p4a.bootstrap = webview
