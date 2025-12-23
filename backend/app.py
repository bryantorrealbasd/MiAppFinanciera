import os
import sqlite3
import requests
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'datos.db')

# --- ESTO SE CONECTA A TUS VARIABLES DE RENDER ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('MI_CHAT_ID')

def enviar_alerta(mensaje):
    if not TOKEN or not CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": mensaje}, timeout=5)
    except: pass

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Inicialización de Base de Datos
with get_db() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, saldo_usdt REAL, btc_auto REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS pagos (id INTEGER PRIMARY KEY, monto REAL, moneda TEXT, status TEXT)')
    if not conn.execute("SELECT * FROM usuarios WHERE id = 1").fetchone():
        conn.execute("INSERT INTO usuarios VALUES (1, 0.0, 0.0)")
    conn.commit()

@app.route('/')
def dashboard():
    with get_db() as conn:
        user = conn.execute("SELECT * FROM usuarios WHERE id = 1").fetchone()
    
    # TASAS MULTIMONEDA
    tasas = {"VES": 54.50, "COP": 3980.0, "ARS": 980.0, "BRL": 5.10}
    saldo = user['saldo_usdt']
    conv = {k: saldo * v for k, v in tasas.items()}

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BROKER GLOBAL PRO</title>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <style>
            body { background: #060606; color: white; font-family: sans-serif; margin: 0; }
            .main { display: flex; flex-direction: row; height: 100vh; }
            .sidebar { width: 350px; background: #121212; padding: 20px; border-right: 1px solid #333; overflow-y: auto; }
            .card { background: #1e1e1e; padding: 15px; border-radius: 12px; margin-bottom: 15px; border-left: 4px solid #f3ba2f; }
            .currency-row { display: flex; justify-content: space-between; font-size: 0.85rem; margin: 8px 0; color: #848e9c; }
            #tv_chart { flex: 1; }
            
            /* ADAPTACIÓN AUTOMÁTICA CELULARES */
            @media (max-width: 768px) {
                .main { flex-direction: column; }
                .sidebar { width: 100%; border-right: none; height: auto; }
                #tv_chart { height: 450px; width: 100%; }
            }
        </style>
    </head>
    <body>
        <div class="main">
            <div class="sidebar">
                <h2 style="color:#f3ba2f;">MI BROKER</h2>
                <div class="card">
                    <small>SALDO TOTAL</small>
                    <div style="font-size: 2rem; font-weight: bold;">$ {{ "%.2f"|format(saldo) }} USDT</div>
                    <hr style="border:0.1px solid #333; margin:15px 0;">
                    <div class="currency-row"><span>Colombia (COP):</span> <b>{{ "{:,.0f}".format(conv['COP']) }}</b></div>
                    <div class="currency-row"><span>Argentina (ARS):</span> <b>{{ "{:,.0f}".format(conv['ARS']) }}</b></div>
                    <div class="currency-row"><span>Brasil (BRL):</span> <b>{{ "{:,.2f}".format(conv['BRL']) }}</b></div>
                </div>
                <button style="background:#2ebd85; width:100%; padding:15px; border:none; color:white; font-weight:bold; border-radius:8px;">DEPOSITAR</button>
            </div>
            <div id="tv_chart"></div>
        </div>
        <script>
            new TradingView.widget({"autosize": true, "symbol": "BINANCE:BTCUSDT", "theme": "dark", "container_id": "tv_chart"});
        </script>
    </body>
    </html>
    ''', saldo=saldo, conv=conv)

@app.route('/admin_panel')
def admin():
    return "Panel de Administración activo para ID 7111219942"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

