from flask import Flask, render_template_string, request, session, redirect
import os, sqlite3, requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_maestra_quantum_global_2025'

# --- CONFIGURACIÓN DE TASAS (Puedes cambiarlas según el día) ---
TASAS = {
    'VES': 62.50,  # 1 USDT = 62.50 Bolívares
    'COP': 4100.0, # 1 USDT = 4100 Pesos Colombianos
    'ARS': 1050.0, # 1 USDT = 1050 Pesos Argentinos
    'BRL': 5.20    # 1 USDT = 5.20 Reales
}

def init_db():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, email TEXT, saldo REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS depositos (id INTEGER PRIMARY KEY, usuario TEXT, monto REAL, moneda TEXT, usdt_equiv REAL, ref TEXT, fecha TEXT)''')
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
    return render_template_string(DASHBOARD_HTML, user=session['user'], saldo=saldo, tasas=TASAS)

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
    monto = float(request.form.get('monto'))
    moneda = request.form.get('moneda')
    ref = request.form.get('ref')
    tasa = TASAS.get(moneda, 1.0)
    usdt_equiv = round(monto / tasa, 2)
    
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect('datos.db')
    conn.execute("INSERT INTO depositos (usuario, monto, moneda, usdt_equiv, ref, fecha) VALUES (?,?,?,?,?,?)",
                 (session['user'], monto, moneda, usdt_equiv, ref, fecha))
    conn.commit()
    conn.close()
    return f"<h1>Solicitud enviada por {usdt_equiv} USDT.</h1><a href='/'>Volver</a>"

# --- INTERFAZ GLOBAL CON CONVERSOR ---
LOGIN_HTML = '''<body style="background:#010409;color:white;text-align:center;padding-top:100px;"><h1>QUANTUM GLOBAL</h1><form action="/login" method="POST"><input name="email" type="email" placeholder="Email" required><button>ENTRAR</button></form></body>'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background:#010409; color:#c9d1d9; font-family:sans-serif; margin:0; }
        .grid { display:grid; grid-template-columns: 1fr 350px; height:100vh; }
        .sidebar { background:#0d1117; padding:20px; border-left:1px solid #30363d; }
        .card { background:#161b22; border:1px solid #30363d; padding:15px; border-radius:10px; margin-bottom:15px; }
        .usdt-calc { color:#3fb950; font-weight:bold; font-size:18px; margin-top:10px; }
        input, select { width:100%; padding:10px; margin:10px 0; background:#010409; color:white; border:1px solid #30363d; }
        button { width:100%; padding:15px; background:#238636; color:white; border:none; font-weight:bold; cursor:pointer; }
    </style>
</head>
<body>
    <div class="grid">
        <div style="background:#000;">
            <iframe src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:BTCUSDT&theme=dark" style="width:100%; height:100%; border:none;"></iframe>
        </div>
        <div class="sidebar">
            <div class="card">
                <small>BILLETERA</small>
                <h2>${{saldo}} USDT</h2>
            </div>
            <div class="card">
                <h4>PASARELA DE PAGO</h4>
                <form action="/notificar" method="POST">
                    <select id="moneda" name="moneda" onchange="calcular()">
                        <option value="VES">Bolívares (VES)</option>
                        <option value="COP">Pesos (COP)</option>
                        <option value="ARS">Pesos (ARS)</option>
                        <option value="BRL">Reales (BRL)</option>
                    </select>
                    <input id="monto" name="monto" type="number" placeholder="Monto Local" oninput="calcular()" required>
                    <div class="usdt-calc">Recibirás: <span id="resultado">0.00</span> USDT</div>
                    <input name="ref" type="text" placeholder="Referencia" required>
                    <button type="submit">INFORMAR DEPÓSITO</button>
                </form>
            </div>
        </div>
    </div>
    <script>
        const tasas = {{ tasas|tojson }};
        function calcular() {
            const m = document.getElementById('monto').value;
            const mon = document.getElementById('moneda').value;
            const res = m / tasas[mon];
            document.getElementById('resultado').innerText = res.toFixed(2);
        }
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

