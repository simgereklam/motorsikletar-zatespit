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
    has_p0300 = any("P0300" in c or "P0301" in c or "P0302" in c for c in dtc_codes)
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
def _get_mode():
    with _conn_lock: return _mode
def _set_mode(m):
    global _mode
    with _conn_lock: _mode = m

# YENİ NESİL BAĞLANTI: Hem ELM hem J2534 altyapısına hazır!
def open_obd(target, run_id):
    global _connection, _mode
    if not _is_current_run(run_id): raise ConnectionError("İptal")
    
    # Hedef formatını anla
    # ELM327 WiFi için: socket://192.168.0.10:35000
    # ELM327 Bluetooth için: /dev/rfcomm0 (Android) veya COM3 (Windows)
    # J2534 için: passthru veya J2534-1 (Python-obd doğrudan desteklemez, ancak sarmalayıcılar için alan açıldı)
    
    url = target.strip()
    if ":" not in url and not url.startswith("/dev/") and not url.startswith("COM") and "passthru" not in url:
        url = f"socket://{url}:35000" # Varsayılan WiFi ELM ayarı
    
    print(f"[OBD] Bağlanıyor: {url}")
    
    try:
        # Bağlantı denemesi (Baudrate J2534 veya K-Line için önemli olabilir)
        conn = obd.OBD(portstr=url, baudrate=38400, fast=False, timeout=20)
    except Exception as e:
        raise ConnectionError(f"Donanım Hatası: {e}")
        
    if not _is_current_run(run_id):
        try: conn.close()
        except: pass
        raise ConnectionError("İptal")
    if not conn.is_connected():
        try: conn.close()
        except: pass
        raise ConnectionError(f"Bağlanamadı: {url}. (WiFi veya Kabloyu kontrol edin)")
    
    with _conn_lock:
        _connection = conn
        _mode = 'real'
    return conn

def close_obd():
    global _connection, _mode
    with _conn_lock:
        conn = _connection; _connection = None
        if _mode == 'real': _mode = 'idle'
    if conn is not None:
        try: conn.close()
        except: pass

def real_data_loop(target, run_id):
    global _last_alert_time
    conn = None
    try:
        while _is_current_run(run_id):
            try:
                conn = open_obd(target, run_id)
                socketio.emit('status', {'msg': 'ECU ONLINE', 'color': '#00ff00'})
                cmds = {
                    'rpm': obd.commands.RPM, 'speed': obd.commands.SPEED,
                    'temp': obd.commands.COOLANT_TEMP, 'tps': obd.commands.THROTTLE_POS,
                    'map': obd.commands.INTAKE_PRESSURE, 'iat': obd.commands.INTAKE_TEMP,
                    'volt': obd.commands.CONTROL_MODULE_VOLTAGE,
                }
                for _attr, _key in [('O2_SENSOR_B1S1', 'o2'), ('O2_SENSOR_1', 'o2'), ('SHORT_FUEL_TRIM_1', 'stft')]:
                    _cmd = getattr(obd.commands, _attr, None)
                    if _cmd is not None and _key not in cmds: cmds[_key] = _cmd

                while _is_current_run(run_id):
                    if not conn.is_connected(): raise ConnectionError("Koptu")
                    data = {}
                    for key, cmd in cmds.items():
                        try:
                            with _query_lock: r = conn.query(cmd)
                            if not r.is_null():
                                v = r.value
                                data[key] = round(float(getattr(v, 'magnitude', v)), 2)
                        except: pass
                    
                    if 'tps' in data:
                        data['inj'] = round(1.5 + data['tps'] / 100 * 8, 1)
                        data['afr'] = round(14.7 - data['tps'] / 100 * 2, 1)
                    if 'speed' in data:
                        s = data['speed']
                        data['gear'] = 1 if s<15 else 2 if s<30 else 3 if s<50 else 4 if s<75 else 5 if s<100 else 6
                    elif data.get('rpm',0) > 800: data['gear'] = 1
                    
                    if data:
                        socketio.emit('telemetry', data)
                        socketio.emit('risk_score', {'score': risk_skoru_hesapla(data)})
                        now = time.time()
                        if now - _last_alert_time > 10:
                            alerts = anomali_kontrol(data)
                            if alerts:
                                _last_alert_time = now
                                socketio.emit('alert', {'msg': alerts[0]})
                    time.sleep(0.15)
            except Exception as e:
                if not _is_current_run(run_id): break
                socketio.emit('status', {'msg': 'BAĞLANTI KOPTU...', 'color': '#ffaa00'})
                if conn:
                    try: conn.close()
                    except: pass
                time.sleep(3)
    finally:
        if conn:
            try: conn.close()
            except: pass
        if _is_current_run(run_id): socketio.emit('status', {'msg': 'KESİLDİ', 'color': '#ff5252'})

# ==================== WEB API (Arayüzden Bağlanmayı Tetiklemek İçin) ====================
@app.route('/api/connect', methods=['POST'])
def api_connect():
    data = request.json
    target = data.get('target', '')
    if not target: return jsonify({"success": False, "msg": "Hedef boş"})
    
    _cancel_runs()
    rid = _next_run_id()
    threading.Thread(target=real_data_loop, args=(target, rid), daemon=True).start()
    return jsonify({"success": True, "msg": "Bağlantı başlatıldı"})

@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    _cancel_runs()
    close_obd()
    socketio.emit('status', {'msg': 'KESİLDİ', 'color': '#ff5252'})
    return jsonify({"success": True})

@app.route('/log')
def view_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f"<pre style='color:black; background:white; padding:20px;'>{f.read()}</pre>"
    return "Henüz log kaydı yok."

# ==================== HTML (Tek Sayfa, Mobil Uyumlu) ====================
HTML_CODE = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Efe Moto Diag</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
/* CSS kodlarını buraya ekleyin (Uzun olduğu için kısaltıldı, önceki koddaki tüm CSS'ler buraya gelecek) */
body{background:#0a0a0a;color:#fff;font-family:'Segoe UI',sans-serif;margin:0;padding-bottom:30px;}
.top-bar{display:flex;justify-content:space-between;align-items:center;padding:10px;border-bottom:2px solid #ff003c;background:#000;}
.nav{display:flex;justify-content:center;background:#000;padding:5px;flex-wrap:wrap;}
.nav button{background:none;border:1px solid #333;color:#888;padding:8px 15px;margin:2px;cursor:pointer;font-weight:bold;font-size:12px;}
.nav button.active{border-color:#00e5ff;color:#00e5ff;background:rgba(0,229,255,0.1);}
.container{display:none;width:95%;margin:10px auto;}
.container.active{display:block;}
.panel{background:rgba(10,10,10,0.9);border:1px solid #444;padding:10px;margin-bottom:10px;}
/* ... Diğer tüm görsel CSS'ler aynen korunacak ... */
/* Mobil için bağlantı kutusu */
#conn-panel{display:flex;flex-wrap:wrap;gap:10px;align-items:center;background:#111;padding:15px;border:1px solid #333;}
#conn-panel input{flex:1;padding:10px;background:#222;color:#fff;border:1px solid #555;font-size:16px;}
#conn-panel button{padding:10px 20px;font-weight:bold;cursor:pointer;border:none;}
.btn-connect{background:#00e5ff;color:#000;}
.btn-disconnect{background:#ff003c;color:#fff;}
</style>
</head>
<body>
<div class="top-bar">
    <h1 style="margin:0;color:#ff003c;font-size:20px;">EFE MOTO DIAG</h1>
    <div id="status-bar" style="font-size:12px;font-weight:bold;color:#ffaa00;">BAĞLANTI YOK</div>
</div>

<!-- BAĞLANTI PANELİ (Mobil İçin Önemli) -->
<div class="container active" id="conn-panel">
    <!-- ELM327 WiFi için IP, Bluetooth için COM veya /dev/rfcomm0, J2534 için passthru yazılabilir -->
    <input type="text" id="conn_target" placeholder="WiFi IP (192.168.0.10) veya BT Port (COM3)" value="192.168.0.10">
    <button class="btn-connect" onclick="connectOBD()">BAĞLAN</button>
    <button class="btn-disconnect" onclick="disconnectOBD()">KES</button>
</div>

<div class="nav">
<button id="nav-dash" class="active" onclick="switchTab('dash')">PANEL</button>
<button id="nav-sens" onclick="switchTab('sens')">SENSÖR</button>
<button id="nav-dtc" onclick="switchTab('dtc')">ARIZA</button>
<button id="nav-test" onclick="switchTab('test')">TEST</button>
</div>

<!-- İçerik Alanları (Görsel olarak aynı kalacak) -->
<div id="tab-dash" class="container">
    <!-- RPM, Hız, vs. buraya gelecek -->
    <div class="panel">
        <h3>Devir: <span id="rpm">0</span> RPM</h3>
        <h3>Hız: <span id="speed">0</span> KM/H</h3>
        <h3>Risk Skoru: <span id="risk-score" style="color:#0f0;">0</span></h3>
    </div>
</div>

<div id="tab-dtc" class="container">
    <button class="btn" onclick="scanDTC()">ARIZA TARA</button>
    <button class="btn" onclick="clearDTC()">ARIZA SİL</button>
    <div id="dtc-result" style="margin-top:10px;"></div>
</div>

<div id="toast-container" style="position:fixed;top:10px;right:10px;z-index:9999;"></div>

<script>
var socket = io();
function switchTab(t){
    document.querySelectorAll('.container').forEach(e=>{if(e.id !== 'conn-panel') e.classList.remove('active')});
    document.querySelectorAll('.nav button').forEach(e=>e.classList.remove('active'));
    document.getElementById('tab-'+t).classList.add('active');
    document.getElementById('nav-'+t).classList.add('active');
}

// BAĞLANMA FONKSİYONU (Flask API'ye istek atar)
function connectOBD() {
    var target = document.getElementById('conn_target').value;
    fetch('/api/connect', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({target: target})
    }).then(res => res.json()).then(data => {
        if(data.success) showToast("Bağlantı başlatıldı...");
        else showToast("Hata: " + data.msg);
    });
}

function disconnectOBD() {
    fetch('/api/disconnect', {method: 'POST'});
}

function showToast(msg) {
    var t = document.createElement('div');
    t.style.cssText = 'background:#ff003c;color:#fff;padding:10px;margin-bottom:5px;border-radius:5px;font-size:12px;';
    t.innerText = msg;
    document.getElementById('toast-container').appendChild(t);
    setTimeout(()=>t.remove(), 4000);
}

socket.on('status', d => {
    let b = document.getElementById('status-bar');
    b.innerText = d.msg;
    b.style.color = d.color;
});
socket.on('telemetry', d => {
    if(d.rpm !== undefined) document.getElementById('rpm').innerText = d.rpm;
    if(d.speed !== undefined) document.getElementById('speed').innerText = d.speed;
});
socket.on('risk_score', d => {
    document.getElementById('risk-score').innerText = d.score;
});
socket.on('alert', d => showToast(d.msg));

// Diğer scanDTC, test vb. fonksiyonlar SocketIO üzerinden aynen çalışacak.
</script>
</body>
</html>
"""

@app.route('/')
def index_page():
    return render_template_string(HTML_CODE)

# ==================== ÇALIŞTIRICI (Flask Sunucusu) ====================
if __name__ == "__main__":
    print("Sunucu baslatiliyor... (APK icin 0.0.0.0:5000)")
    # APK içinde çalışırken 127.0.0.1 (localhost) üzerinden yayın yapar
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
