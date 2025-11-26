import re

RISK_PATTERNS = {
    "EMAIL": {"regex": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "weight": 25},
    "EMAIL_OBFUSCATED": {"regex": r'\b[A-Za-z0-9._%+-]+\s*\[\s*at\s*\]\s*[A-Za-z0-9.-]+\s*\[\s*dot\s*\]\s*[A-Z|a-z]{2,}\b', "weight": 25, "flags": re.IGNORECASE},
    "PHONE_TR": {"regex": r'\b(0|\+90)?\s*?(\d{3})\s*?(\d{3})\s*?(\d{2})\s*?(\d{2})\b', "weight": 30},
    "BIRTH_DATE": {"regex": r'\b(\d{1,2}[\s\./-]\d{1,2}[\s\./-]\d{2,4})\b', "weight": 35},
    "BIRTH_DATE_KEYWORD": {"regex": r'(Doğum\sTarihi|Doğum\sGünü|Doğdu)\s*:?\s*(\d{1,2}\s(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s\d{2,4})', "weight": 35, "flags": re.IGNORECASE},
    "ADDRESS": {"regex": r'\b(sokak|cadde|mahalle|apartman|no:|sk\.|mh\.)\b', "weight": 20, "flags": re.IGNORECASE},
    "VACATION": {"regex": r'\b(tatildeyim|tatilde|seyahat|otel|rezervasyon|yurtdışı)\b', "weight": 15, "flags": re.IGNORECASE}
}

def calculate_risk(text_data):
    total_score, found_details = 0, {}
    if not text_data: text_data = ""
    for key, p_info in RISK_PATTERNS.items():
        matches = re.findall(p_info["regex"], text_data, p_info.get("flags", 0))
        if matches:
            total_score += p_info["weight"]
            item = "".join(filter(None, matches[0])) if isinstance(matches[0], tuple) else matches[0]
            found_details[key.lower()] = item
    
    score = min(total_score, 100)
    level = "Yüksek" if 70 <= score else "Orta" if 40 <= score else "Düşük"
    return {"score": score, "level": level, "details": found_details}