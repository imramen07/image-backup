# pkg update
# pkg install python
# pip install requests
# pkg install cronie -y
# crond
# crontab -e

import os
import sqlite3
import json
import time
import requests
from datetime import datetime
from local_config import SERVER_URL

# config
PHOTO_DIR = os.path.expanduser("~/storage/dcim/Camera")
DB_PATH = os.path.expanduser("~/photo_state.db")
EXT = ('.jpg', '.jpeg', '.png')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS photos
    (filename TEXT PRIMARY KEY,
    mtime REAL,
    uploaded INTEGER DEFAULT 1,
    server_filename TEXT)''')
    conn.commit()
    return conn

def get_current_files():
    files = {}
    for f in os.listdir(PHOTO_DIR):
        if f.lower().endswith(EXT):
            path = os.path.join(PHOTO_DIR, f)
            mtime = os.path.getmtime(path)
            files[f] = mtime
    return files

def check_internet():
    # check server reachable
    try:
        print(f"Pinging {SERVER_URL}/ping")
        r = requests.get(f"{SERVER_URL}/ping", timeout=10)
        print(f"Response code: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"Ping fail: {e}")
        return False

def upload_file(fname, fpath):
    url = f"{SERVER_URL}/upload"
    with open(fpath, 'rb') as f:
        files = {'photo': (fname, f, 'image/jpeg')}
        try:
            r = requests.post(url, files=files, timeout=30)
            if r.status_code == 200:
                data = r.json()
                return True, data.get('saved_as', fname)
            else:
                return False, None
        except:
            return False, None

def notify_deletion(filenames):
    if not filenames:
        return True
    url = f"{SERVER_URL}/delete"
    payload = {"filenames": filenames}
    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.status_code == 200
    except:
        return False

def main():
    if not check_internet():
        print("Server not available")
        return
    conn = init_db()
    c = conn.cursor()

    # get state of folder
    current_files = get_current_files()
    current_set = set(current_files.keys())

    # get known from db
    c.execute("SELECT filename, mtime, server_filename FROM photos WHERE uploaded=1")
    db_rows = {row[0]: (row[1], row[2]) for row in c.fetchall()}
    db_set = set(db_rows.keys())

    # get deleteions
    # in db but not in phone
    # del from server
    del_files = db_set - current_set
    if del_files:
        # make list of server side names
        #ser_names = [db_rows[fname][1] for fname in del_files if db_rows[fname][1] is not None]
        ser_names = []
        for fname in del_files:
            name_on_server = db_rows[fname][1]
            if name_on_server is not None:
                ser_names.append(name_on_server)
            else:
                # if no name on server then use og name
                ser_names.append(fname)
        #ser_names = [name or fname for fname, name in zip(del_files, ser_names)]
        print(f"Deleting {len(ser_names)} files from server: {ser_names}")
        if notify_deletion(ser_names):
            for fname in del_files:
                c.execute("DELETE FROM photos WHERE filename=?", (fname,))
            conn.commit()
            print("Deletions mirrored")
    
    # get new files
    to_push = []
    for fname, mtime in current_files.items():
        if fname not in db_set:
            to_push.append(fname)
        else:
            # check modifications by change in time
            # use [0], return tuple
            if abs(mtime - db_rows[fname][0]) > 1.0: # 1 sec tolerance
                to_push.append(fname)
    if not to_push:
        print("No new files")
        conn.close()
        return
    
    print(f"Uploading {len(to_push)} files")
    for fname in to_push:
        fpath = os.path.join(PHOTO_DIR, fname)
        if not os.path.exists(fpath):
            continue
        # call once, unpack tuple
        success, name_on_server = upload_file(fname, fpath)
        if success:
            mtime = os.path.getmtime(fpath)
            # fix: add name on server colmn
            c.execute("INSERT OR REPLACE INTO photos (filename, mtime, uploaded, server_filename) VALUES (?, ?, 1, ?)",
            (fname, mtime, name_on_server))
            conn.commit()
            print(f"Uploaded {fname} as {name_on_server}")
        else:
            print(f"Failed to upload {fname}")
    conn.close()

if __name__ == "__main__":
    main()