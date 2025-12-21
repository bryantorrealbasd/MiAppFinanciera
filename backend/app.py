from flask import Flask, render_template_string, request, session, redirect
import os
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_maestra_trading_pro_2025'

# --- CONFIGURACIÓN DE TU WHATSAPP (CON CÓDIGO 58 ANEXADO) ---
NUMERO_CELULAR = "584165696847" 
API_KEY_WHA = "ESCRIBE_AQUI_TU_CODIGO" # <--- ¡PON AQUÍ TU CÓDIGO DE 6 DÍGITOS!

def enviar_alerta_pago(usuario, monto, ref):
    mensaje = f"🚀 *Trading Pro: NUEVO PAGO*\n\n👤 Usuario: {usuario}\n💰 Monto: {monto} USDT\n🔢 Ref: {ref}\n\n⚠️ Verifique su banco antes de confirmar."
    url = f"https://api.callmebot.com/whatsapp.php?phone={NUMERO_CELULAR}&text={mensaje}&apikey={API_KEY_WHA}"
    try:
        requests.get(url)
    except:
        print("Error enviando alerta de WhatsApp")

# --- BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS depositos 
                      (id INTEGER PRIMARY KEY, usuario TEXT, monto REAL, ref TEXT, 
                       estado TEXT, fecha TEXT, auditoria TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user' not in session:
        return render_template_string(LOGIN_HTML)
    return render_template_string(DASHBOARD_HTML, user=session['user'])

@app.route('/login', methods=['POST'])
def login():
    session['user'] = request.form['email']
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/notificar', methods=['POST'])
def notificar():
    if 'user' not in session: return redirect('/')
    monto = request.form.get('monto')
    ref = request.form.get('ref')
    user = session['user']
    
    # ENVIAR ALERTA A TU CELULAR
    enviar_alerta_pago(user, monto, ref)
    
    # GUARDAR EN BASE DE DATOS
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO depositos (usuario, monto, ref, estado, fecha, auditoria) VALUES (?,?,?,?,?,?)",
                   (user, monto, ref, 'Pendiente', datetime.now().strftime("%Y-%m-%d %H:%M"), "AUDITORÍA OK"))
    conn.commit()
    conn.close()
    return "<h1>Notificación enviada con éxito. Revisaremos su pago.</h1><a href='/'>Volver</a>"

# --- INTERFAZ VISUAL ---
LOGIN_HTML = '''
<body style="background:#010409; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
    <div style="background:#0d1117; padding:40px; border-radius:15px; border:1px solid #30363d; text-align:center; width:300px;">
        <h2 style="color:#58a6ff;">Trading Pro Terminal</h2>
        <form action="/login" method="POST">
            <input name="email" type="email" placeholder="Correo Electrónico" required style="width:100%; padding:12px; margin:10px 0; background:#010409; border:1px solid #30363d; color:white; border-radius:5px;">
            <button style="width:100%; padding:12px; background:#238636; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">INGRESAR</button>
        </form>
    </div>
</body>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Trading Pro | Live</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background:#010409; color:#c9d1d9; font-family:sans-serif; margin:0; display:grid; grid-template-rows: 60px 1fr; height:100vh; }
        .nav { background:#161b22; border-bottom:1px solid #30363d; display:flex; justify-content:space-between; align-items:center; padding:0 25px; }
        .main { display:grid; grid-template-columns: 280px 1fr 320px; gap:10px; padding:10px; overflow:hidden; }
        .panel { background:#0d1117; border:1px solid #30363d; border-radius:10px; padding:15px; }
        #btc-price { font-size: 22px; font-weight: bold; }
        .up { color: #3fb950; } .down { color: #f85149; }
    </style>
</head>
<body>
    <div class="nav">
        <div style="font-size:20px; font-weight:bold; color:#58a6ff;"><i class="fas fa-microchip"></i> QUANTUM AI</div>
        <div>{{ user }} | <a href="/logout" style="color:#f85149; text-decoration:none;">Salir</a></div>
    </div>
    <div class="main">
        <div class="panel">
            <h4><i class="fas fa-satellite-dish"></i> Algoritmo</h4>
            <div id="btc-price">$--.--</div>
            <div id="signal-text" style="margin-top:10px; font-weight:bold;">Cargando...</div>
        </div>
        <div class="panel" style="padding:0;">
            <div id="tradingview_widget" style="height:100%;"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
              new TradingView.widget({"autosize": true, "symbol": "BINANCE:BTCUSDT", "interval": "1", "theme": "dark", "container_id": "tradingview_widget"});
            </script>
        </div>
        <div class="panel">
            <h4><i class="fas fa-wallet"></i> Billetera</h4>
            <div style="font-size:24px; color:#3fb950; font-weight:bold;">$1,250.00 USDT</div>
            <hr style="border:0.5px solid #30363d; margin:20px 0;">
            <form action="/notificar" method="POST">
                <input name="monto" type="number" placeholder="Monto USDT" required style="width:100%; padding:10px; background:#010409; border:1px solid #30363d; color:white; margin-bottom:10px;">
                <input name="ref" type="text" placeholder="Ref. Bancaria" required style="width:100%; padding:10px; background:#010409; border:1px solid #30363d; color:white; margin-bottom:10px;">
                <button style="width:100%; padding:10px; background:#238636; color:white; border:none; cursor:pointer;">CONFIRMAR PAGO</button>
            </form>
        </div>
    </div>
    <script>
        const btcDisplay = document.getElementById('btc-price');
        const signalText = document.getElementById('signal-text');
        const ws = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@ticker');
        ws.onmessage = (event) => {
            let data = JSON.parse(event.data);
            let price = parseFloat(data.c).toFixed(2);
            let change = parseFloat(data.P).toFixed(2);
            btcDisplay.innerText = `$${price}`;
            btcDisplay.className = change >= 0 ? 'up' : 'down';
            signalText.innerText = change > 0 ? "SEÑAL: COMPRA" : "SEÑAL: VENTA";
            signalText.style.color = change > 0 ? "#3fb950" : "#f85149";
        };
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

