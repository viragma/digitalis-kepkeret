# routes/admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services import data_manager

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin', template_folder='../../templates')

@admin_bp.route('/')
def admin_index():
    if not session.get('logged_in'): return redirect(url_for('admin_bp.login'))
    return redirect(url_for('admin_bp.dashboard_page'))

@admin_bp.route('/dashboard')
def dashboard_page():
    if not session.get('logged_in'): return redirect(url_for('admin_bp.login'))
    persons_data = data_manager.get_persons()
    config_data = data_manager.get_config()
    return render_template('admin.html', persons=persons_data, config=config_data)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
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
    if not session.get('logged_in'): return redirect(url_for('admin_bp.login'))
    config_data = data_manager.get_config()
    slideshow_config = config_data.get('slideshow', {})
    slideshow_config['birthday_boost_ratio'] = int(request.form.get('birthday_boost_ratio', 75))
    # ... egyéb beállítások mentése ...
    config_data['slideshow'] = slideshow_config
    data_manager.save_config(config_data)
    flash('Beállítások sikeresen mentve!', 'success')
    return redirect(url_for('admin_bp.dashboard_page'))

@admin_bp.route('/add_person', methods=['POST'])
def add_person():
    if not session.get('logged_in'): return redirect(url_for('admin_bp.login'))
    name = request.form['name']
    birthday = request.form['birthday']
    persons_data = data_manager.get_persons()
    if name and name not in persons_data:
        persons_data[name] = {"birthday": birthday, "profile_image": None}
        data_manager.save_persons(persons_data)
        flash(f'{name} sikeresen hozzáadva.', 'success')
    return redirect(url_for('admin_bp.dashboard_page'))

@admin_bp.route('/delete_person/<name>')
def delete_person(name):
    if not session.get('logged_in'): return redirect(url_for('admin_bp.login'))
    persons_data = data_manager.get_persons()
    if name in persons_data:
        del persons_data[name]
        data_manager.save_persons(persons_data)
        flash(f'{name} sikeresen törölve.', 'warning')
    return redirect(url_for('admin_bp.dashboard_page'))

@admin_bp.route('/save_persons', methods=['POST'])
def save_persons_route():
    if not session.get('logged_in'): return redirect(url_for('admin_bp.login'))
    persons_data = data_manager.get_persons()
    for key, value in request.form.items():
        if key.startswith('birthday_'):
            person_name = key.replace('birthday_', '')
            if person_name in persons_data:
                persons_data[person_name]['birthday'] = value
    data_manager.save_persons(persons_data)
    flash('Születésnapok sikeresen mentve!', 'success')
    return redirect(url_for('admin_bp.dashboard_page'))