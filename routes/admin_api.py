from flask import Blueprint, request, jsonify
import json
import os

admin_api = Blueprint("admin_api", __name__)

HIGHLIGHT_FILTER_PATH = "data/highlight_filter.json"

def load_highlight_filter():
    if os.path.exists(HIGHLIGHT_FILTER_PATH):
        with open(HIGHLIGHT_FILTER_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"names": [], "custom_text": ""}

def save_highlight_filter(names, custom_text):
    with open(HIGHLIGHT_FILTER_PATH, "w", encoding="utf-8") as f:
        json.dump({"names": names, "custom_text": custom_text}, f, ensure_ascii=False, indent=2)

@admin_api.route("/api/highlight_filter", methods=["GET"])
def get_highlight_filter():
    return jsonify(load_highlight_filter())

@admin_api.route("/api/highlight_filter", methods=["POST"])
def set_highlight_filter():
    data = request.get_json(force=True)
    names = data.get("names", [])
    custom_text = data.get("custom_text", "")
    save_highlight_filter(names, custom_text)
    return jsonify({"ok": True})

@admin_api.route("/api/highlight_filter", methods=["DELETE"])
def reset_highlight_filter():
    save_highlight_filter([], "")
    return jsonify({"ok": True})