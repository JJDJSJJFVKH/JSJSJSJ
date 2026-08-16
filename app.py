from flask import Flask, request, jsonify, render_template
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL', 'locations.db')

def get_db_connection():
    if DATABASE_URL.startswith('postgres'):
        conn = psycopg2.connect(DATABASE_URL)
    else:
        import sqlite3
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    if DATABASE_URL.startswith('postgres'):
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ubicaciones (
                id SERIAL PRIMARY KEY,
                latitud DOUBLE PRECISION,
                longitud DOUBLE PRECISION,
                precision DOUBLE PRECISION,
                user_agent TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ubicaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitud REAL,
                longitud REAL,
                precision REAL,
                user_agent TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO ubicaciones (latitud, longitud, precision, user_agent) VALUES (%s, %s, %s, %s)',
        (data['latitud'], data['longitud'], data.get('precision'), data.get('user_agent'))
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/ver-ubicaciones')
def ver_ubicaciones():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM ubicaciones ORDER BY fecha DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()

    html = '<h1>Ubicaciones guardadas</h1><table border="1"><tr><th>ID</th><th>Latitud</th><th>Longitud</th><th>Precisión</th><th>Fecha</th></tr>'
    for row in rows:
        html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[5]}</td></tr>'
    html += '</table>'
    return html

@app.route('/mapa')
def mapa():
    return '<h1>Redirigido correctamente</h1>'

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
