# routes/api/slideshow.py
from flask import Blueprint, jsonify
from services import data_manager, theme_engine
from datetime import datetime, date, timedelta

slideshow_api_bp = Blueprint('slideshow_api_bp', __name__, url_prefix='/api')

@slideshow_api_bp.route('/birthday_info', methods=['GET'])
def get_birthday_info():
    config = data_manager.get_config()
    slideshow_config = config.get('slideshow', {})
    if not slideshow_config.get('birthday_boost_ratio', 0) > 0: return jsonify({})

    birthday_person_name = data_manager.get_todays_birthday_person()
    if birthday_person_name:
        persons = data_manager.get_persons()
        birthday_str = persons.get(birthday_person_name, {}).get('birthday')
        try:
            birthday = datetime.strptime(birthday_str.replace('.', '').strip(), '%Y%m%d')
            age = datetime.now().year - birthday.year
            message = slideshow_config.get('birthday_message', 'Boldog Születésnapot!')
            return jsonify({"name": birthday_person_name, "age": age, "message": message})
        except (ValueError, TypeError): 
            return jsonify({})
            
    return jsonify({})

@slideshow_api_bp.route('/upcoming_birthdays', methods=['GET'])
def get_upcoming_birthdays():
    config = data_manager.get_config()
    slideshow_config = config.get('slideshow', {})
    if not slideshow_config.get('show_upcoming_birthdays', True): return jsonify([])

    limit_days = slideshow_config.get('upcoming_days_limit', 30)
    persons = data_manager.get_persons()
    today = date.today()
    upcoming = []

    for name, data in persons.items():
        birthday_str = data.get("birthday")
        if not birthday_str: continue
        
        try:
            birth_date = datetime.strptime(birthday_str.strip(), '%Y.%m.%d').date()
            next_birthday = birth_date.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            
            days_left = (next_birthday - today).days
            
            if 0 <= days_left <= limit_days:
                upcoming.append({"name": name, "days_left": days_left})

        except (ValueError, TypeError):
            continue
    
    upcoming.sort(key=lambda x: x['days_left'])
    return jsonify(upcoming)

@slideshow_api_bp.route('/active_theme', methods=['GET'])
def get_active_theme_api():
    active_themes = theme_engine.get_active_themes()
    return jsonify(active_themes)