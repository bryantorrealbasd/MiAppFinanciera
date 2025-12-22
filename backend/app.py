from flask import Flask, render_template_string, request, session, redirect
import os, sqlite3, requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_maestra_2025_global'

# --- CONFIGURACIÓN TELEGRAM ---
USUARIO_TELEGRAM = "TU_USUARIO" 
API_KEY_TEL = "TU_API_KEY" # Pon tus datos cuando el bot responda

def enviar_alerta(mensaje):
    if "TU_API_KEY" in API_KEY_TEL: return
    url = f"https://api.callmebot.com/text.php?user={USUARIO_TELEGRAM}&text={mensaje}&apikey={API_KEY_TEL}"
    requests.get(url)

def init_db():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, email TEXT, saldo REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS depositos (id INTEGER PRIMARY KEY, usuario TEXT, monto REAL, moneda TEXT, banco TEXT, ref TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user' not in session: return render_template_string(LOGIN_HTML)
    conn = sqlite3.connect('datos.db')
    res = conn.execute("SELECT saldo FROM usuarios WHERE email=?", (session['user'],)).fetchone()
    saldo = res[0] if res else 0.0
    conn.close()
    return render_template_string(DASHBOARD_HTML, user=session['user'], saldo=saldo)

@app.route('/login', methods=['POST'])
def login():
    session['user'] = request.form['email']
    conn = sqlite3.connect('datos.db')
    if not conn.execute("SELECT email FROM usuarios WHERE email=?", (session['user'],)).fetchone():
        conn.execute("INSERT INTO usuarios (email, saldo) VALUES (?, 10.0)", (session['user'],))
        conn.commit()
    conn.close()
    return redirect('/')

@app.route('/notificar', methods=['POST'])
def notificar():
    monto = request.form.get('monto')
    moneda = request.form.get('moneda')
    banco = request.form.get('banco')
    ref = request.form.get('ref')
    enviar_alerta(f"💰 NUEVO PAGO: {monto} {moneda} vía {banco}. Ref: {ref}")
    return "<h1>Procesando Depósito...</h1><a href='/'>Volver</a>"

# --- INTERFAZ GLOBAL ---
LOGIN_HTML = '''<body style="background:#010409;color:white;text-align:center;padding:100px;"><h1>QUANTUM GLOBAL AI</h1><form action="/login" method="POST"><input name="email" type="email" placeholder="Email" required style="padding:10px;"><button style="padding:10px;background:#238636;color:white;border:none;">ENTRAR</button></form></body>'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://kit.fontawesome.com/a076d05399.js"></script>
    <style>
        body { background:#010409; color:#c9d1d9; font-family:sans-serif; margin:0; display:flex; flex-direction:column; height:100vh; }
        .header { padding:15px; border-bottom:1px solid #30363d; display:flex; justify-content:space-between; }
        .main-container { display:grid; grid-template-columns: 1fr 350px; flex:1; }
        .chart-area { background:#000; border-right:1px solid #30363d; }
        .sidebar { padding:20px; background:#0d1117; overflow-y:auto; }
        .card { background:#161b22; border:1px solid #30363d; padding:15px; border-radius:10px; margin-bottom:15px; }
        select, input { width:100%; padding:10px; margin:5px 0; background:#010409; color:white; border:1px solid #30363d; border-radius:5px; }
        button { width:100%; padding:12px; background:#238636; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer; }
    </style>
</head>
<body>
    <div class="header">
        <b><i class="fas fa-globe"></i> QUANTUM TERMINAL PRO</b>
        <span>{{user}}</span>
    </div>

    <div class="main-container">
        <div class="chart-area">
            <div class="tradingview-widget-container" style="height:100%;width:100%;">
                <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_7626b&symbol=BINANCE:BTCUSDT&interval=1&hidesidetoolbar=1&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=[]&theme=dark&style=1&timezone=Etc%2FUTC" style="width: 100%; height: 100%; margin: 0; padding: 0;" frameborder="0" allowfullscreen></iframe>
            </div>
        </div>

        <div class="sidebar">
            <div class="card">
                <small style="color:gray;">BILLETERA USDT</small>
                <h2 style="margin:5px 0;">${{saldo}}</h2>
            </div>

            <div class="card">
                <h4><i class="fas fa-university"></i> DEPÓSITO BANCARIO</h4>
                <form action="/notificar" method="POST">
                    <select name="moneda" required>
                        <option value="VES">Bolívares (Venezuela)</option>
                        <option value="COP">Peso Colombiano</option>
                        <option value="ARS">Peso Argentino</option>
                        <option value="BRL">Real Brasilero</option>
                        <option value="USD">Dólares (Zelle/Binance)</option>
                    </select>
                    <select name="banco" required>
                        <option value="Pago Movil">Pago Móvil / Transferencia</option>
                        <option value="Nequi">Nequi / Daviplata</option>
                        <option value="MercadoPago">Mercado Pago</option>
                        <option value="BinancePay">Binance Pay (ID)</option>
                    </select>
                    <input name="monto" type="number" placeholder="Monto en moneda local" required>
                    <input name="ref" type="text" placeholder="Número de Referencia" required>
                    <button type="submit">CONFIRMAR TRANSACCIÓN</button>
                </form>
            </div>
            
            <p style="font-size:11px;color:gray;text-align:center;">El bot Quantum procesará la conversión a USDT automáticamente tras validar la referencia.</p>
        </div>
    </div>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

