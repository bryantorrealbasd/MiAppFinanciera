from flask import Flask, render_template_string, request, session, redirect, url_for
import os, sqlite3, random, requests

from datetime import datetime

app = Flask(__name__)
app.secret_key = 'quantum_ai_pro_2025'

# --- CONFIGURACIÓN SEGURA ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
MI_CHAT_ID = os.environ.get("MI_CHAT_ID")



TASAS = {'VES': 62.50, 'COP': 4100.0, 'ARS': 1050.0}

def get_db():
    conn = sqlite3.connect('datos.db')
    return conn

# Inicialización con columna de estado del bot
def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, email TEXT, saldo_real REAL, saldo_demo REAL, bot_activo INTEGER DEFAULT 0)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS depositos (id INTEGER PRIMARY KEY, usuario TEXT, monto REAL, moneda TEXT, usdt_equiv REAL, ref TEXT, estado TEXT, fecha TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user' not in session: return render_template_string(LOGIN_HTML)
    if 'mode' not in session: session['mode'] = 'DEMO'
    
    conn = get_db()
    user_data = conn.execute("SELECT saldo_real, saldo_demo, bot_activo FROM usuarios WHERE email=?", (session['user'],)).fetchone()
    conn.close()
    
    saldo = user_data[1] if session['mode'] == 'DEMO' else user_data[0]
    bot_status = user_data[2]
    
    # Simulación de Ganancia Automática si el bot está activo
    if bot_status == 1:
        ganancia = round(random.uniform(0.10, 0.50), 2)
        conn = get_db()
        if session['mode'] == 'DEMO':
            conn.execute("UPDATE usuarios SET saldo_demo = saldo_demo + ? WHERE email=?", (ganancia, session['user']))
        else:
            conn.execute("UPDATE usuarios SET saldo_real = saldo_real + ? WHERE email=?", (ganancia, session['user']))
        conn.commit()
        conn.close()

    return render_template_string(DASHBOARD_HTML, user=session['user'], saldo=saldo, mode=session['mode'], tasas=TASAS, bot_on=bot_status)

@app.route('/toggle_bot')
def toggle_bot():
    conn = get_db()
    user_data = conn.execute("SELECT saldo_real, bot_activo FROM usuarios WHERE email=?", (session['user'],)).fetchone()
    # Solo permite activar si es modo Demo o si tiene saldo real
    if session['mode'] == 'DEMO' or user_data[0] > 0:
        nuevo_estado = 0 if user_data[1] == 1 else 1
        conn.execute("UPDATE usuarios SET bot_activo = ? WHERE email=?", (nuevo_estado, session['user']))
        conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    session['user'] = request.form['email']
    conn = get_db()
    if not conn.execute("SELECT email FROM usuarios WHERE email=?", (session['user'],)).fetchone():
        conn.execute("INSERT INTO usuarios (email, saldo_real, saldo_demo, bot_activo) VALUES (?, 0.0, 10000.0, 0)", (session['user'],))
        conn.commit()
    conn.close()
    return redirect(url_for('index'))

# --- INTERFACES ---
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background:#010409; color:white; font-family:sans-serif; margin:0; }
        .header { display:flex; justify-content:space-between; padding:15px; background:#161b22; border-bottom:1px solid #30363d; }
        .status-bar { background: {{ '#238636' if bot_on else '#da3633' }}; text-align:center; padding:5px; font-size:12px; font-weight:bold; }
        .card { background:#161b22; margin:15px; padding:20px; border-radius:10px; border:1px solid #30363d; }
        .btn-bot { width:100%; padding:15px; border-radius:5px; border:none; font-weight:bold; cursor:pointer; margin-top:10px;
                   background: {{ '#da3633' if bot_on else '#238636' }}; color:white; }
        .alert-box { border-left: 4px solid #f2994a; background:#1c160d; padding:10px; margin:15px; font-size:13px; }
        /* BOTON FLOTANTE SOPORTE */
        .btn-soporte-tg {
            position: fixed;
            bottom: 25px;
            right: 25px;
            background: #0088cc;
            color: white;
            width: 55px;
            height: 55px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            z-index: 1000;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="status-bar">
        BOT STATUS: {{ 'OPERANDO Y GENERANDO' if bot_on else 'INACTIVO - ESPERANDO ACTIVACIÓN' }}
    </div>
    <div class="header">
        <b>QUANTUM BOT AI</b>
        <a href="/switch_mode" style="text-decoration:none;"><span style="color:#f2994a;">{{ mode }}</span></a>
    </div>
    <iframe src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:BTCUSDT&theme=dark" style="width:100%; height:250px; border:none;"></iframe>
    
    <div class="alert-box">
        <b>🔔 SEÑAL RECIENTE:</b> BTC/USDT <br>
        Acción: <span style="color:#3fb950;">COMPRA (BUY)</span> | Confianza: 94%
    </div>

    <div class="card">
        <small>MI BALANCE {{ mode }}</small>
        <h2 style="color:#3fb950;">${{ "{:,.2f}".format(saldo) }} USDT</h2>
        
        <a href="/toggle_bot">
            <button class="btn-bot">
                {{ 'DESACTIVAR BOT AUTOMÁTICO' if bot_on else 'ACTIVAR OPERACIÓN AUTOMÁTICA' }}
            </button>
        </a>
            <a href="https://t.me/SoportteQuantumBryan" class="btn-soporte-tg" target="_blank">
        ✈️
    </a>
</body>
</html>
'''

# --- ARRANQUE DEL SERVIDOR ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

