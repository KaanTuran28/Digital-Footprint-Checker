import re
from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify
from app import db
from app.models import User, Analysis, AnalysisItem
from flask_login import login_user, logout_user, login_required, current_user
from app.services import scraper_service, analysis_service

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if not username or not email or not password:
            flash('Tüm alanları doldurmak zorunludur.')
            return redirect(url_for('main.register'))

        if password != password2:
            flash('Girilen şifreler uyuşmuyor!')
            return redirect(url_for('main.register'))
        
        if len(password) < 8 or not re.search("[A-Z]", password) or not re.search("[a-z]", password) or not re.search("[0-9]", password) or not re.search("[^A-Za-z0-9]", password):
            flash('Şifre belirlenen güvenlik kurallarına uymuyor.')
            return redirect(url_for('main.register'))

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Bu kullanıcı adı veya e-posta zaten kullanılıyor.')
            return redirect(url_for('main.register'))
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Tebrikler, kaydınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.')
        return redirect(url_for('main.login'))
        
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Geçersiz kullanıcı adı veya şifre!')
            return redirect(url_for('main.login'))
        login_user(user)
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        new_password2 = request.form.get('new_password2')
        if not current_user.check_password(current_password):
            flash('Mevcut şifreniz yanlış! Lütfen tekrar deneyin.')
            return redirect(url_for('main.profile'))
        if not new_password:
            flash('Yeni şifre alanı boş bırakılamaz.')
            return redirect(url_for('main.profile'))
        if new_password != new_password2:
            flash('Girilen yeni şifreler uyuşmuyor!')
            return redirect(url_for('main.profile'))
        current_user.set_password(new_password)
        db.session.commit()
        flash('Şifreniz başarıyla güncellendi.')
        return redirect(url_for('main.profile'))
    return render_template('profile.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    past_analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).all()
    return render_template('dashboard.html', past_analyses=past_analyses)

@bp.route('/start-analysis', methods=['POST'])
@login_required
async def start_analysis():
    data = request.get_json()
    deep_scan = data.get('deep_scan', False)
    usernames_to_scan = {
        "instagram": data.get("instagram_username"),
        "x": data.get("x_username"),
        "linkedin": data.get("linkedin_username")
    }
    if not any(usernames_to_scan.values()):
        return jsonify({"error": "Lütfen en az bir kullanıcı adı girin."}), 400
    
    scraped_results = await scraper_service.run_concurrent_scraping(usernames_to_scan, deep_scan=deep_scan)
    
    new_analysis = Analysis(user_id=current_user.id)
    db.session.add(new_analysis)
    db.session.commit()

    results_for_json = []
    for result in scraped_results:
        analysis_data = analysis_service.calculate_risk(result.get('data'))
        item = AnalysisItem(
            analysis_id=new_analysis.id, platform=result.get('platform'),
            profile_username=result.get('username'), risk_score=analysis_data.get('score'),
            risk_level=analysis_data.get('level'), found_data_json=analysis_data.get('details')
        )
        db.session.add(item)
        results_for_json.append({
            "platform": result.get('platform'), "username": result.get('username'),
            "score": analysis_data.get('score'), "level": analysis_data.get('level'),
            "details": analysis_data.get('details')
        })
    db.session.commit()
    return jsonify(success=True, results=results_for_json)

@bp.route('/analysis/delete/<int:analysis_id>', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    analysis_to_delete = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
    if analysis_to_delete:
        db.session.delete(analysis_to_delete)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Analiz başarıyla silindi.'})
    else:
        return jsonify({'success': False, 'message': 'Analiz bulunamadı veya silme yetkiniz yok.'}), 404

@bp.route('/analysis/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    items = analysis.items
    return render_template('analysis_detail.html', analysis=analysis, items=items)
