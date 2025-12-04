def get_headers():
    """
    Siteye gerçek bir tarayıcı (Chrome) gibi görünmek için gerekli başlıklar.
    """
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    }

def clean_price(price_text):
    """
    '1.299,90 TL' gibi metinleri 1299.90 (float) sayısına çevirir.
    """
    if not price_text:
        return 0.0
    
    # TL simgesini ve boşlukları temizle
    clean = price_text.replace("TL", "").replace("tl", "").strip()
    # Binlik ayırıcı noktayı kaldır (1.200 -> 1200)
    clean = clean.replace(".", "")
    # Kuruş ayırıcı virgülü noktaya çevir (1200,50 -> 1200.50)
    clean = clean.replace(",", ".")
    
    try:
        return float(clean)
    except ValueError:
        return 0.0