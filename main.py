from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import obd
import threading
import time

# === TÜM YAMAHA ARIZA KODLARI ===
YAMAHA_DTC = {
    "12": "Krank Pozisyon Sensörü", "13": "Emme Hava Basınç Sensörü",
    "14": "Emme Hava Basınç Sensörü (Vakum Hortumu)", "15": "Gaz Kelebeği Pozisyon Sensörü (TPS)",
    "16": "Gaz Kelebeği Pozisyon Sensörü (Takılı Kalmış)", "19": "Ateşleme Sinyali (ECU'ya Gitmiyor)",
    "22": "Emme Hava Sıcaklık Sensörü", "24": "O2 Sensörü", "30": "Latch Up (ECU Kilitleme)",
    "33": "Ateşleme Bobini #1", "34": "Ateşleme Bobini #2", "37": "Rölanti Kontrol (ISC)",
    "39": "Yakıt Enjektörü", "41": "Yatma Sensörü (Tip Over)", "42": "Ön Tekerlek Sensörü (ABS)",
    "44": "ECU Okuma/Yazma Hatası", "46": "Şarj Voltajı Anormal", "50": "ECU Bellek Arızası",
    "61": "Rölanti Kontrol (ISC) Devresi",
    # Standart OBD-II P Kodları
    "P0107": "MAP Sensörü Düşük Voltaj", "P0108": "MAP Sensörü Yüksek Voltaj",
    "P0115": "Motor Soğutma Suyu Sensörü", "P0117": "Soğutma Suyu Sensörü Düşük Voltaj",
    "P0118": "Soğutma Suyu Sensörü Yüksek Voltaj", "P0122": "Gaz Kelebeği Pozisyon Sensörü Düşük Voltaj",
    "P0335": "Krank Mili Pozisyon Sensörü Arızası", "P0500": "Araç Hız Sensörü Arızası",
    "P0505": "Rölanti Kontrol Sistemi", "P0511": "Rölanti Hava Kontrol (IAC) Devresi",
    "P0560": "Sistem Voltajı", "P0601": "ECU Bellek Hatası",
    "P1604": "Immobilizer Kod Hatası", "P2101": "Gaz Kelebeği Aktüatör Arızası",
    "P2135": "Gaz Kelebeği Sensörleri Korelasyon Hatası", "U0100": "ECM ile İletişim Kaybı",
}

class EfeMotoApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.status_label = Label(text="Bağlantı Bekleniyor...", font_size=20)
        self.data_label = Label(text="Veri Yok", font_size=30)
        self.btn_connect = Button(text="BAĞLAN", size_hint=(1, 0.2))
        self.btn_connect.bind(on_press=self.connect_obd)
        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.data_label)
        self.layout.add_widget(self.btn_connect)
        return self.layout

    def connect_obd(self, instance):
        self.status_label.text = "Bağlanıyor..."
        threading.Thread(target=self._connect_logic, daemon=True).start()

    def _connect_logic(self):
        try:
            self.connection = obd.OBD("socket://192.168.0.10:35000", fast=False)
            if self.connection.is_connected():
                self.status_label.text = "ECU ONLINE"
                Clock.schedule_interval(self.update_data, 0.5)
            else:
                self.status_label.text = "Bağlantı Başarısız"
        except Exception as e:
            self.status_label.text = f"Hata: {e}"

    def update_data(self, dt):
        rpm = self.connection.query(obd.commands.RPM)
        speed = self.connection.query(obd.commands.SPEED)
        self.data_label.text = f"RPM: {rpm.value}\nHız: {speed.value}"

if __name__ == '__main__':
    EfeMotoApp().run()
