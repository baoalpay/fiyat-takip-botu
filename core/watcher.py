"""
core/watcher.py - Geliştirilmiş Çoklu Site Fiyat Takip Sistemi
"""
import time
from datetime import datetime
from scraper.trendyol import check_trendyol
from scraper.hepsiburada import check_hepsiburada
from alert.telegram import send_message
from core.storage import get_product, update_product


class PriceWatcher:
    """
    Fiyat takip sınıfı - Çoklu site desteği ile
    """
    
    def __init__(self, telegram_enabled=True, verbose=True):
        """
        Args:
            telegram_enabled: Telegram bildirimleri açık mı?
            verbose: Detaylı çıktı göster
        """
        self.telegram_enabled = telegram_enabled
        self.verbose = verbose
        self.stats = {
            "total_checked": 0,
            "price_drops": 0,
            "price_increases": 0,
            "no_change": 0,
            "errors": 0
        }
    
    def detect_site(self, url):
        """URL'den hangi site olduğunu belirle"""
        url_lower = url.lower()
        
        if "trendyol.com" in url_lower:
            return "trendyol"
        elif "hepsiburada.com" in url_lower:
            return "hepsiburada"
        # Gelecek siteler buraya eklenecek:
        # elif "n11.com" in url_lower:
        #     return "n11"
        else:
            return "unknown"
    
    def fetch_current_data(self, url, site):
        """
        Site'ye özel scraper'ı çağırır
        """
        try:
            if site == "trendyol":
                return check_trendyol(url)
            elif site == "hepsiburada":
                return check_hepsiburada(url)
            else:
                if self.verbose:
                    print(f"⚠️ Desteklenmeyen site: {site}")
                return None
        except Exception as e:
            if self.verbose:
                print(f"❌ Scraper hatası: {e}")
            return None
    
    def send_notification(self, message):
        """
        Telegram bildirimi gönder (sadece aktifse)
        """
        if self.telegram_enabled:
            try:
                send_message(message)
                if self.verbose:
                    print("✉️ Telegram bildirimi gönderildi")
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ Telegram hatası: {e}")
    
    def compare_prices(self, url, current_data, old_data):
        """
        Fiyatları karşılaştır ve gerekirse bildirim gönder
        """
        product_name = current_data['name']
        current_price = current_data['price']
        
        if not current_price or current_price <= 0:
            if self.verbose:
                print("❌ Geçersiz fiyat, atlanıyor.")
            return "error"
        
        # İlk kayıt
        if not old_data:
            if self.verbose:
                print(f"🆕 Yeni ürün eklendi: {current_price} TL")
            
            msg = (
                f"🆕 <b>Takip Başladı</b>\n\n"
                f"📦 <b>{product_name}</b>\n"
                f"💰 Fiyat: {current_price} TL\n\n"
                f"🔗 <a href='{url}'>Ürüne Git</a>"
            )
            self.send_notification(msg)
            return "new"
        
        # Fiyat karşılaştırması
        old_price = old_data.get('price', 0)
        
        # --- HATA DÜZELTME: SIFIRA BÖLME KORUMASI ---
        # Eğer eski fiyat 0 ise (hatalı çekimse), hesaplama yapmadan güncelle
        if old_price == 0:
            if self.verbose:
                print(f"🆕 Fiyat ilk kez geçerli olarak güncellendi: {current_price} TL")
            # Bildirim atmaya gerek yok, sessizce güncelle
            return "updated"

        if current_price < old_price:
            # 🔻 FİYAT DÜŞTÜ
            diff = old_price - current_price
            discount_percent = (diff / old_price) * 100
            
            if self.verbose:
                print(f"📉 FİYAT DÜŞTÜ: {old_price} TL → {current_price} TL (-%{discount_percent:.1f})")
            
            msg = (
                f"📉 <b>FİYAT DÜŞTÜ!</b>\n\n"
                f"📦 <b>{product_name}</b>\n\n"
                f"💰 Eski: <s>{old_price} TL</s>\n"
                f"✅ Yeni: <b>{current_price} TL</b>\n"
                f"🔻 İndirim: {diff:.2f} TL (%{discount_percent:.1f})\n\n"
                f"🔗 <a href='{url}'>Hemen Al</a>"
            )
            self.send_notification(msg)
            self.stats["price_drops"] += 1
            return "drop"
        
        elif current_price > old_price:
            # 📈 FİYAT YÜKSELDİ
            diff = current_price - old_price
            increase_percent = (diff / old_price) * 100
            
            if self.verbose:
                print(f"📈 Fiyat yükseldi: {old_price} TL → {current_price} TL (+%{increase_percent:.1f})")
            
            self.stats["price_increases"] += 1
            return "increase"
        
        else:
            # ➖ FİYAT AYNI
            if self.verbose:
                print(f"➖ Fiyat değişmedi: {current_price} TL")
            
            self.stats["no_change"] += 1
            return "same"
    
    def check_single_url(self, url):
        """
        Tek bir URL'i kontrol et
        """
        self.stats["total_checked"] += 1
        
        # Site tespiti
        site = self.detect_site(url)
        
        if self.verbose:
            site_emoji = "🟠" if site == "trendyol" else "🔵" if site == "hepsiburada" else "⚪"
            print(f"\n{site_emoji} [{site.upper()}] Kontrol ediliyor...")
            print(f"🔗 {url[:70]}...")
            print("-" * 60)
        
        # Veri çekme
        current_data = self.fetch_current_data(url, site)
        
        if not current_data:
            if self.verbose:
                print("❌ Veri alınamadı")
            self.stats["errors"] += 1
            return None
        
        # Eski veriyi al
        old_data = get_product(url)
        
        # Fiyat karşılaştırması
        status = self.compare_prices(url, current_data, old_data)
        
        # Veriyi güncelle
        update_product(url, current_data)
        
        if self.verbose:
            print(f"✅ İşlem tamamlandı")
        
        return {
            "url": url,
            "site": site,
            "status": status,
            "current_price": current_data.get("price"),
            "product_name": current_data.get("name")
        }
    
    def check_all_urls(self, urls):
        """
        Tüm URL'leri kontrol et (ana fonksiyon)
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"🚀 FİYAT TAKİP SİSTEMİ BAŞLATILDI")
            print(f"{'='*60}")
            print(f"📦 Toplam Ürün: {len(urls)}")
            print(f"🕐 Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")
        
        results = []
        
        for i, url in enumerate(urls, 1):
            if self.verbose:
                print(f"[{i}/{len(urls)}]", end=" ")
            
            result = self.check_single_url(url)
            
            if result:
                results.append(result)
            
            # Rate limiting (son ürün değilse bekle)
            if i < len(urls):
                if self.verbose:
                    print("⏳ 2 saniye bekleniyor...\n")
                time.sleep(2)
        
        # Özet rapor
        self._print_summary()
        
        return results
    
    def _print_summary(self):
        """İstatistik özeti yazdır"""
        if not self.verbose:
            return
        
        print(f"\n{'='*60}")
        print(f"📊 KONTROL ÖZETİ")
        print(f"{'='*60}")
        print(f"✅ Başarılı: {self.stats['total_checked'] - self.stats['errors']}")
        print(f"❌ Hata: {self.stats['errors']}")
        print(f"📉 Fiyat Düşüşü: {self.stats['price_drops']}")
        print(f"📈 Fiyat Artışı: {self.stats['price_increases']}")
        print(f"➖ Değişiklik Yok: {self.stats['no_change']}")
        print(f"{'='*60}\n")
    
    def reset_stats(self):
        """İstatistikleri sıfırla"""
        self.stats = {
            "total_checked": 0,
            "price_drops": 0,
            "price_increases": 0,
            "no_change": 0,
            "errors": 0
        }


# ============================================
# ESKI SÜRÜMLE UYUMLULUK (Backward Compatible)
# ============================================

# Global watcher instance
_default_watcher = PriceWatcher(telegram_enabled=True, verbose=True)

def check_all_urls(urls):
    """
    Eski kodlarla uyumluluk için sarmalayıcı fonksiyon
    """
    return _default_watcher.check_all_urls(urls)

def check_single_url(url):
    """
    Tek URL kontrol fonksiyonu
    """
    return _default_watcher.check_single_url(url)