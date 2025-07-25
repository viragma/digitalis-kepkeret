# routes/admin_routes.py - VÉGLEGES, JAVÍTOTT VERZIÓ

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services import data_manager

# Létrehozzuk az admin blueprintet egy '/admin' előtaggal
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin', template_folder='../../templates')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Ezt a jelszót a config.json-ból olvassuk majd
        if request.form['password'] == 'admin': 
            session['logged_in'] = True
            # A redirect a főoldalra mutat, ami a 'main_bp'-ben van
            return redirect(url_for('main_bp.index'))
        else:
            flash('Hibás jelszó!')
    # A render_template relatív a 'templates' mappához, ami a főkönyvtárban van
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
    # Mivel a Blueprint máshol van, meg kell adnunk a template relatív elérési útját
    return render_template('admin/persons.html', persons=persons_data)

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