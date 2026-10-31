import os
import time
import threading
from flask import Flask, render_template_string
from flask_socketio import SocketIO

# Kivy ve Android Yerel Kütüphaneleri
from kivy.app import App
from jnius import autoclass

try:
    import obd
    OBD_OK = True
except ImportError:
    OBD_OK = False

# ==================== GELİŞMİŞ DTC VERİTABANI ====================
DTC_TR = {
    "13": "Pulsar Bobin Sinyali Hatası", "14": "Krank Konum Sensörü Sinyali Hatası",
    "15": "Motor Sıcaklık Sensörü Sinyali Hatası", "17": "Vuruntu Sensörü Hatası",
    "18": "Gaz Kelebeği Konum Sensörü Sinyali Hatası", "19": "Akü Voltajı Hatası",
    "22": "Atmosferik Basınç Sensörü Sinyali Hatası", "23": "Emme Havası Sıcaklık Sensörü Sinyali Hatası",
    "24": "Eksantrik Mili (EX) Konum Sensörü Hatası", "25": "Yakıt Basıncı Sensörü Sinyali Hatası",
    "26": "Enjektör Sinyali Hatası", "27": "Yakıt Filtresinde Su Hatası",
    "28": "Vites Konum Anahtarı Sinyali Hatası", "29": "Emme Basınç Sensörü Hatası",
    "30": "Latch Up (ECU Kilitleme) Tespit Edildi", "33": "Silindir #1 Ateşleme Bobini Arızası",
    "34": "Silindir #2 Ateşleme Bobini Arızası", "39": "Yağ Basıncı Sensörü Hatası",
    "41": "Hız Sensörü Sinyali Yok", "42": "Vites Konum Anahtarı Açık/ Kısa Devre",
    "43": "Yakıt Sistemi Voltajı Anormal", "44": "EEPROM Okuma/Yazma Hatası",
    "46": "Şarj Voltajı Anormal", "50": "ECU Bellek Arızası", "70": "Motor Rölanti Durdurma Hatası",
    "P0030": "O2 Sensörü Isıtıcı Devresi Arızası", "P0107": "MAP Sensörü Düşük Voltaj",
    "P0113": "Emme Hava Sıcaklık Sensörü Yüksek Voltaj (IAT)",
    "P0117": "Motor Soğutma Suyu Sensörü Düşük Voltaj",
    "P0118": "Motor Soğutma Suyu Sıcaklık Sensörü Yüksek Voltaj (ECT)",
    "P0122": "Gaz Kelebeği Pozisyon Sensörü Düşük Voltaj",
    "P0335": "Krank Mili Pozisyon Sensörü Arızası", "P0500": "Araç Hız Sensörü Arızası",
    "P0511": "Rölanti Hava Kontrol (IAC) Devresi Arızası",
    "P0562": "Sistem Gerilimi Düşük", "P0601": "ECU Bellek Hatası",
    "P1604": "Immobilizer Kod Hatası", "P2101": "Gaz Kelebeği Aktüatör Arızası",
    "P2135": "Gaz Kelebeği Sensörleri Korelasyon Hatası", "U0100": "ECM ile İletişim Kaybı",
}

# ==================== FLASK & SOCKETIO BACKEND ====================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'efe_moto_apk'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@app.route('/')
def index():
    return render_template_string("<h1>Efe Moto Diag Sunucusu Aktif</h1>")

@socketio.on('connect')
def on_connect():
    socketio.emit('status', {'msg': 'READY'})

@socketio.on('start_stream')
def on_start(data):
    target = data.get('target', '192.168.0.10')
    if OBD_OK:
        try:
            conn = obd.OBD(portstr=target, baudrate=38400, timeout=5)
            if conn.is_connected():
                socketio.emit('status', {'msg': 'ECU CONNECTED'})
            else:
                socketio.emit('status', {'msg': 'CONN FAILED'})
        except Exception as e:
            socketio.emit('status', {'msg': f'ERROR: {str(e)}'})

# ==================== KIVY ANDROID WEBVIEW SARMALAYICI ====================
def start_flask():
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)

class EfeMotoApp(App):
    def build(self):
        threading.Thread(target=start_flask, daemon=True).start()
        time.sleep(1)
        
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        
        activity = PythonActivity.mActivity
        webview = WebView(activity)
        webview.getSettings().setJavaScriptEnabled(True)
        webview.getSettings().setDomStorageEnabled(True)
        webview.setWebViewClient(WebViewClient())
        webview.loadUrl('http://127.0.0.1:5000')
        
        activity.setContentView(webview)

if __name__ == '__main__':
    EfeMotoApp().run()
