import json
import os

# Verilerin tutulacağı dosya
DATA_FILE = "data.json"

def load_data():
    """Kayıtlı verileri dosyadan okur."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    """Verileri dosyaya kaydeder."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Kayıt hatası: {e}")

def get_product(url):
    """URL'ye göre kayıtlı ürün bilgisini getirir."""
    data = load_data()
    return data.get(url)

def update_product(url, product_info):
    """Ürün bilgisini günceller veya yeni ekler."""
    data = load_data()
    data[url] = product_info
    save_data(data)