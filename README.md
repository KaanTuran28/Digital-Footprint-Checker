# 🕵️‍♂️ Dijital Ayak İzi ve Risk Analiz Aracı (OSINT Tool)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)
![Playwright](https://img.shields.io/badge/Automation-Playwright-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> **Sivas Cumhuriyet Üniversitesi - Yönetim Bilişim Sistemleri Bölümü Bitirme Projesi** > **Geliştirici:** Kaan Turan

Bu proje, bireylerin dijital dünyada bıraktıkları izleri (Digital Footprint) analiz ederek siber güvenlik farkındalığı oluşturmayı amaçlayan bir **Açık Kaynak İstihbaratı (OSINT)** yazılımıdır. Instagram, X (Twitter) ve LinkedIn platformlarını tarayarak paylaşılan verilerdeki güvenlik risklerini (E-posta, Telefon, Konum, Eğitim Bilgisi vb.) tespit eder ve risk skoru üretir.

---

## 🚀 Özellikler

* **Çoklu Platform Desteği:** Instagram, X (Twitter) ve LinkedIn profillerini analiz eder.
* **Akıllı Bot Mimarisi:** Playwright tabanlı, "Persistent Context" (Kalıcı Oturum) kullanan ve insan davranışlarını taklit eden botlar.
* **Derin Tarama (Deep Scan):** Sadece profil bilgilerini değil, gönderi açıklamalarını (captions), resim alt metinlerini (ALT text) ve tweetleri okur.
* **Regex Tabanlı Risk Motoru:**
    * 💳 **Finansal:** Kredi kartı, IBAN, Kripto cüzdanları.
    * 🆔 **Kimlik:** T.C. Kimlik, Pasaport, SSN.
    * 📍 **Konum:** Ülke, şehir ve açık adres tespiti.
    * 🎓 **Kişisel:** Eğitim durumu, e-posta, telefon numaraları.
* **Dinamik Risk Skorlama:** Her veriye ağırlık vererek 0-100 arası "Kritik", "Yüksek", "Orta", "Düşük" risk seviyesi belirler.
* **Görsel Pano (Dashboard):** Geçmiş analizlerin saklandığı ve görselleştirildiği kullanıcı arayüzü.

---

## 🛠️ Kurulum

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### 1. Projeyi Klonlayın

* git clone https://github.com/KaanTuran28/Digital-Footprint-Checker.git
* cd digital-footprint-checker

## Sanal Ortamı (Virtualenv) Oluşturun

python -m venv .venv
# Windows için:
.venv\Scripts\activate
# Mac/Linux için:
source .venv/bin/activate

## Gerekli Kütüphaneleri Yükleyin

* pip install -r requirements.txt

## Playwright Tarayıcılarını Kurun

* playwright install
* playwright install-deps

## .env Dosyasını Oluşturun

* SECRET_KEY=gizli_anahtariniz_buraya
* DATABASE_URL=sqlite:///site.db

# Bot Hesap Bilgileri (Fake hesap kullanmanız önerilir)
* IG_USERNAME=fake_insta_kullanici
* IG_PASSWORD=sifre123
* TW_USERNAME=fake_twitter_kullanici
* TW_PASSWORD=sifre123
* LINKEDIN_EMAIL=fake_linkedin@email.com
* LINKEDIN_PASSWORD=sifre123

## Veritabanını Başlatın

* python init_db.py

## Uygulamayı Çalıştırın

* python run.py
* Tarayıcınızda http://127.0.0.1:5000 adresine gidin.
