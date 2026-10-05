# 🕵️ Digital Footprint & Risk Analysis Tool (OSINT)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)
![Playwright](https://img.shields.io/badge/Automation-Playwright-orange)
![License](https://img.shields.io/badge/license-MIT-green)

<p align="center"><b><a href="#english">English</a></b> · <b><a href="#türkçe">Türkçe</a></b></p>

> **Graduation project.**

---

## English

An Open-Source Intelligence (OSINT) tool that raises cyber-security awareness by analysing the traces people leave online (their *digital footprint*). It scans Instagram, X (Twitter) and LinkedIn profiles, detects security risks in what has been shared publicly (email, phone, location, education, etc.) and produces a risk score.

> **For authorised awareness and research use.** Analyse your own accounts or accounts you have permission to assess. Respect each platform's terms of service and applicable privacy law.

### Features

- **Multi-platform:** analyses Instagram, X (Twitter) and LinkedIn profiles.
- **Smart bot architecture:** Playwright-based bots using a persistent context that mimic human behaviour.
- **Deep scan:** reads not only profile fields but also post captions, image ALT text and tweets.
- **Regex-based risk engine:**
  - 💳 Financial: credit cards, IBAN, crypto wallets
  - 🆔 Identity: national ID, passport, SSN
  - 📍 Location: country, city and open address
  - 🎓 Personal: education, email, phone numbers
- **Dynamic risk scoring:** each finding is weighted to produce a 0–100 score across "Critical", "High", "Medium" and "Low" levels.
- **Dashboard:** a UI that stores and visualises past analyses.

### Tech stack

- **Backend:** Python, Flask
- **Scraping/automation:** Playwright (persistent context)
- **Database:** SQLAlchemy (SQLite)
- **Analysis:** regex-based weighted risk engine

### Setup

```bash
git clone https://github.com/KaanTuran28/Digital-Footprint-Checker.git
cd Digital-Footprint-Checker

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
playwright install
playwright install-deps
```

Create a `.env` file (do **not** commit it):

```env
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///site.db

# Bot account credentials (a dedicated/throwaway account is recommended)
IG_USERNAME=...
IG_PASSWORD=...
TW_USERNAME=...
TW_PASSWORD=...
LINKEDIN_EMAIL=...
LINKEDIN_PASSWORD=...
```

Then initialise the database and run:

```bash
python setup_db.py
python run.py
# open http://127.0.0.1:5000
```

### License

MIT — see [LICENSE](./LICENSE).

---

## Türkçe

Bireylerin dijital dünyada bıraktıkları izleri (*digital footprint*) analiz ederek siber güvenlik farkındalığı oluşturmayı amaçlayan bir **Açık Kaynak İstihbaratı (OSINT)** yazılımı. Instagram, X (Twitter) ve LinkedIn profillerini tarayarak herkese açık paylaşımlardaki güvenlik risklerini (e-posta, telefon, konum, eğitim bilgisi vb.) tespit eder ve risk skoru üretir.

> **Yetkili farkındalık ve araştırma amaçlıdır.** Kendi hesaplarınızı ya da değerlendirme izniniz olan hesapları analiz edin. Platformların kullanım şartlarına ve ilgili gizlilik mevzuatına uyun.

### Özellikler

- **Çoklu platform:** Instagram, X (Twitter) ve LinkedIn profillerini analiz eder.
- **Akıllı bot mimarisi:** Playwright tabanlı, "Persistent Context" (kalıcı oturum) kullanan ve insan davranışlarını taklit eden botlar.
- **Derin tarama:** sadece profil bilgilerini değil, gönderi açıklamalarını (caption), resim ALT metinlerini ve tweetleri de okur.
- **Regex tabanlı risk motoru:**
  - 💳 Finansal: kredi kartı, IBAN, kripto cüzdanları
  - 🆔 Kimlik: T.C. Kimlik, pasaport, SSN
  - 📍 Konum: ülke, şehir ve açık adres
  - 🎓 Kişisel: eğitim durumu, e-posta, telefon
- **Dinamik risk skorlama:** her veriye ağırlık vererek 0–100 arası "Kritik", "Yüksek", "Orta", "Düşük" seviyesi belirler.
- **Görsel pano (dashboard):** geçmiş analizlerin saklandığı ve görselleştirildiği arayüz.

### Teknolojiler

- **Backend:** Python, Flask
- **Tarama/otomasyon:** Playwright (persistent context)
- **Veritabanı:** SQLAlchemy (SQLite)
- **Analiz:** regex tabanlı ağırlıklı risk motoru

### Kurulum

```bash
git clone https://github.com/KaanTuran28/Digital-Footprint-Checker.git
cd Digital-Footprint-Checker

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
playwright install
playwright install-deps
```

Bir `.env` dosyası oluşturun (commit **etmeyin**):

```env
SECRET_KEY=gizli_anahtariniz
DATABASE_URL=sqlite:///site.db

# Bot hesap bilgileri (özel/tek kullanımlık hesap önerilir)
IG_USERNAME=...
IG_PASSWORD=...
TW_USERNAME=...
TW_PASSWORD=...
LINKEDIN_EMAIL=...
LINKEDIN_PASSWORD=...
```

Ardından veritabanını başlatıp çalıştırın:

```bash
python setup_db.py
python run.py
# http://127.0.0.1:5000 adresine gidin
```

### Lisans

MIT — bkz. [LICENSE](./LICENSE).
