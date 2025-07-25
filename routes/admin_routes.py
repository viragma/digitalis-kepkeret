# routes/admin_routes.py - FRISSÍTVE A RÉSZLETES CONFIG MENTÉSÉHEZ

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services import data_manager

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin', template_folder='../../templates')

# ... (admin_index, login, logout, add_person, delete_person, save_persons_route változatlan) ...
@admin_bp.route('/')
def admin_index():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))
    return redirect(url_for('admin_bp.persons_page'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'admin': 
            session['logged_in'] = True
            return redirect(url_for('admin_bp.persons_page'))
        else:
            flash('Hibás jelszó!')
    return render_template('login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_bp.login'))

@admin_bp.route('/persons')
def persons_page():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))
    
    persons_data = data_manager.get_persons()
    config_data = data_manager.get_config()
    
    return render_template('admin.html', persons=persons_data, config=config_data)

# --- VÁLTOZÁS: A mentési logika sokkal okosabb lett ---
@admin_bp.route('/save_config', methods=['POST'])
def save_config_route():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))
    
    # 1. Betöltjük a teljes, meglévő konfigurációt
    config_data = data_manager.get_config()
    
    # 2. Biztosítjuk, hogy a 'slideshow' kulcs létezzen
    if 'slideshow' not in config_data:
        config_data['slideshow'] = {}

    # 3. Csak azokat az értékeket frissítjük, amiket a formon keresztül kaptunk
    # A többi (pl. zoom_start, image_filter) érintetlen marad
    config_data['slideshow']['delay'] = int(request.form.get('delay', 10000))
    config_data['slideshow']['transition_speed'] = int(request.form.get('transition_speed', 1000))
    config_data['slideshow']['blur_strength'] = int(request.form.get('blur_strength', 20))
    
    # A kapcsolókhoz speciális logika kell: csak akkor léteznek a formban, ha be vannak pipálva
    config_data['slideshow']['zoom_enabled'] = 'zoom_enabled' in request.form
    config_data['slideshow']['birthday_boost'] = 'birthday_boost' in request.form
    
    # 4. Elmentjük a teljes, frissített konfigurációt
    data_manager.save_config(config_data)
    
    flash('Beállítások sikeresen mentve!', 'success')
    return redirect(url_for('admin_bp.persons_page'))

@admin_bp.route('/add_person', methods=['POST'])
def add_person():
    if not session.get('logged_in'): return redirect(url_for('admin_bp.login'))
    name = request.form['name']
    birthday = request.form['birthday']
    persons_data = data_manager.get_persons()
    if name and name not in persons_data:
        persons_data[name] = birthday
        data_manager.save_persons(persons_data)
        flash(f'{name} sikeresen hozzáadva.', 'success')
    return redirect(url_for('admin_bp.persons_page'))

@admin_bp.route('/delete_person/<name>')
def delete_person(name):
    if not session.get('logged_in'): return redirect(url_for('admin_bp.login'))
    persons_data = data_manager.get_persons()
    if name in persons_data:
        del persons_data[name]
        data_manager.save_persons(persons_data)
        flash(f'{name} sikeresen törölve.', 'warning')
    return redirect(url_for('admin_bp.persons_page'))

@admin_bp.route('/save_persons', methods=['POST'])
def save_persons_route():
    if not session.get('logged_in'): return redirect(url_for('admin_bp.login'))
    persons_data = {}
    for key, value in request.form.items():
        if key.startswith('birthday_'):
            person_name = key.replace('birthday_', '')
            persons_data[person_name] = value
    data_manager.save_persons(persons_data)
    flash('Születésnapok sikeresen mentve!', 'success')
    return redirect(url_for('admin_bp.persons_page'))