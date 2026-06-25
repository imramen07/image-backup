import os
from datetime import datetime
from flask import Flask
from db import init_db

app = Flask(__name__)

# config
#STORAGE_BASE = "~/phone-backup"
#API_KEY = os.environ.get("API_KEY", "yourkey")
from local_config import STORAGE_BASE
os.makedirs(STORAGE_BASE, exist_ok = True)

init_db()

# test with in memory known files first
# switch to sqlite later
#known_files = set()
'''
// add when auth
def scan_api_key(f):
    def wrapper(*args, **kwargs):
        if request.headers.get("X-API-Key") != API_KEY:
            return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper
'''
'''
def load_known_files():
    for root, _, files in os.walk(STORAGE_BASE):
        for f in files:
            known_files.add(f)
    print(f"Loaded {len(known_files)} existing photos")

load_known_files()
'''
def get_destination_path(ph_name):
    # organize by date of photo or current date
    # if no date then today
    try:
        parts = ph_name.split('_')
        if len(parts) >= 2 and parts[0].startswith('IMG'):
            # YYYYMMDD
            date_str = parts[1][:8]
            dt = datetime.strptime(date_str, "%Y%m%d")
            year = dt.year
            month = f"{dt.month:02d}"
            day = f"{dt.day:02d}"
        else:
            raise ValueError
    except:
        # fallback today
        now = datetime.now()
        year = now.year
        month = f"{now.month:02d}"
        day = f"{now.day:02d}"

    dir_path = os.path.join(STORAGE_BASE, str(year), month, day)
    os.makedirs(dir_path, exist_ok = True)
    return os.path.join(dir_path, ph_name)