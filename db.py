import sqlite3
from local_config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_name TEXT,
    stored_name TEXT,
    stored_path TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    return conn