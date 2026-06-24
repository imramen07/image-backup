import os
import shutil
from flask import request, jsonify
from server import STORAGE_BASE, app
from server import known_files
from server import get_destination_path

@app.route('/upload', methods=['POST'])
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
    known_files.add(os.path.basename(destination))
    print(f"Saved: {destination}")
    return jsonify({"status": "ok", "saved_as": os.path.basename(destination)}), 200

@app.route('/delete', methods=['POST'])
def delete_photo():
    # get list of names to del
    lis = request.get_json()
    if not lis or 'filenames' not in lis:
        return jsonify({"error": "Missing files"}), 400

    deleted = []
    not_found = []
    for fname in lis['filenames']:
        found = False
        for root, _, files in os.walk(STORAGE_BASE):
            if fname in files:
                fpath = os.path.join(root, fname)
                os.remove(fpath)
                deleted.append(fname)
                known_files.discard(fname)
                found = True
                break
        if not found:
            not_found.append(fname)
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