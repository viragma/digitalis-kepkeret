# routes/api_routes.py
# Ez a fájl a jövőben törölhető, vagy új, központi API funkciók helye lehet.
# Jelenleg üres, mert minden funkciót a saját blueprintjébe szerveztünk.

from flask import Blueprint

# Létrehozunk egy üres blueprintet, hogy a meglévő importok ne okozzanak hibát.
# Ezt a sort később, a takarítás során törölhetjük.
api_bp = Blueprint('api_bp_placeholder', __name__)