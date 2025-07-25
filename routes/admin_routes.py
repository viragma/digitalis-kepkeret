# routes/admin_routes.py - JAVÍTVA A BIZTONSÁGOS MENTÉSSEL

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services import data_manager
# A 'json' importra már itt sincs szükség
# import json

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'admin': # Ezt később a configból olvassuk
            session['logged_in'] = True
            return redirect(url_for('main_bp.index'))
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
        # --- VÁLTOZÁS ---
        # A régi "with open(...)" helyett a biztonságos mentést használjuk
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
        # --- VÁLTOZÁS ---
        # Itt is a biztonságos mentést használjuk
        data_manager.save_persons(persons_data)
        flash(f'{name} sikeresen törölve.', 'warning')
            
    return redirect(url_for('admin_bp.persons_page'))