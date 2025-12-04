import requests
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_message(text):
    """
    Belirtilen metni Telegram üzerinden kullanıcıya gönderir.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"  # Mesajlarda kalın/italik yazı kullanabilmek için
    }
    
    try:
        # İsteği gönder
        response = requests.post(url, json=payload)
        response.raise_for_status() # Eğer hata varsa (örn. internet yoksa) uyarı ver
        print(f"✅ Telegram mesajı gönderildi: {text}")
        return True
    except Exception as e:
        print(f"❌ Mesaj gönderilemedi: {e}")
        return False