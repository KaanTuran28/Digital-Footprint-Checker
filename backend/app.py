from flask import Flask, request, jsonify
import pandas as pd
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Backend dosyasına göre proje kökünde data klasörü
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '../data')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Basit analiz fonksiyonu
def analyze_profile(profile):
    sensitive_info = {}
    risk_score = 0

    if pd.notna(profile.get('email')):
        sensitive_info['emails'] = [profile['email']]
        risk_score += 50

    # Örnek: telefon numarası varsa ek puan
    if pd.notna(profile.get('phone')):
        sensitive_info['phones'] = [profile['phone']]
        risk_score += 30

    # Risk seviyesi belirleme
    risk_level = "Low"
    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 40:
        risk_level = "Medium"

    return {
        "user_id": profile.get('id', ''),
        "name": profile.get('name', ''),
        "role": profile.get('role', ''),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "sensitive_info_detected": sensitive_info,
        "analysis_date": datetime.utcnow().isoformat()
    }

@app.route('/')
def home():
    return "Digital-Footprint-Checker Backend Çalışıyor"

# CSV yükleme endpoint
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        df = pd.read_csv(filepath)

        reports = []
        for _, row in df.iterrows():
            profile = row.to_dict()
            report = analyze_profile(profile)
            reports.append(report)

        return jsonify({"reports": reports})

if __name__ == '__main__':
    app.run(debug=True)
