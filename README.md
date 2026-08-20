# CV Oluşturucu — 10 Şablonlu PDF CV Uygulaması

Bilgilerinizi doldurup 10 farklı hazır tasarımdan birini seçerek saniyeler
içinde profesyonel bir PDF CV oluşturmanızı sağlayan Python masaüstü
uygulaması.

## Özellikler

- **10 farklı şablon**: Klasik, Modern Mavi, Minimalist Gri, İki Sütun Koyu
  Kenar, Zaman Çizelgesi, Yaratıcı Renkli, Kurumsal Yeşil, Zarif Bordo,
  Teknoloji Koyu Tema, Sade Turuncu.
- Kişisel bilgiler, profil özeti, sınırsız sayıda iş deneyimi / eğitim
  kaydı, yetenekler, diller, sertifikalar.
- Türkçe karakterler (ğ, ş, ı, İ, ö, ü, ç) tam destekli — uygulamayla
  birlikte gelen font sayesinde herhangi bir ek kurulum gerekmez.
- Uzun içerikler otomatik olarak ikinci sayfaya taşar.
- Taslağınızı JSON olarak kaydedip daha sonra kaldığınız yerden devam
  edebilirsiniz (Dosya → Taslağı Kaydet / Taslak Yükle).

## Kurulum

1. Python 3.9 veya üzeri gereklidir. [python.org](https://www.python.org/downloads/)
   üzerinden indirebilirsiniz. **Windows'ta kurulum sırasında "Add Python to
   PATH" kutusunu işaretlemeyi unutmayın.**
2. Tkinter genelde Python ile birlikte gelir. Eğer içeren dağıtımınızda
   yoksa (bazı Linux dağıtımlarında ayrı paket olabilir):
   ```bash
   # Ubuntu / Debian
   sudo apt-get install python3-tk
   ```
3. Proje klasörüne terminalde girin ve gerekli kütüphaneyi kurun:
   ```bash
   pip install -r requirements.txt
   ```

## Çalıştırma

```bash
python app.py
```
(Bazı sistemlerde `python3 app.py` gerekebilir.)

## Kullanım

1. Açılan pencerede **Kişisel Bilgiler**, **Profil Özeti**, **İş Deneyimi**,
   **Eğitim**, **Yetenekler**, **Diller** ve **Sertifikalar** alanlarını
   doldurun.
   - "+ Deneyim Ekle" / "+ Eğitim Ekle" ile istediğiniz kadar kayıt
     ekleyebilir, her kaydın altındaki "Bu Kaydı Sil" ile kaldırabilirsiniz.
   - Yetenek/Dil/Sertifika alanlarına yazıp Enter'a basarak veya "Ekle"
     butonuyla listeye ekleyin; listeden seçip "Seçileni Sil" ile
     kaldırabilirsiniz.
2. Sayfanın altındaki **Şablon Seçimi** bölümünden 10 tasarımdan birini
   seçin.
3. **"PDF CV Oluştur"** butonuna basın, kaydetmek istediğiniz konumu seçin.
4. İsterseniz oluşturulan PDF'i hemen açabilirsiniz.

### Taslağı kaydetme

Uzun bir CV'yi tek seferde bitiremeyebilirsiniz. **Dosya → Taslağı Kaydet
(JSON)** ile tüm girdilerinizi bir dosyaya kaydedip, **Dosya → Taslak
Yükle** ile daha sonra kaldığınız yerden devam edebilirsiniz.

## Proje Dosyaları

```
cv_app/
├── app.py              # Tkinter arayüzü (uygulamayı bu dosyayla başlatın)
├── templates.py         # 10 şablonun PDF çizim kodları
├── pdf_utils.py          # Metin sarma / sayfa taşması yardımcı fonksiyonları
├── fonts/                # Türkçe karakter destekli gömülü fontlar (DejaVu)
├── logos/                # Uygulama ikonu kaynakları (logo.png, app.ico, app.icns)
├── build_icon.py         # logo.png → çoklu boyutlu app.ico / app.icns üretir
├── CV-Olusturucu.spec    # Windows exe derleme yapılandırması
├── CV-Olusturucu-mac.spec# macOS .app derleme yapılandırması
├── build_mac.sh          # macOS'ta .app + .dmg üretir
├── .github/workflows/    # GitHub Actions: Windows + macOS otomatik derleme
├── requirements.txt
└── README.md
```

## Yeni şablon eklemek isterseniz

`templates.py` içinde `draw_xxx(c, data)` imzasında yeni bir fonksiyon
yazıp, dosyanın sonundaki `TEMPLATES` listesine bir giriş eklemeniz
yeterlidir — uygulama arayüzündeki şablon listesi otomatik güncellenir.
