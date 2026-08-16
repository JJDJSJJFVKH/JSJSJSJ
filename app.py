from flask import Flask, request, jsonify, render_template, g, url_for
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
TARGET_TIKTOK = "https://vt.tiktok.com/ZSVN7YNTV/"
DATABASE = os.path.join(app.root_path, 'locations.db')

# --- Database helpers ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute(
        '''CREATE TABLE IF NOT EXISTS locations (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               created_at TEXT NOT NULL,
               ip TEXT,
               user_agent TEXT,
               consent INTEGER,
               latitude REAL,
               longitude REAL
           )'''
    )
    db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize DB at startup
with app.app_context():
    init_db()

# --- Routes ---
@app.route('/')
def index():
    # Basic logging of access
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
    else:
        ip = request.remote_addr or ''
    user_agent = request.headers.get('User-Agent', '')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{now} {ip} {user_agent} GET /", flush=True)

    # Render transparent consent UI
    return render_template('index.html', target=TARGET_TIKTOK)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/guardar-ubicacion', methods=['POST'])
def recibir_ubicacion():
    try:
        datos = request.get_json(silent=True)
        if not datos:
            # Missing or invalid JSON
            return jsonify({"status": "error", "message": "JSON inválido o vacío"}), 400

        latitud = datos.get('latitud')
        longitud = datos.get('longitud')
        consent = datos.get('consent', True)

        forwarded = request.headers.get('X-Forwarded-For', '')
        if forwarded:
            ip = forwarded.split(',')[0].strip()
        else:
            ip = request.remote_addr or ''
        user_agent = request.headers.get('User-Agent', '')
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Save to SQLite
        db = get_db()
        db.execute(
            'INSERT INTO locations (created_at, ip, user_agent, consent, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)',
            (now, ip, user_agent, 1 if consent else 0, latitud, longitud)
        )
        db.commit()

        # Log to stdout
        print(f"{now} {ip} GEO lat:{latitud} lon:{longitud} consent:{consent} UA:{user_agent}", flush=True)

        return jsonify({"status": "exito"}), 200

    except Exception as e:
        # Avoid exposing internals; log server-side and return generic error
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        forwarded = request.headers.get('X-Forwarded-For', '')
        ip = forwarded.split(',')[0].strip() if forwarded else (request.remote_addr or '')
        user_agent = request.headers.get('User-Agent', '')
        print(f"{now} ERROR guardar-ubicacion from {ip} UA:{user_agent} -> {e}", flush=True)
        return jsonify({"status": "error", "message": "Ocurrió un error procesando la solicitud"}), 500

if __name__ == '__main__':
    # For local debugging only. In production use gunicorn as configured in Procfile.
    app.run(host='0.0.0.0', port=5000, debug=False)
