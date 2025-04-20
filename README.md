# 📊 Anket Yönetim Platformu

Modern ve kullanıcı dostu bir anket oluşturma, yönetme ve analiz platformu. Tamamen Django tabanlı bu uygulama, kullanıcıların kolayca anketler oluşturmasına, paylaşmasına ve sonuçları analiz etmesine olanak tanır.

![Anket Yönetim Platformu](https://cdn-icons-png.flaticon.com/512/5610/5610944.png)

## 🌟 Özellikler

- 👤 **Kullanıcı Yönetimi**: Kayıt ol, giriş yap, şifre sıfırlama
- 📝 **Çeşitli Soru Tipleri**:
  - Kısa metin cevapları
  - Uzun metin yanıtları
  - Çoktan seçmeli (tek seçim)
  - Çoktan seçmeli (çoklu seçim)
  - Derecelendirme soruları (1-5 arası yıldız)
- 🚀 **Gelişmiş Anket Özellikleri**:
  - Anketleri aktif/pasif yapma
  - Anketleri URL ile paylaşma
  - Zorunlu sorular belirleme
  - Soruları sıralama
- 📈 **Veri Analizi**:
  - Yanıt istatistikleri
  - Grafiksel sonuç gösterimi

## 🔧 Teknolojiler

- **Backend**: Django 5.1.1
- **Frontend**: HTML5, CSS3, JavaScript
- **Veritabanı**: SQLite (Geliştirme), PostgreSQL (Üretim)
- **Dağıtım**: Gunicorn, Whitenoise

## 🚀 Kurulum

### Ön Koşullar

- Python 3.10+
- pip

### Adımlar

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/username/survey-management.git
   cd survey-management
   ```

2. Sanal ortam oluşturun ve aktif edin:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. Veritabanı göçlerini uygulayın:
   ```bash
   python manage.py migrate
   ```

5. Statik dosyaları toplayın:
   ```bash
   python manage.py collectstatic
   ```

6. Geliştirme sunucusunu başlatın:
   ```bash
   python manage.py runserver
   ```

7. Tarayıcınızda `http://127.0.0.1:8000` adresine gidin.


## 📝 Kullanım

1. Kaydolun veya giriş yapın
2. "Anket Oluştur" butonuna tıklayın
3. Anket başlığı ve açıklaması ekleyin
4. Sorular ve seçenekler ekleyin
5. Anketi aktif hale getirin
6. Oluşturulan bağlantıyı paylaşın ve cevapları alın
7. Sonuçları analiz edin


## 🤝 Katkıda Bulunma

1. Bu depoyu fork edin
2. Özellik dalınızı oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Dalınıza push edin (`git push origin feature/amazing-feature`)
5. Bir Pull Request oluşturun

## ⭐ Projeyi Destekleyin

Eğer bu projeyi faydalı bulduysanız, yıldız vererek destekleyebilirsiniz! 