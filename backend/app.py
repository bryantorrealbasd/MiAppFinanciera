from flask import Flask, render_template_string, request, session, redirect
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_maestra_trading_pro_2025'

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

# --- INTERFAZ PROFESIONAL ---
LOGIN_HTML = '''
<body style="background:#010409; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
    <div style="background:#0d1117; padding:40px; border-radius:15px; border:1px solid #30363d; text-align:center; width:300px;">
        <h2 style="color:#58a6ff;">Trading Pro Terminal</h2>
        <form action="/login" method="POST">
            <input name="email" type="email" placeholder="Correo Electrónico" required style="width:100%; padding:12px; margin:10px 0; background:#010409; border:1px solid #30363d; color:white; border-radius:5px;">
            <div style="font-size:11px; color:#8b949e; margin-bottom:15px; text-align:left;">
                <input type="checkbox" required> Acepto los Términos de Riesgo y Privacidad.
            </div>
            <button style="width:100%; padding:12px; background:#238636; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">INGRESAR</button>
        </form>
    </div>
</body>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Trading Pro | Live Terminal</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background:#010409; color:#c9d1d9; font-family:sans-serif; margin:0; display:grid; grid-template-rows: 60px 1fr; height:100vh; }
        .nav { background:#161b22; border-bottom:1px solid #30363d; display:flex; justify-content:space-between; align-items:center; padding:0 25px; }
        .main-container { display:grid; grid-template-columns: 280px 1fr 320px; gap:10px; padding:10px; overflow:hidden; }
        .panel { background:#0d1117; border:1px solid #30363d; border-radius:10px; padding:15px; display:flex; flex-direction:column; }
        .price-card { background:#161b22; padding:15px; border-radius:8px; margin-bottom:15px; border-left: 4px solid #58a6ff; }
        .btn-action { width:100%; padding:12px; border:none; border-radius:6px; cursor:pointer; font-weight:bold; margin-top:10px; color:white; }
        #btc-price { font-size: 22px; font-weight: bold; transition: all 0.3s; }
        .up { color: #3fb950; } .down { color: #f85149; }
    </style>
</head>
<body>
    <div class="nav">
        <div style="font-size:20px; font-weight:bold; color:#58a6ff;"><i class="fas fa-microchip"></i> QUANTUM AI</div>
        <div><i class="fas fa-user-circle"></i> {{ user }} | <a href="/logout" style="color:#f85149; text-decoration:none; margin-left:15px;">Cerrar Sesión</a></div>
    </div>

    <div class="main-container">
        <div class="panel">
            <h4 style="margin-top:0;"><i class="fas fa-satellite-dish"></i> Algoritmo Quantum</h4>
            <div id="signal-box" style="padding:15px; border-radius:8px; background:rgba(88,166,255,0.1); border:1px solid #58a6ff;">
                <small>Estado: Escaneando Binance...</small>
                <div id="signal-text" style="font-weight:bold; margin-top:10px; font-size:14px;">Iniciando sistema...</div>
            </div>
            <div class="price-card" style="margin-top:20px;">
                <small>BTC/USDT LIVE</small>
                <div id="btc-price">$--.--</div>
                <small id="btc-change">--%</small>
            </div>
        </div>

        <div class="panel" style="padding:0; overflow:hidden;">
            <div id="tradingview_widget" style="height:100%;"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
              new TradingView.widget({
                "autosize": true, "symbol": "BINANCE:BTCUSDT", "interval": "1", "timezone": "Etc/UTC",
                "theme": "dark", "style": "1", "locale": "es", "enable_publishing": false, "hide_side_toolbar": false, "container_id": "tradingview_widget"
              });
            </script>
        </div>

        <div class="panel">
            <h4 style="margin-top:0;"><i class="fas fa-wallet"></i> Billetera P2P</h4>
            <div style="background:#161b22; padding:20px; border-radius:8px; text-align:center;">
                <small style="color:#8b949e;">Balance Neto</small>
                <div style="font-size:28px; color:#3fb950; font-weight:bold;">$1,250.00 <small style="font-size:12px;">USDT</small></div>
            </div>

            <h5 style="margin-bottom:10px;"><i class="fas fa-university"></i> Depósito Local</h5>
            <input type="number" placeholder="Monto a depositar" style="width:100%; padding:10px; background:#010409; border:1px solid #30363d; color:white; border-radius:5px; margin-bottom:10px; box-sizing:border-box;">
            <input type="text" placeholder="Nro de Referencia" style="width:100%; padding:10px; background:#010409; border:1px solid #30363d; color:white; border-radius:5px; margin-bottom:10px; box-sizing:border-box;">
            <button class="btn-action" style="background:#238636;">CONFIRMAR PAGO</button>

            <div style="margin-top:auto; padding:10px; background:rgba(248,81,73,0.1); border:1px solid #f85149; border-radius:8px; font-size:11px;">
                <i class="fas fa-user-shield"></i> <strong>Asistente Legal:</strong><br>
                Todas las transacciones son auditadas. El uso de referencias falsas resultará en el bloqueo de la cuenta.
            </div>
        </div>
    </div>

    <script>
        const btcDisplay = document.getElementById('btc-price');
        const btcChange = document.getElementById('btc-change');
        const signalText = document.getElementById('signal-text');
        
        // WebSocket de Binance para datos reales
        const ws = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@ticker');

        ws.onmessage = (event) => {
            let data = JSON.parse(event.data);
            let price = parseFloat(data.c).toFixed(2);
            let change = parseFloat(data.P).toFixed(2);
            
            btcDisplay.innerText = `$${price}`;
            btcDisplay.className = change >= 0 ? 'up' : 'down';
            btcChange.innerText = `${change}%`;
            btcChange.className = change >= 0 ? 'up' : 'down';

            // Lógica del Algoritmo Quantum
            if (change > 0.10) {
                signalText.innerText = "SEÑAL: COMPRA FUERTE (LONG)";
                signalText.style.color = "#3fb950";
            } else if (change < -0.10) {
                signalText.innerText = "SEÑAL: VENTA FUERTE (SHORT)";
                signalText.style.color = "#f85149";
            } else {
                signalText.innerText = "ESTADO: MERCADO LATERAL - ESPERAR";
                signalText.style.color = "#58a6ff";
            }
        };
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

