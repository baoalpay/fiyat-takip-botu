import os
from dotenv import load_dotenv

# .env dosyasını bul ve yükle
load_dotenv()

# Değişkenleri alıp Python içinde kullanıma hazır hale getiriyoruz
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Varsayılan kontrol süresi (eğer .env'de yoksa 5 dakika olsun)
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 5))

# Güvenlik Kontrolü: Eğer şifreler yoksa programı durdur
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("HATA: .env dosyasında Token veya Chat ID eksik! Lütfen dosyayı kontrol et.")