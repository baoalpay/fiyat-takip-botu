from playwright.sync_api import sync_playwright
import json
import re
import time
from urllib.parse import urlparse, parse_qs, unquote

def check_hepsiburada(url):
    """
    HEPSİBURADA - BUKALEMUN MODU:
    - Elektronik (Standart) ve Moda (Sepete Özel) sayfalarına uyum sağlar.
    - "Sepete özel fiyat" yazısını görürse, onun yanındaki rakamı çeker.
    - Yükleme sorunlarına karşı daha dirençlidir.
    """
    try:
        # URL'den satıcı hedefi
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        target_seller = None
        if 'magaza' in params:
            target_seller = unquote(params['magaza'][0]).lower().replace('+', ' ').strip()
            print(f"🎯 Hedef Satıcı: {target_seller}")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False, 
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            print("⏳ Hepsiburada'ya gidiliyor...")
            try:
                page.goto(url, timeout=90000)
                print("💤 Sayfa yükleniyor...")
                # Networkidle bazen moda sayfalarında hiç durmaz (sürekli resim yüklenir),
                # bu yüzden domcontentloaded + süre daha güvenlidir.
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(4000)
            except:
                print("⚠️ Sayfa yükleme uyarısı (Devam ediliyor).")

            # --- 1. STOK KONTROLÜ ---
            try:
                if page.locator("#addToCart").count() == 0 and page.locator(".add-to-cart").count() == 0:
                    body_text = page.inner_text("body").lower()
                    if "tükendi" in body_text or "temin edilemiyor" in body_text:
                        print("❌ Ürün STOKTA YOK.")
                        browser.close()
                        return None
            except: pass

            found_name = "İsim Bulunamadı"
            try:
                h1 = page.locator("h1").first
                if h1.count() > 0: found_name = h1.inner_text().strip()
                else: found_name = page.title().split("|")[0].strip()
            except: pass

            print(f"📦 Ürün: {found_name}")
            
            final_price = 0.0
            method = "Yok"

            # --- 2. MODA/KAMPANYA KONTROLÜ ("Sepete Özel" Avcısı) ---
            print("👁️ Fiyat etiketleri taranıyor...")
            
            try:
                # Ekranda "Sepete özel fiyat" veya "Sepette" yazısı var mı?
                basket_label = page.locator("text=/Sepete özel fiyat|Sepette/i").first
                if basket_label.count() > 0 and basket_label.is_visible():
                    print("🛍️ 'Sepete Özel Fiyat' kampanya etiketi tespit edildi!")
                    # Bu yazının ebeveynine (kutusuna) bakıp içindeki fiyatı alalım
                    # Genelde yazı ve fiyat aynı div içindedir veya kardeş elementtir.
                    
                    # Yöntem: Yazının bulunduğu ana konteynerdeki tüm metni alıp fiyatı sök
                    container = basket_label.locator("..").locator("..") # 2 seviye yukarı çık
                    text = container.inner_text()
                    
                    # Metnin içinden fiyatları bul (Birden fazla olabilir: 3000 TL yerine 1600 TL)
                    prices = extract_all_prices(text)
                    if prices:
                        # Sepete özel fiyat genelde en düşük olandır
                        final_price = min(prices)
                        method = "Kampanya (Sepete Özel)"
                        print(f"✅ Kampanya Fiyatı Bulundu: {final_price} TL")
            except Exception as e:
                print(f"⚠️ Kampanya tarama hatası: {e}")

            # --- 3. STANDART ANA FİYAT (Elektronik vb.) ---
            if final_price == 0:
                try:
                    # Öncelikli Seçiciler
                    selectors = [
                        '[data-test-id="price-current-price"]', # Standart
                        'span[data-bind*="currentPrice"]',       # Moda Alternatif
                        '.price-value',                          # Genel
                        '.product-price',                        # Genel
                        '#offering-price span:first-child'       # Yeni Tasarım
                    ]

                    for selector in selectors:
                        elements = page.locator(selector).all()
                        for el in elements:
                            if el.is_visible():
                                p = extract_price(el.inner_text())
                                if p and p > 10:
                                    final_price = p
                                    method = f"Standart Etiket ({selector})"
                                    print(f"✅ Standart Fiyat Bulundu: {final_price} TL")
                                    break
                        if final_price > 0: break
                except: pass

            # --- 4. YEDEK: LİSTE TARAMA (Satıcı Seçimi İçin) ---
            # Eğer yukarıdakiler bulamadıysa veya özel satıcı istiyorsak
            if final_price == 0 or (target_seller and final_price > 0):
                # Mevcut satıcıyı kontrol et (Eğer özel satıcı istiyorsak)
                current_seller_ok = True
                if target_seller:
                    try:
                        seller_text = page.locator(".merchant-name, .seller-container").first.inner_text().lower()
                        if target_seller not in seller_text:
                            current_seller_ok = False
                            print(f"⚠️ Ana satıcı farklı, liste taranacak...")
                    except: pass

                if final_price == 0 or not current_seller_ok:
                    print("🔄 Liste/Genel tarama yapılıyor...")
                    
                    # Listeyi aç
                    try:
                        buttons = page.locator("text=/Tüm satıcıları gör|satıcı daha|Diğer satıcılar/i").all()
                        for btn in buttons:
                            if btn.is_visible():
                                btn.click()
                                page.wait_for_timeout(2000)
                                break
                    except: pass

                    # Genel Tarama
                    raw_prices = []
                    blacklist = ["kazanç", "kazanc", "indirim", "taksit", "kargo", "getir", "yenile", "ayda"]
                    
                    try:
                        # Tüm fiyat benzeri kutular
                        elements = page.locator("[class*='price']").all()
                        for el in elements:
                            if not el.is_visible(): continue
                            text = el.inner_text()
                            
                            # Yasaklı kelime kontrolü
                            # Elementin kendisinde veya bir üst ebeveyninde yasaklı kelime var mı?
                            full_text = text + " " + el.locator("..").inner_text()
                            if any(bad in full_text.lower() for bad in blacklist):
                                continue

                            p = extract_price(text)
                            if p and p > 10: raw_prices.append(p)
                    except: pass

                    if raw_prices:
                        unique_prices = sorted(list(set(raw_prices)))
                        print(f"📄 Adaylar: {unique_prices}")
                        
                        # En mantıklısını seç
                        if unique_prices:
                            # Eğer daha önce bir fiyat bulduysak ve bu listede daha ucuzu yoksa, eskisini koru
                            min_p = min(unique_prices)
                            if final_price == 0 or min_p < final_price:
                                final_price = min_p
                                method = "Genel Tarama"

            browser.close()

            if final_price > 0:
                print(f"✅ SONUÇ: {final_price} TL [{method}]")
            else:
                print("❌ Fiyat bulunamadı.")

            return {
                "name": found_name,
                "price": final_price,
                "url": url
            }

    except Exception as e:
        print(f"HATA (Hepsiburada): {e}")
        return None

def extract_price(text):
    """Metinden İLK fiyatı çıkar"""
    if not text: return None
    text = text.replace('TL', '').replace('₺', '').strip()
    matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?)', text)
    if not matches: return None
    try:
        clean = matches[0].replace('.', '').replace(',', '.')
        return float(clean)
    except: pass
    return None

def extract_all_prices(text):
    """Metinden TÜM fiyatları çıkarır (Kampanya vs kıyaslaması için)"""
    if not text: return []
    text = text.replace('TL', '').replace('₺', '').strip()
    matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?)', text)
    results = []
    for m in matches:
        try:
            clean = m.replace('.', '').replace(',', '.')
            val = float(clean)
            if val > 10: results.append(val)
        except: pass
    return results