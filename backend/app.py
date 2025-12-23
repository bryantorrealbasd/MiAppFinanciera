import os
import sqlite3
import requests
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'datos.db')

# --- CONEXIÓN SEGURA CON TUS DATOS DE RENDER ---
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

# Inicialización de tablas profesionales
with get_db() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, saldo_usdt REAL, btc_auto REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS pagos (id INTEGER PRIMARY KEY, monto REAL, moneda TEXT, status TEXT, comprobante TEXT)')
    if not conn.execute("SELECT * FROM usuarios WHERE id = 1").fetchone():
        conn.execute("INSERT INTO usuarios VALUES (1, 100.0, 0.005)") # Saldo inicial de prueba
    conn.commit()

@app.route('/')
def dashboard():
    with get_db() as conn:
        user = conn.execute("SELECT * FROM usuarios WHERE id = 1").fetchone()
    
    # Tasas de cambio dinámicas (Base 1 USDT)
    tasas = {"VES": 54.50, "COP": 3980.0, "ARS": 980.0, "BRL": 5.10}
    saldo = user['saldo_usdt']
    conv = {k: saldo * v for k, v in tasas.items()}

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"><title>PRO BROKER GLOBAL</title>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <style>
            body { background: #060606; color: white; font-family: sans-serif; margin: 0; }
            .main { display: flex; height: 100vh; }
            .sidebar { width: 350px; background: #121212; padding: 20px; border-right: 1px solid #333; overflow-y: auto; }
            .card { background: #1e1e1e; padding: 15px; border-radius: 12px; margin-bottom: 15px; border-left: 4px solid #f3ba2f; }
            .currency { display: flex; justify-content: space-between; font-size: 0.85rem; margin: 5px 0; color: #848e9c; }
            .btn-buy { background: #2ebd85; color: white; width: 100%; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
            #tv_chart { flex: 1; }
        </style>
    </head>
    <body>
        <div class="main">
            <div class="sidebar">
                <h2 style="color:#f3ba2f; margin-bottom:25px;">BROKER ADVANCED</h2>
                <div class="card">
                    <small style="color:#848e9c;">SALDO TOTAL (USDT)</small>
                    <div style="font-size: 2rem; font-weight: bold;">$ {{ "%.2f"|format(saldo) }}</div>
                    <hr style="border:0.1px solid #333; margin:15px 0;">
                    <div class="currency"><span>Pesos Col (COP)</span><span style="color:white;">{{ "{:,.0f}".format(conv['COP']) }}</span></div>
                    <div class="currency"><span>Pesos Arg (ARS)</span><span style="color:white;">{{ "{:,.0f}".format(conv['ARS']) }}</span></div>
                    <div class="currency"><span>Real Bra (BRL)</span><span style="color:white;">{{ "{:,.2f}".format(conv['BRL']) }}</span></div>
                    <div class="currency"><span>Bolívares (VES)</span><span style="color:white;">{{ "{:,.2f}".format(conv['VES']) }}</span></div>
                </div>
                <div class="card" style="border-left-color: #2ebd85;">
                    <h4 style="margin:0;">AUTO-TRADING BOT</h4>
                    <p style="font-size:0.8rem;">Operando con: <b style="color:white;">{{ btc_auto }} BTC</b></p>
                </div>
                <button class="btn-buy" onclick="location.href='/admin_panel'">ADMINISTRAR PAGOS</button>
            </div>
            <div id="tv_chart"></div>
        </div>
        <script>
            new TradingView.widget({"autosize": true, "symbol": "BINANCE:BTCUSDT", "interval": "1", "theme": "dark", "container_id": "tv_chart", "locale": "es"});
        </script>
    </body>
    </html>
    ''', saldo=saldo, conv=conv, btc_auto=user['btc_auto'])

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin():
    with get_db() as conn:
        pagos = conn.execute("SELECT * FROM pagos WHERE status = 'PENDIENTE'").fetchall()

    if request.method == 'POST':
        accion = request.form.get('accion')
        if accion == "validar":
            p_id = request.form.get('p_id')
            monto = float(request.form.get('monto'))
            with get_db() as conn:
                conn.execute("UPDATE pagos SET status = 'REAL' WHERE id = ?", (p_id,))
                conn.execute("UPDATE usuarios SET saldo_usdt = saldo_usdt + ? WHERE id = 1", (monto,))
                conn.commit()
            enviar_alerta(f"✅ PAGO APROBADO: +{monto} USDT añadidos al balance.")
        return redirect('/admin_panel')

    return render_template_string('''
        <body style="background:#000; color:#fff; padding:30px; font-family:sans-serif;">
            <h2>ADMIN: VERIFICACIÓN DE PAGOS</h2>
            <div style="border:1px solid #333; padding:20px; border-radius:10px;">
                {% for p in pagos %}
                    <div style="background:#111; padding:15px; margin-bottom:10px; border-radius:5px;">
                        <p>ID: {{ p.id }} | Monto: {{ p.monto }} USDT</p>
                        <form method="POST">
                            <input type="hidden" name="accion" value="validar">
                            <input type="hidden" name="p_id" value="{{ p.id }}">
                            <input type="hidden" name="monto" value="{{ p.monto }}">
                            <button type="submit" style="background:#2ebd85; color:white; border:none; padding:10px; cursor:pointer;">ES PAGO REAL (ACREDITAR)</button>
                        </form>
                    </div>
                {% else %}
                    <p style="color:#444;">No hay pagos esperando validación.</p>
                {% endfor %}
            </div>
            <br><a href="/" style="color:#f3ba2f;">Volver al Dashboard</a>
        </body>
    ''', pagos=pagos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

