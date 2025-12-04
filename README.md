# 🚀 Akıllı Fiyat Takip Botu (Trendyol & Hepsiburada) - v1.0

Bu yazılım, belirlediğiniz ürünleri 7/24 izleyen, fiyat düştüğü anda telefonunuza **Telegram** üzerinden bildirim gönderen profesyonel bir otomasyon aracıdır.

Sadece fiyatı çekmez; arkasındaki **Gelişmiş Algoritma** sayesinde taksitli fiyatları, "Eskisini Getir" kampanyalarını ve yanıltıcı kupon indirimlerini ayırt eder. Size sadece **gerçek satıcı fiyatını** bildirir.

---

## 🔥 Temel Özellikler

* **Çift Platform Desteği:** Trendyol ve Hepsiburada ile tam uyumlu çalışır.
* **Akıllı Fiyat Süzgeci:** Ürün sayfasındaki "Taksit Tutarını" veya "Kazanç Miktarını" fiyat sanıp hata yapmaz.
* **Satıcı Odaklı Takip (Hepsiburada):** Hepsiburada'da sadece en ucuzunu değil, **istediğiniz satıcıyı** takip edebilirsiniz.
* **Kesintisiz Çalışma:** Docker altyapısı sayesinde bilgisayarınızda kurulum derdi olmadan, tek tıkla çalışır.
* **Canlı Güncelleme:** Bot çalışırken yeni ürün linki eklerseniz, botu durdurup başlatmaya gerek kalmadan algılar.

---

## 🛠️ Kurulum Rehberi (Adım Adım)

Bu botu çalıştırmak için yazılımcı olmanıza gerek yok. Aşağıdaki adımları sırasıyla uygulayın.

### 1. Hazırlık (Gereksinimler)
Bilgisayarınızda **Docker Desktop** uygulamasının yüklü ve çalışıyor olması gerekir.
* *Yüklü değilse: [Docker Resmi Sitesinden](https://www.docker.com/products/docker-desktop/) indirip kurabilirsiniz (Ücretsizdir).*

---

### 2. Telegram Ayarlarını Yapma (Token ve ID Alma)

Botun size mesaj atabilmesi için gerekli bilgileri şu şekilde alabilirsiniz:

#### A. Bot Token Alma (BotFather)
1.  Telegram uygulamasını açın ve arama çubuğuna **`BotFather`** yazın (Mavi tikli olan).
2.  Sohbeti başlatın ve **`/newbot`** komutunu gönderin.
3.  Sizden botunuz için bir **isim** isteyecek (Örn: Fiyat Takipçim). Yazıp gönderin.
4.  Sizden bir **kullanıcı adı** isteyecek. Sonu mutlaka `bot` ile bitmeli (Örn: `AlpayFiyatBot`).
5.  İşlem bitince size **`HTTP API:`** ile başlayan uzun bir şifre verecek. **Bu şifreyi kopyalayın.**

#### B. Kendi ID'nizi Alma (Chat ID)
Botun mesajı kime atacağını bilmesi için ID'nize ihtiyacı var.
1.  Telegram arama çubuğuna **`userinfobot`** yazın.
2.  Çıkan profile tıklayıp **Start** (Başlat) deyin.
3.  Size `Id: 123456789` şeklinde bir numara gönderecek. **O numarayı kopyalayın.**

---

### 3. Dosyaları Düzenleme

İndirdiğiniz klasörün içindeki dosyaları şu şekilde düzenleyin:

#### A. Şifreleri Girme (`.env`)
1.  Klasördeki `env.example` dosyasının adını **`.env`** olarak değiştirin (Sonundaki `.example` yazısını silin).
2.  Bu dosyayı Not Defteri ile açın ve az önce aldığınız bilgileri yapıştırın:
    ```ini
    TELEGRAM_TOKEN=123456:ABC-DEF... (BotFather'dan aldığınız şifre)
    TELEGRAM_CHAT_ID=123456789 (userinfobot'tan aldığınız numara)
    ```
3.  Dosyayı kaydedip kapatın.

#### B. Ürün Listesi (`urls.txt`)
1.  `urls.txt` dosyasını açın.
2.  Takip etmek istediğiniz ürünlerin linklerini **alt alta** yapıştırın.
3.  Kaydedip kapatın.

---

### 4. Botu Başlatma
1.  Bot klasörünün içinde boş bir yere **Sağ Tık** yapın ve **"Terminalde Aç"** (veya PowerShell / CMD) seçeneğine tıklayın.
2.  Açılan siyah ekrana şu komutu yazıp **Enter** tuşuna basın:

    `docker-compose up -d`

🎉 **Tebrikler!** Botunuz arka planda çalışmaya başladı. İlk açılışta listenizdeki ürünlerin güncel fiyatlarını size mesaj olarak atacaktır.

---

## 💡 İpuçları ve Püf Noktaları

### 🛒 Hepsiburada'da "Belirli Bir Satıcıyı" Takip Etmek
Hepsiburada'da bir ürünün birden fazla satıcısı olabilir. Bot varsayılan olarak "En Ucuz" satıcıyı takip eder. Eğer siz **özel bir satıcıyı** (örneğin Apple Türkiye'yi) takip etmek istiyorsanız:

1.  Hepsiburada'da ürün sayfasına gidin.
2.  Sağ taraftaki "Diğer Satıcılar" listesinden istediğiniz satıcının yanındaki "Ürüne Git" butonuna basın.
3.  Tarayıcının adres çubuğundaki linki kopyalayın. (Linkin sonunda `?magaza=SaticiAdi` yazar).
4.  Bu linki `urls.txt` dosyasına yapıştırın.
    * *Bot artık sadece o satıcının fiyatını takip edecektir.*

### 🔄 Yeni Ürün Eklemek
Bot çalışırken yeni bir ürün eklemek isterseniz, botu durdurmanıza gerek yoktur.
1.  `urls.txt` dosyasını açın ve yeni linki ekleyin.
2.  Kaydedin.
3.  Bot, bir sonraki kontrol döngüsünde (varsayılan 10 dakika) yeni linki otomatik olarak algılayacaktır.

---

## ❓ Sıkça Sorulan Sorular (SSS)

**S: Bilgisayarımı kapatırsam bot çalışmaya devam eder mi?**
C: Hayır. Botun çalışması için bilgisayarınızın açık ve internete bağlı olması gerekir. Eğer 7/24 kesintisiz takip istiyorsanız, bu klasörü bir Sanal Sunucuya (VPS) yükleyebilirsiniz.

**S: Botu nasıl durdururum?**
C: Terminali tekrar açın ve şu komutu yazın: `docker-compose down`

**S: Bot hata verirse ne yapmalıyım?**
C: `.env` dosyasındaki Telegram Token ve Chat ID'nizin doğru olduğundan (boşluk bırakmadığınızdan) emin olun. Docker uygulamasının açık olduğundan emin olun.

---
*Bol kazançlı ve keyifli alışverişler dileriz!*