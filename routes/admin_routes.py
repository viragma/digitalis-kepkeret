from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services import data_manager

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin', template_folder='../../templates')

@admin_bp.route('/')
def admin_index():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))
    return redirect(url_for('admin_bp.persons_page'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Ezt a jelszót a configból olvassuk majd
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
    slideshow_config['birthday_boost'] = 'birthday_boost' in request.form
    slideshow_config['randomize_playlist'] = 'randomize_playlist' in request.form
    slideshow_config['clock_size'] = request.form.get('clock_size', '2.5rem')
    slideshow_config['birthday_message'] = request.form.get('birthday_message', 'Boldog Születésnapot!')
    
    config_data['slideshow'] = slideshow_config
    data_manager.save_config(config_data)
    
    flash('Beállítások sikeresen mentve!', 'success')
    return redirect(url_for('admin_bp.persons_page'))

@admin_bp.route('/add_person', methods=['POST'])
def add_person():
    if not session.get('logged_in'): 
        return redirect(url_for('admin_bp.login'))
    
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
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))
        
    persons_data = data_manager.get_persons()

    if name in persons_data:
        del persons_data[name]
        data_manager.save_persons(persons_data)
        flash(f'{name} sikeresen törölve.', 'warning')
            
    return redirect(url_for('admin_bp.persons_page'))

@admin_bp.route('/save_persons', methods=['POST'])
def save_persons_route():
    if not session.get('logged_in'): 
        return redirect(url_for('admin_bp.login'))
    
    # Itt a teljes 'persons' szótárat frissítjük a formról érkező adatokkal
    persons_data = {}
    for key, value in request.form.items():
        # A form mezők neve 'birthday_NÉV'
        if key.startswith('birthday_'):
            person_name = key.replace('birthday_', '')
            persons_data[person_name] = value
            
    data_manager.save_persons(persons_data)
    flash('Születésnapok sikeresen mentve!', 'success')
    return redirect(url_for('admin_bp.persons_page'))