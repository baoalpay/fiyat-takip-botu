from playwright.sync_api import sync_playwright
import re
import time

def check_trendyol(url):
    """
    GELİŞTİRİLMİŞ TRENDYOL FİYAT BULMA:
    - Trendyol'a özel CSS sınıflarını hedefler
    - İndirimli fiyata öncelik verir
    - Sepet indirimlerini algılar
    - Gelişmiş taksit filtreleme
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False, 
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()

            print("⏳ Siteye gidiliyor...")
            try:
                page.goto(url, timeout=90000)
                print("💤 Sayfa yükleniyor...")
                page.wait_for_load_state("networkidle", timeout=15000)
                page.wait_for_timeout(3000)  # Dinamik içerik için extra süre
            except:
                print("⚠️ Zaman aşımı, devam ediliyor...")

            # --- 1. STOK KONTROLÜ ---
            try:
                body_text = page.inner_text("body").lower()
                if "tükendi" in body_text or "temin edilemiyor" in body_text:
                    print("❌ Ürün STOKTA YOK.")
                    browser.close()
                    return None
            except:
                pass

            # --- 2. İSİM BULMA ---
            found_name = "İsim Bulunamadı"
            try:
                # Trendyol'da genelde h1 veya product-name class'ı
                h1 = page.locator("h1, [class*='product-name']").first
                if h1.count() > 0:
                    found_name = h1.inner_text().strip()
                else:
                    found_name = page.title().split("|")[0].strip()
            except:
                pass

            print(f"📦 Ürün: {found_name}")
            print("🔍 Fiyat analizi yapılıyor...")
            
            # --- 3. TRENDYOL'A ÖZEL FİYAT BULMA ---
            price_data = {
                "discounted": None,  # İndirimli fiyat (kırmızı)
                "original": None,    # Orijinal fiyat (üstü çizili)
                "basket": None       # Sepet indirimi
            }
            
            # A) İndirimli Fiyat (prc-dsc, price-discount gibi class'lar)
            try:
                discount_selectors = [
                    "[class*='prc-dsc']",
                    "[class*='discounted']",
                    "[class*='sale-price']",
                    ".product-price .prc-slg",  # Trendyol'un ana fiyat class'ı
                    "[data-test-id='price-current']",  # Yeni Trendyol yapısı
                    ".pr-in-w .prc-slg",  # Fiyat wrapper içindeki fiyat
                    "[class*='product-price'] span:not([class*='prc-org'])"  # Üstü çizili olmayan fiyatlar
                ]
                
                for selector in discount_selectors:
                    elements = page.locator(selector).all()
                    for el in elements:
                        if el.is_visible():
                            text = el.inner_text()
                            price = extract_price(text)
                            if price:
                                price_data["discounted"] = price
                                print(f"💚 İndirimli Fiyat Bulundu: {price} TL")
                                break
                    if price_data["discounted"]:
                        break
            except Exception as e:
                print(f"⚠️ İndirimli fiyat araması hatası: {e}")

            # B) Orijinal Fiyat (üstü çizili - prc-org)
            try:
                original_selectors = [
                    "[class*='prc-org']",
                    "[class*='original']",
                    "del",
                    ".price-strike"
                ]
                
                for selector in original_selectors:
                    elements = page.locator(selector).all()
                    for el in elements:
                        if el.is_visible():
                            text = el.inner_text()
                            price = extract_price(text)
                            if price:
                                price_data["original"] = price
                                print(f"🔵 Orijinal Fiyat: {price} TL")
                                break
                    if price_data["original"]:
                        break
            except:
                pass

            # C) Sepet İndirimi Kontrolü (Sadece bilgi amaçlı)
            try:
                basket_text = page.inner_text("body").lower()
                # "sepette 5.999 tl" gibi ifadeleri ara
                basket_matches = re.findall(r'sepette?\s+(\d+(?:\.\d+)?(?:,\d+)?)\s*tl', basket_text)
                if basket_matches:
                    basket_price = extract_price(basket_matches[0])
                    if basket_price:
                        price_data["basket"] = basket_price
                        print(f"🛒 Sepet İndirimi Mevcut: {basket_price} TL (bilgi amaçlı)")
            except:
                pass

            # --- 4. YEDEK YÖNTEM: GENEL TARAMA ---
            # Eğer yukarıdaki yöntemler işe yaramazsa, eski yönteme dön
            if not price_data["discounted"] and not price_data["original"]:
                print("⚠️ Özel selectors başarısız, genel tarama başlatılıyor...")
                fallback_result = fallback_price_search(page)
                if fallback_result:
                    price_data["discounted"] = fallback_result
                    print(f"🔄 Yedek yöntemle bulundu: {fallback_result} TL")

            # --- 5. EN İYİ FİYATI BELİRLE ---
            final_price = determine_best_price(price_data)
            
            if final_price:
                print(f"✅ SONUÇ: {final_price} TL")
            else:
                print("❌ Fiyat belirlenemedi!")

            browser.close()

            return {
                "name": found_name,
                "price": final_price,
                "url": url,
                "price_details": price_data
            }

    except Exception as e:
        print(f"HATA: {e}")
        return None


def extract_price(text):
    """Metinden fiyat çıkar ve float'a çevir"""
    if not text:
        return None
    
    # 1.250,90 veya 1250,90 formatını yakala
    matches = re.findall(r'(\d+(?:\.\d+)?(?:,\d+)?)', text)
    if not matches:
        return None
    
    try:
        # TR formatını (1.000,50) Python float'a (1000.50) çevir
        clean_val = float(matches[0].replace('.', '').replace(',', '.'))
        
        # Mantıklı fiyat aralığı kontrolü
        if 1 < clean_val < 1000000:
            return clean_val
    except:
        pass
    
    return None


def fallback_price_search(page):
    """Eski genel tarama yöntemi (yedek)"""
    candidates = []
    
    # TL içeren metinleri topla
    try:
        elements = page.get_by_text("TL", exact=False).all()
        for el in elements:
            if el.is_visible():
                text = el.inner_text().strip()
                if text:  # Boş string kontrolü
                    candidates.append(text)
    except:
        pass

    # Class'ında price geçenleri topla
    try:
        price_boxes = page.locator("[class*='price'], [class*='prc'], [class*='pr-']").all()
        for box in price_boxes:
            if box.is_visible():
                text = box.inner_text().strip()
                if text:
                    candidates.append(text)
    except:
        pass
    
    # Span ve div elementlerinde direkt fiyat araması
    try:
        all_spans = page.locator("span, div").all()
        for span in all_spans:
            if span.is_visible():
                text = span.inner_text().strip()
                # Sadece fiyat formatına uyan kısa metinleri al (örn: "24.999 TL")
                if text and "TL" in text and len(text) < 30:
                    candidates.append(text)
    except:
        pass

    # Ayıklama
    raw_prices = []
    blacklist = ["kupon", "fırsat", "kazan", "kargo", "taksit", "ay", "aylık", "/ay", "ödeme"]

    for text in candidates:
        text_lower = text.lower()
        if any(bad in text_lower for bad in blacklist):
            continue
        
        price = extract_price(text)
        if price and 10 < price < 500000:
            raw_prices.append(price)

    if not raw_prices:
        return None

    # Taksit filtresi (Geliştirilmiş)
    unique_prices = sorted(list(set(raw_prices)))
    
    # Eğer sadece 1-2 fiyat varsa direkt en düşüğü dön
    if len(unique_prices) <= 2:
        return min(unique_prices)
    
    clean_list = []
    
    for p in unique_prices:
        is_installment = False
        for parent in unique_prices:
            if p == parent:
                continue
            # 2,3,6,9,12 taksit kontrolü
            ratio = parent / p
            for installment in [2, 3, 6, 9, 12]:
                if installment - 0.15 < ratio < installment + 0.15:
                    is_installment = True
                    break
            if is_installment:
                break
        
        if not is_installment:
            clean_list.append(p)
    
    return min(clean_list) if clean_list else min(unique_prices)


def determine_best_price(price_data):
    """Fiyat önceliğine göre en doğru fiyatı seç"""
    
    # 1. Öncelik: İndirimli Fiyat (Sayfada görünen gerçek fiyat)
    if price_data["discounted"]:
        return price_data["discounted"]
    
    # 2. Öncelik: Orijinal Fiyat (İndirim yoksa)
    if price_data["original"]:
        return price_data["original"]
    
    # NOT: Sepet indirimi sadece bilgi amaçlı, gerçek fiyat değil
    
    return None