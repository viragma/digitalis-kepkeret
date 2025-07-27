# services/event_logger.py
from datetime import datetime
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOG_FILE = os.path.join(PROJECT_ROOT, 'data', 'events.log')
MAX_LOG_LINES = 100

def log_event(message):
    """
    Beír egy eseményt a log fájlba, időbélyeggel ellátva.
    A log fájlt korlátozza, hogy ne nőjön a végtelenségig.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        lines = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        lines.insert(0, log_entry)
        lines = lines[:MAX_LOG_LINES]
        
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    except Exception as e:
        print(f"Hiba a log írása közben: {e}")