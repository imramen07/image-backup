import os
import shutil
from flask import request, jsonify
from server import STORAGE_BASE, app
from server import get_destination_path
#from server import scan_api_key
from db import get_db

@app.route('/upload', methods=['POST'])
#@scan_api_key
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({"error": "No photo part"}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    # donot overwrite for same name
    base_name = file.filename
    destination = get_destination_path(base_name)

    # append counter for same name existing
    count = 1
    og_destination = destination
    while os.path.exists(destination):
        name, ext = os.path.splitext(base_name)
        new_name = f"{name}_{count}{ext}"
        destination = get_destination_path(new_name)
        count+=1
    file.save(destination)
    stored_name = os.path.basename(destination)
    # insert in db
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO files (original_name, stored_name, stored_path) VALUES (?, ?, ?)",
        (base_name, stored_name, destination)
    )
    conn.commit()
    conn.close()
    print(f"Saved: {destination}")
    return jsonify({"status": "ok", "saved_as": os.path.basename(destination)}), 200

@app.route('/delete', methods=['POST'])
def delete_photo():
    # get list of names to del
    lis = request.get_json()
    if not lis or 'filenames' not in lis:
        return jsonify({"error": "Missing files"}), 400

    conn = get_db()
    c = conn.cursor()
    deleted = []
    not_found = []
    for fname in lis['filenames']:
        # try find stored path for og name
        c.execute("SELECT stored_path FROM files WHERE original_name = ?", (fname,))
        row = c.fetchone()
        if row:
            stored_path = row[0]
            if os.path.exists(stored_path):
                os.remove(stored_path)
            # del from db
            c.execute("DELETE FROM files WHERE original_name = ?", (fname,))
            conn.commit()
            deleted.append(fname)
        else:
            not_found.append(fname)
    conn.close()
    return jsonify({
        "deleted": deleted,
        "not_found": not_found
    }), 200

@app.route('/ping', methods=['GET'])
def ping():
    return "OK", 200

if __name__ == '__main__':
    # run all interf
    app.run(host = '0.0.0.0', port = 5000, debug = False)