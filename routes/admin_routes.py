# routes/admin_routes.py - JAVÍTVA

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services import data_manager

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin', template_folder='../../templates')

@admin_bp.route('/')
def admin_index():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))
    # Ha már be van lépve, az admin főoldalára irányítunk
    return redirect(url_for('admin_bp.persons_page'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'admin': 
            session['logged_in'] = True
            # Sikeres login után az admin főoldalára megyünk
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
    # --- VÁLTOZÁS ---
    # A helyes template fájlra hivatkozunk
    return render_template('admin.html', persons=persons_data)

# ... (add_person és delete_person változatlan)
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

    # routes/admin_routes.py - A FÁJL VÉGÉRE

@admin_bp.route('/save_config', methods=['POST'])
def save_config_route():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))
    
    # Betöltjük a jelenlegi konfigurációt
    config_data = data_manager.get_config()
    
    # Frissítjük a slideshow beállításokat a formról kapott adatokkal
    slideshow_config = config_data.get('slideshow', {})
    slideshow_config['delay'] = int(request.form.get('delay', 5000))
    slideshow_config['effect'] = request.form.get('effect', 'fade')
    
    config_data['slideshow'] = slideshow_config
    
    # Elmentjük a frissített adatokat
    data_manager.save_config(config_data)
    
    flash('Beállítások sikeresen mentve!', 'success')
    return redirect(url_for('admin_bp.persons_page')) # Visszairányítjuk az admin oldalra