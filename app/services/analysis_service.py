import re
from typing import Dict, List, Any, Optional

class RiskAnalyzer:
    """
    ENTERPRISE GRADE OSINT ANALYZER
    --------------------------------
    Gelişmiş Regex motoru ile finansal verileri, bulut (cloud) anahtarlarını,
    altyapı bilgilerini (IP/MAC) ve kişisel verileri (PII) analiz eder.
    """

    def __init__(self):
        # Kategori Limitleri (Puanların aşırı şişmesini engeller)
        self.CATEGORY_LIMITS = {
            "KRİTİK_GÜVENLİK": 100, # API Keyler, Private Keyler
            "FİNANSAL": 100,        # Kredi Kartı, Kripto
            "KİMLİK": 100,          # TC, SSN, Pasaport
            "ALTYAPI": 80,          # IP, Domain, Server
            "İLETİŞİM": 70,         # Email, Telefon
            "KONUM": 60,            # Adres, GPS
            "KURUMSAL": 50,         # İş Ünvanları
            "GİZLİLİK": 50          # "Confidential" ibareleri
        }

        self.PATTERNS = self._get_patterns()
        self._compile_patterns()

    def _get_patterns(self) -> Dict[str, Dict[str, Any]]:
        return {
            # ================================================================
            # 1. KRİTİK GÜVENLİK VE BULUT (CLOUD SECRETS) - WEIGHT: 100
            # ================================================================
            "AWS_ACCESS_KEY": {
                # AWS Access Key ID (AKIA...)
                "regex": r'\b(AKIA|ASIA)[0-9A-Z]{16}\b',
                "weight": 100,
                "category": "KRİTİK_GÜVENLİK",
                "label": "AWS Erişim Anahtarı"
            },
            "GOOGLE_API_KEY": {
                # Google Cloud API Key
                "regex": r'\bAIza[0-9A-Za-z\\-_]{35}\b',
                "weight": 100,
                "category": "KRİTİK_GÜVENLİK",
                "label": "Google API Anahtarı"
            },
            "PRIVATE_KEY_BLOCK": {
                # SSH / RSA Private Key Başlangıç Bloğu
                "regex": r'-----BEGIN (RSA|DSA|EC|OPENSSH|PRIVATE) KEY-----',
                "weight": 100,
                "category": "KRİTİK_GÜVENLİK",
                "label": "Özel Anahtar (Private Key)"
            },
            "DB_CONNECTION_STRING": {
                # Veritabanı bağlantı linkleri (Şifre içerebilir)
                "regex": r'\b(rdbms|postgresql|mysql|mongodb|jdbc):(?:\/\/)?',
                "weight": 95,
                "category": "KRİTİK_GÜVENLİK",
                "label": "Veritabanı Bağlantı Dizisi"
            },
            "SLACK_WEBHOOK": {
                # Slack Webhook URL (İç haberleşme sızıntısı)
                "regex": r'https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+',
                "weight": 95,
                "category": "KRİTİK_GÜVENLİK",
                "label": "Slack Webhook URL"
            },
            "GENERIC_API_TOKEN": {
                # Genel Token formatları (Bearer, Token vb.)
                "regex": r'\b(api_key|access_token|secret_key)\s*[:=]\s*[A-Za-z0-9\-_]{16,}\b',
                "weight": 90,
                "flags": re.IGNORECASE,
                "category": "KRİTİK_GÜVENLİK",
                "label": "Genel API Token"
            },

            # ================================================================
            # 2. FİNANSAL VERİLER (FINANCIAL) - WEIGHT: 90-100
            # ================================================================
            "CREDIT_CARD": {
                # Luhn algoritması ile doğrulanacak
                "regex": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
                "weight": 100,
                "category": "FİNANSAL",
                "label": "Kredi Kartı Numarası",
                "validator": self._validate_luhn
            },
            "CRYPTO_WALLET": {
                # BTC, ETH, Litecoin vb.
                "regex": r'\b(0x[a-fA-F0-9]{40}|bc1[a-zA-HJ-NP-Z0-9]{39,59}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b',
                "weight": 95,
                "category": "FİNANSAL",
                "label": "Kripto Cüzdan Adresi"
            },
            "IBAN_GLOBAL": {
                # TR ve Avrupa IBAN formatları
                "regex": r'\b[A-Z]{2}\d{2}[A-Z0-9]{12,30}\b',
                "weight": 90,
                "category": "FİNANSAL",
                "label": "IBAN Numarası"
            },

            # ================================================================
            # 3. KİŞİSEL VERİLER (PII) - WEIGHT: 80-90
            # ================================================================
            "TC_KIMLIK": {
                # 11 haneli, 0 ile başlamayan
                "regex": r'\b[1-9]\d{10}\b',
                "weight": 90,
                "category": "KİMLİK",
                "label": "T.C. Kimlik No"
            },
            "US_SSN": {
                # ABD Sosyal Güvenlik Numarası (XXX-XX-XXXX)
                "regex": r'\b\d{3}-\d{2}-\d{4}\b',
                "weight": 90,
                "category": "KİMLİK",
                "label": "ABD Sosyal Güvenlik No (SSN)"
            },
            "PASSPORT_NO": {
                # Genel Pasaport Formatı (1 Harf + 6-9 Rakam)
                "regex": r'\b[A-Z][0-9]{6,9}\b',
                "weight": 85,
                "category": "KİMLİK",
                "label": "Pasaport Numarası"
            },

            # ================================================================
            # 4. ALTYAPI VE AĞ (INFRASTRUCTURE) - WEIGHT: 70-80
            # ================================================================
            "IPV4_ADDRESS": {
                # IP Adresi (Örn: 192.168.1.1)
                "regex": r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
                "weight": 75,
                "category": "ALTYAPI",
                "label": "IPv4 Adresi"
            },
            "MAC_ADDRESS": {
                # Donanım Adresi (MM:MM:MM:SS:SS:SS)
                "regex": r'\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b',
                "weight": 70,
                "category": "ALTYAPI",
                "label": "MAC Adresi"
            },
            "INTERNAL_DOMAIN": {
                # Kurumsal iç ağ domainleri
                "regex": r'\b[a-z0-9-]+\.(local|internal|corp|lan)\b',
                "weight": 60,
                "flags": re.IGNORECASE,
                "category": "ALTYAPI",
                "label": "Dahili Ağ Alan Adı"
            },

            # ================================================================
            # 5. İLETİŞİM VE KONUM - WEIGHT: 50-70
            # ================================================================
            "PHONE_GLOBAL": {
                # Uluslararası format (+90..., 00...)
                "regex": r'\b(?:\+|00)[1-9](?:[\s.-]?\d{2,5}){1,4}\b',
                "weight": 70,
                "category": "İLETİŞİM",
                "label": "Uluslararası Telefon"
            },
            "EMAIL": {
                "regex": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "weight": 40,
                "category": "İLETİŞİM",
                "label": "E-posta Adresi"
            },
            "ADDRESS_DETAILED": {
                "regex": r'\b(No:\s*\d+|Daire:\s*\d+|Kat:\s*\d+|Apt\.|Apartmanı|Blok|Site|Mahallesi|Sokak|Cadde)\b',
                "weight": 70,
                "flags": re.IGNORECASE,
                "category": "KONUM",
                "label": "Detaylı Adres"
            },
            "LOCATION_COUNTRY": {
                # Geniş Ülke Listesi
                "regex": r'\b(ABD|USA|United States|Amerika|TR|Türkiye|Turkey|Almanya|Germany|UK|England|France|Italy|Spain|Russia|China)\b',
                "weight": 30,
                "flags": re.IGNORECASE,
                "category": "KONUM",
                "label": "Ülke Bilgisi"
            },
            "LOCATION_CITY": {
                # Şehirler
                "regex": r'\b(Istanbul|Ankara|Izmir|Sivas|Bursa|Antalya|London|New York|Paris|Berlin|Tokyo|Moscow|Dubai|Rome|Amsterdam)\b',
                "weight": 20,
                "flags": re.IGNORECASE,
                "category": "KONUM",
                "label": "Şehir Bilgisi"
            },

            # ================================================================
            # 6. DİĞER (EĞİTİM, KURUMSAL, GİZLİLİK) - WEIGHT: 30-50
            # ================================================================
            "CONFIDENTIAL_DOC": {
                # Sızan belgelerdeki gizlilik ibareleri
                "regex": r'\b(CONFIDENTIAL|GİZLİDİR|INTERNAL USE ONLY|HİZMETE ÖZEL|DO NOT SHARE)\b',
                "weight": 80,
                "flags": re.IGNORECASE,
                "category": "GİZLİLİK",
                "label": "Gizlilik İbaresi"
            },
            "UNIVERSITY_TR": {
                # Üniversite ve Kısaltmalar
                "regex": r'\b(Üniversite|University|Uni|Kampüs|Campus|Fakülte|SCÜ|CÜ|ODTÜ|İTÜ|BOUN|YTÜ|Hacettepe|Bilkent|Harvard|MIT)\b',
                "weight": 30,
                "flags": re.IGNORECASE,
                "category": "EĞİTİM",
                "label": "Eğitim Kurumu"
            },
            "JOB_TITLES": {
                "regex": r'\b(CEO|CTO|CISO|Manager|Director|Engineer|Developer|Admin|Müdür|Yönetici|Uzman|Consultant|HR)\b',
                "weight": 30,
                "flags": re.IGNORECASE,
                "category": "KURUMSAL",
                "label": "Meslek/Ünvan"
            }
        }

    def _compile_patterns(self):
        """Regex desenlerini derler ve hatalı olanları izole eder."""
        for key, data in self.PATTERNS.items():
            flags = data.get("flags", 0)
            try:
                data["compiled_regex"] = re.compile(data["regex"], flags)
            except re.error as e:
                # Loglama yapılabilir
                print(f"Regex Compile Error ({key}): {e}")
                data["compiled_regex"] = re.compile(r"(?!x)x") # Asla eşleşmeyecek desen

    def _validate_luhn(self, card_number: str) -> bool:
        """Kredi kartı doğrulama (Luhn Algoritması)."""
        digits = [int(d) for d in re.sub(r'\D', '', str(card_number))]
        if len(digits) < 13: return False
        checksum = 0
        reverse_digits = digits[::-1]
        for i, digit in enumerate(reverse_digits):
            if i % 2 == 1:
                doubled = digit * 2
                checksum += doubled - 9 if doubled > 9 else doubled
            else:
                checksum += digit
        return checksum % 10 == 0

    def analyze(self, text_data: str) -> Dict[str, Any]:
        """Metin verisini analiz eder ve risk raporu oluşturur."""
        total_score = 0
        found_details = {}
        category_scores = {cat: 0 for cat in self.CATEGORY_LIMITS}

        if not text_data:
            return {"score": 0, "level": "Güvenli", "details": {}}

        # Metni temizle ve normalize et
        text_clean = str(text_data).replace('\n', ' ').strip()

        for key, p_info in self.PATTERNS.items():
            regex = p_info["compiled_regex"]
            matches = regex.findall(text_clean)

            # Özel doğrulayıcı varsa (Validator)
            if matches and "validator" in p_info:
                candidates = []
                for m in matches:
                    val = " ".join(m) if isinstance(m, tuple) else str(m)
                    candidates.append(val)
                # Doğrulayıcıdan geçenleri al
                matches = [m for m in candidates if p_info["validator"](m)]

            if matches:
                count = len(matches)
                weight = p_info["weight"]
                category = p_info.get("category", "GENEL")
                label = p_info["label"]

                # Puanlama: İlk bulgu tam, sonrakiler %20 ağırlıklı
                item_score = weight + ((count - 1) * (weight * 0.2))

                # Kategori Limiti Uygula
                max_allowed = self.CATEGORY_LIMITS.get(category, 100)
                current_cat_score = category_scores.get(category, 0)

                if current_cat_score < max_allowed:
                    if current_cat_score + item_score > max_allowed:
                        item_score = max_allowed - current_cat_score
                    
                    category_scores[category] = current_cat_score + item_score
                    total_score += item_score

                # Sonuçları temizle ve kaydet
                clean_matches = []
                for m in matches:
                    val = " ".join(m) if isinstance(m, tuple) else str(m)
                    clean_matches.append(val.strip())
                
                # Tekrarları kaldır ve sırala
                unique_matches = sorted(list(set(clean_matches)))
                
                # Raporda göstermek için ilk 5 tanesini al
                found_details[label] = ", ".join(unique_matches[:5])

        # Final Skorlama
        final_score = min(round(total_score), 100)
        
        # Risk Seviyesi Belirleme
        if final_score >= 85: level = "Kritik"
        elif final_score >= 60: level = "Yüksek"
        elif final_score >= 35: level = "Orta"
        else: level = "Düşük"

        return {
            "score": final_score,
            "level": level,
            "details": found_details
        }

# --- SINGLETON INSTANCE ---
# Uygulama boyunca tek bir analizci örneği kullanılır (Performans için)
analyzer = RiskAnalyzer()

def calculate_risk(text_data):
    return analyzer.analyze(text_data)