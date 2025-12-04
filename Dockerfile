# 1. Microsoft'un hazır Playwright imajını kullanıyoruz (İçinde Python ve Tarayıcılar hazır!)
# Bu sayede müşteri "Playwright install hatası" almaz.
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

# 2. Çalışma klasörünü ayarla
WORKDIR /app

# 3. Gerekli dosyaları kopyala
COPY requirements.txt .

# 4. Kütüphaneleri yükle
RUN pip install --no-cache-dir -r requirements.txt

# 5. Proje kodlarını kopyala
COPY . .

# 6. Zaman dilimini Türkiye yap (Loglar doğru saatte görünsün)
ENV TZ="Europe/Istanbul"

# 7. Botu başlat (Unbuffered: Logları anlık görmek için)
CMD ["python", "-u", "main.py"]