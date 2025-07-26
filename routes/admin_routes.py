# routes/admin_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services import data_manager
from datetime import datetime

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin', template_folder='../../templates')

def calculate_age(birthday_str):
    if not birthday_str: return None
    try:
        birth_date = datetime.strptime(birthday_str.strip(), '%Y.%m.%d')
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except ValueError:
        return None

@admin_bp.route('/')
def admin_index():
    if not session.get('logged_in'): 
        return redirect(url_for('admin_bp.login'))
    return redirect(url_for('admin_bp.dashboard_page'))

@admin_bp.route('/dashboard')
def dashboard_page():
    if not session.get('logged_in'): 
        return redirect(url_for('admin_bp.login'))
    
    persons_data = data_manager.get_persons()
    config_data = data_manager.get_config()
    for name, data in persons_data.items():
        data['age'] = calculate_age(data.get('birthday'))

    return render_template('admin.html', persons=persons_data, config=config_data)

@admin_bp.route('/known_faces')
def known_faces_page():
    if not session.get('logged_in'): 
        return redirect(url_for('admin_bp.login'))
    return render_template('known_faces.html')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Ezt a jelszót a configból kellene olvasni
        if request.form['password'] == 'admin': 
            session['logged_in'] = True
            return redirect(url_for('admin_bp.dashboard_page'))
        else:
            flash('Hibás jelszó!')
    return render_template('login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_bp.login'))

@admin_bp.route('/save_config', methods=['POST'])
def save_config_route():
    if not session.get('logged_in'): 
        return redirect(url_for('admin_bp.login'))
    
    config_data = data_manager.get_config()
    slideshow_config = config_data.get('slideshow', {})
    
    slideshow_config['interval'] = int(request.form.get('interval', 10000))
    slideshow_config['transition_speed'] = int(request.form.get('transition_speed', 1000))
    slideshow_config['blur_strength'] = int(request.form.get('blur_strength', 20))
    slideshow_config['image_filter'] = request.form.get('image_filter', 'contrast(1.05) saturate(1.1)')
    slideshow_config['zoom_enabled'] = 'zoom_enabled' in request.form
    slideshow_config['enable_clock'] = 'enable_clock' in request.form
    slideshow_config['birthday_boost_ratio'] = int(request.form.get('birthday_boost_ratio', 75))
    slideshow_config['randomize_playlist'] = 'randomize_playlist' in request.form
    slideshow_config['clock_size'] = request.form.get('clock_size', '2.5rem')
    slideshow_config['birthday_message'] = request.form.get('birthday_message', 'Boldog Születésnapot!')
    slideshow_config['show_upcoming_birthdays'] = 'show_upcoming_birthdays' in request.form
    slideshow_config['upcoming_days_limit'] = int(request.form.get('upcoming_days_limit', 30))
    
    config_data['slideshow'] = slideshow_config
    data_manager.save_config(config_data)
    
    flash('Beállítások sikeresen mentve!', 'success')
    return redirect(url_for('admin_bp.dashboard_page'))

@admin_bp.route('/add_person', methods=['POST'])
def add_person():
    if not session.get('logged_in'): 
        return redirect(url_for('admin_bp.login'))
    
    name = request.form.get('name')
    birthday_from_form = request.form.get('birthday', '')
    
    birthday_to_store = birthday_from_form.replace('-', '.') if birthday_from_form else ""
    
    persons_data = data_manager.get_persons()
    if name and name not in persons_data:
        persons_data[name] = {"birthday": birthday_to_store, "profile_image": None}
        data_manager.save_persons(persons_data)
        flash(f'{name} sikeresen hozzáadva.', 'success')
            
    return redirect(url_for('admin_bp.dashboard_page'))

@admin_bp.route('/delete_person/<name>')
def delete_person(name):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))
        
    persons_data = data_manager.get_persons()

    if name in persons_data:
        del persons_data[name]
        data_manager.save_persons(persons_data)
        flash(f'{name} sikeresen törölve.', 'warning')
            
    return redirect(url_for('admin_bp.dashboard_page'))