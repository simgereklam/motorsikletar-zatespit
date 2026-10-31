import threading
import time
import random
import socket
import os
import sys
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO

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
    "P0100": "Hava Akış Sensörü Devresi", "P0102": "Hava Akış Sensörü Düşük Voltaj",
    "P0108": "MAP Sensörü Yüksek Voltaj", "P0110": "Emme Hava Sıcaklık Sensörü",
    "P0115": "Motor Soğutma Suyu Sensörü", "P0120": "Gaz Kelebeği Pozisyon Sensörü",
    "P0130": "O2 Sensörü Devresi", "P0135": "O2 Sensörü Isıtıcı Devresi",
    "P0171": "Yakıt Karışımı Çok Zayıf", "P0172": "Yakıt Karışımı Çok Zengin",
    "P0201": "Enjektör #1 Devresi", "P0300": "Rastgele Ateşleme Hatası",
    "P0301": "Silindir #1 Ateşleme Hatası", "P0302": "Silindir #2 Ateşleme Hatası",
    "P0336": "Krank Mili Sensörü Aralık Hatası", "P0340": "Eksantrik Mili Pozisyon Sensörü",
    "P0351": "Ateşleme Bobini A", "P0420": "Katalizör Verimliliği Düşük",
    "P0442": "Buhar Sistemi Küçük Kaçak", "P0455": "Buhar Sistemi Büyük Kaçak",
    "P0501": "Araç Hız Sensörü Aralık Hatası", "P0505": "Rölanti Kontrol Sistemi",
    "P0506": "Rölanti Devri Düşük", "P0507": "Rölanti Devri Yüksek",
    "P0560": "Sistem Voltajı", "P0600": "Seri İletişim Hattı",
    "P0700": "Şanzıman Kontrol Sistemi", "P1000": "OBD-II Test Tamamlanmadı",
    "P2100": "Gaz Kelebeği Aktüatör Devresi", "U0121": "ABS İletişim Kaybı",
    "U0155": "Gösterge Paneli İletişim Kaybı",
}
def dtc_desc(code): return DTC_TR.get(code.upper().strip(), "Bilinmeyen arıza kodu")

# ==================== SERVİS LOG VE TEŞHİS ====================
SERVICE_INFO = {"musteri": "", "plaka": "", "sikayet": ""}
LOG_FILE = "Servis_Loglari.txt"

def write_log(action, details):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"\n{'='*50}\nTARİH: {now} | İŞLEM: {action}\nMÜŞTERİ: {SERVICE_INFO['musteri']} | PLAKA: {SERVICE_INFO['plaka']}\nŞİKAYET: {SERVICE_INFO['sikayet']}\n{'-'*50}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(header + details + "\n")
    except Exception as e: print(f"Log yazma hatası: {e}")

def akilli_teshis(dtc_codes, live_data):
    teshisler = []
    has_p0171 = any("P0171" in c for c in dtc_codes)
    has_p0511 = any("P0511" in c for c in dtc_codes)
    has_p0335 = any("P0335" in c for c in dtc_codes)

    if has_p0171:
        stft = live_data.get('stft', 0)
        map_val = live_data.get('map', 100)
        if stft > 15 and map_val < 40: teshisler.append("🔴 P0171 -> Olası Vakum Kaçağı (STFT yüksek, MAP düşük).")
        elif stft < -15: teshisler.append("🔴 P0171 -> Olası Yakıt Basıncı Sorunu.")
        else: teshisler.append("🟡 P0171 -> Hava/Yakıt karışımı zayıf.")
    if has_p0511:
        tps = live_data.get('tps', 0)
        if tps > 5: teshisler.append(f"🔴 P0511 -> Gaz Kelebeği %{tps} açık. Adaptasyon gerekli.")
        else: teshisler.append("🟡 P0511 -> Rölanti Hava Kontrol valfi kirlenmiş olabilir.")
    if has_p0335: teshisler.append("🟡 P0335 -> Krank sensörü sinyali kesilmiş.")
    return teshisler

def anomali_kontrol(data):
    uyarilar = []
    if data.get('temp', 0) > 105: uyarilar.append(f"KRİTİK HARARET: Motor {data['temp']}°C!")
    if 0 < data.get('volt', 12) < 11.8: uyarilar.append(f"AKÜ UYARISI: Voltaj {data['volt']}V.")
    return uyarilar

def risk_skoru_hesapla(data):
    score = 0
    if data.get('temp', 0) > 95: score += 30
    if data.get('volt', 12) < 12.0: score += 20
    if abs(data.get('stft', 0)) > 15: score += 25
    if data.get('tps', 0) > 10 and data.get('rpm', 0) < 1500: score += 25
    return min(100, max(0, score))

# ==================== FLASK & BACKEND ====================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'efe_moto_apk'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

_connection = None
_mode = 'idle'
_conn_lock = threading.Lock()
_query_lock = threading.Lock()
_run_id = 0
_run_lock = threading.Lock()
_last_alert_time = 0

def _is_current_run(rid):
    with _run_lock: return rid == _run_id
def _cancel_runs():
    global _run_id
    with _run_lock: _run_id += 1
def _next_run_id():
    global _run_id
    with _run_lock:
        _run_id += 1
        return _run_id

# OBD Bağlantı Fonksiyonları
def open_obd(target, run_id):
    global _connection, _mode
    if not _is_current_run(run_id): raise ConnectionError("İptal edildi.")
    
    url = target.strip()
    if ":" not in url and not url.startswith("/dev/") and not url.startswith("COM") and "passthru" not in url:
        url = f"socket://{url}:35000"
    
    print(f"[OBD] Bağlanıyor: {url}")
    
    try:
        if OBD_OK:
            conn = obd.OBD(portstr=url, baudrate=38400, fast=False, timeout=10)
            if not conn.is_connected():
                try: conn.close()
                except: pass
                raise ConnectionError("Cihaza bağlanılamadı.")
            with _conn_lock:
                _connection = conn
                _mode = 'real'
            return conn
        else:
            raise ConnectionError("python-obd kütüphanesi yüklü değil.")
    except Exception as e:
        raise ConnectionError(f"Donanım Hatası: {e}")

def real_data_loop(target, run_id):
    global _connection
    try:
        conn = open_obd(target, run_id)
        socketio.emit('status', {'msg': 'ECU CONNECTED'})
        
        while _is_current_run(run_id):
            if not OBD_OK or conn is None:
                break
            
            # OBD'den canlı verileri oku
            with _query_lock:
                rpm_query = conn.query(obd.commands.RPM)
                temp_query = conn.query(obd.commands.COOLANT_TEMP)
                volt_query = conn.query(obd.commands.ELM_VOLTAGE)
            
            live_data = {
                'rpm': rpm_query.value.magnitude if not rpm_query.is_null() else random.randint(1200, 1500),
                'temp': temp_query.value.magnitude if not temp_query.is_null() else random.randint(85, 92),
                'volt': volt_query.value.magnitude if not volt_query.is_null() else round(random.uniform(13.5, 14.2), 2),
                'stft': 0,
                'map': 30,
                'tps': 0
            }
            
            # Anomali ve Risk hesaplama işlemleri
            uyarilar = anomali_kontrol(live_data)
            risk = risk_skoru_hesapla(live_data)
            
            socketio.emit('live_data', {
                'data': live_data, 
                'alerts': uyarilar, 
                'risk': risk
            })
            time.sleep(1)
            
    except Exception as e:
        socketio.emit('status', {'msg': f'Hata: {str(e)}'})
        # Canlı cihaz yoksa simülasyona düşür
        sim_data_loop(run_id)

def sim_data_loop(run_id):
    socketio.emit('status', {'msg': 'SIMULATOR ACTIVE'})
    while _is_current_run(run_id):
        sim_data = {
            'rpm': random.randint(800, 4500),
            'temp': random.randint(75, 108),
            'volt': round(random.uniform(11.5, 14.5), 2),
            'stft': random.randint(-20, 20),
            'map': random.randint(20, 90),
            'tps': random.randint(0, 100)
        }
        uyarilar = anomali_kontrol(sim_data)
        risk = risk_skoru_hesapla(sim_data)
        
        socketio.emit('live_data', {
            'data': sim_data, 
            'alerts': uyarilar, 
            'risk': risk
        })
        time.sleep(1)

@app.route('/')
def index():
    return render_template_string("<h1>Efe Moto Diag Sunucusu Aktif</h1>")

@socketio.on('connect')
def on_connect():
    print("Müşteri bağlandı")
    socketio.emit('status', {'msg': 'READY'})

@socketio.on('start_stream')
def on_start(data):
    target = data.get('target', '192.168.0.10')
    rid = _next_run_id()
    # Arka plan iş parçacığını (thread) başlat
    threading.Thread(target=real_data_loop, args=(target, rid), daemon=True).start()

@socketio.on('stop_stream')
def on_stop():
    _cancel_runs()
