import time
import schedule
import os
from core.watcher import check_all_urls

# Linklerin okunacağı dosya
URL_FILE = "urls.txt"

def get_urls_from_file():
    """urls.txt dosyasındaki linkleri okur ve temizler."""
    if not os.path.exists(URL_FILE):
        print(f"⚠️ HATA: {URL_FILE} dosyası bulunamadı!")
        return []
    
    with open(URL_FILE, "r", encoding="utf-8") as f:
        # Satır satır oku, boşlukları temizle, boş satırları atla
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return urls

def job():
    print("-" * 50)
    print(f"🕒 Otomatik Kontrol Başladı: {time.strftime('%H:%M:%S')}")
    
    # Her döngüde dosyayı tekrar oku (Böylece program çalışırken link ekleyebilirler!)
    current_urls = get_urls_from_file()
    
    if current_urls:
        check_all_urls(current_urls)
    else:
        print("❌ Takip listesi (urls.txt) boş!")
    
    print("-" * 50)

if __name__ == "__main__":
    print("🚀 FİYAT TAKİP BOTU BAŞLATILDI")
    print("📂 Linkler 'urls.txt' dosyasından okunuyor...")
    
    # İlk çalıştırma
    job()

    # Zamanlayıcı (10 Dakika)
    schedule.every(10).minutes.do(job)

    print(f"\n✅ Bot aktif. 10 dakikada bir kontrol edecek.")
    print(f"💡 İPUCU: Program çalışırken 'urls.txt' dosyasına yeni link ekleyip kaydedebilirsiniz.")
    print("❌ Çıkış için: CTRL + C")
    
    while True:
        schedule.run_pending()
        time.sleep(1)