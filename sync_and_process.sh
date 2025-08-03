#!/bin/bash

# A script könyvtárának meghatározása, hogy bárhonnan futtatható legyen
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Konfiguráció
REMOTE="gdrive:/Csalad"
DEST="/home/viragma/frame-sync/originals"
LOG="/home/viragma/frame-sync/logs/sync.log"
PYTHON_PROCESSOR="$SCRIPT_DIR/venv/bin/python3"
PROCESS_SCRIPT="$SCRIPT_DIR/scripts/process_inbox.py"

# --- A Folyamat ---
echo " " >> "$LOG" # Üres sor a jobb olvashatóságért
echo "========== [$(date)] Új futtatás ==========" >> "$LOG"

# 1. Képek letöltése a Google Drive-ról
echo "[$(date)] Szinkronizálás indul..." >> "$LOG"
rclone sync "$REMOTE" "$DEST" --progress >> "$LOG" 2>&1
echo "[$(date)] Szinkronizálás kész." >> "$LOG"

# 2. Képek feldolgozása és arcfelismerés
echo "[$(date)] Feldolgozás és arcfelismerés indítása..." >> "$LOG"
"$PYTHON_PROCESSOR" "$PROCESS_SCRIPT" >> "$LOG" 2>&1
echo "[$(date)] Feldolgozás vége." >> "$LOG"