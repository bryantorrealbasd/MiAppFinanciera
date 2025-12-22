from flask import Flask, render_template_string, request, session, redirect, url_for
import os, sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'admin_quantum_secret_2025'

# --- CONFIGURACIÓN DE TASAS ---
TASAS = {'VES': 62.50, 'COP': 4100.0, 'ARS': 1050.0, 'BRL': 5.20}

def init_db():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, email TEXT, saldo REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS depositos (id INTEGER PRIMARY KEY, usuario TEXT, monto REAL, moneda TEXT, usdt_equiv REAL, ref TEXT, estado TEXT, fecha TEXT)''')
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
        conn.execute("INSERT INTO usuarios (email, saldo) VALUES (?, 0.0)", (session['user'],))
        conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/notificar', methods=['POST'])
def notificar():
    monto = float(request.form.get('monto'))
    moneda = request.form.get('moneda')
    ref = request.form.get('ref')
    usdt = round(monto / TASAS.get(moneda, 1.0), 2)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    conn = sqlite3.connect('datos.db')
    conn.execute("INSERT INTO depositos (usuario, monto, moneda, usdt_equiv, ref, estado, fecha) VALUES (?,?,?,?,?,?,?)",
                 (session['user'], monto, moneda, usdt, ref, 'Pendiente', fecha))
    conn.commit()
    conn.close()
    return "<h1>Solicitud en revisión. El bot validará su pago.</h1><a href='/'>Volver</a>"

# --- SECCIÓN DE ADMINISTRADOR ---
@app.route('/admin')
def admin():
    conn = sqlite3.connect('datos.db')
    depositos = conn.execute("SELECT * FROM depositos WHERE estado='Pendiente'").fetchall()
    conn.close()
    return render_template_string(ADMIN_HTML, depositos=depositos)

@app.route('/aprobar/<int:id>')
def aprobar(id):
    conn = sqlite3.connect('datos.db')
    dep = conn.execute("SELECT usuario, usdt_equiv FROM depositos WHERE id=?", (id,)).fetchone()
    if dep:
        conn.execute("UPDATE usuarios SET saldo = saldo + ? WHERE email=?", (dep[1], dep[0]))
        conn.execute("UPDATE depositos SET estado='Aprobado' WHERE id=?", (id,))
        conn.commit()
    conn.close()
    return redirect(url_for('admin'))

# --- INTERFACES ---
LOGIN_HTML = '''<body style="background:#010409;color:white;text-align:center;padding-top:100px;"><h1>QUANTUM LOGIN</h1><form action="/login" method="POST"><input name="email" type="email" placeholder="Email"><button>ENTRAR</button></form></body>'''

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
            <div class="card"><h3>Saldo: ${{saldo}} USDT</h3></div>
            <div class="card">
                <h4>DEPÓSITO GLOBAL</h4>
                <form action="/notificar" method="POST">
                    <select id="moneda" name="moneda" onchange="calc()">
                        <option value="VES">Bolívares (VES)</option>
                        <option value="COP">Pesos (COP)</option>
                        <option value="ARS">Pesos (ARS)</option>
                    </select>
                    <input id="monto" name="monto" type="number" placeholder="Monto Local" oninput="calc()" required>
                    <div style="color:#3fb950">Recibirás: <span id="res">0.00</span> USDT</div>
                    <input name="ref" type="text" placeholder="Referencia Bancaria" required>
                    <button type="submit">INFORMAR PAGO</button>
                </form>
            </div>
        </div>
    </div>
    <script>
        const t = {{ tasas|tojson }};
        function calc() {
            const m = document.getElementById('monto').value;
            const mon = document.getElementById('moneda').value;
            document.getElementById('res').innerText = (m / t[mon]).toFixed(2);
        }
    </script>
</body>
</html>'''

ADMIN_HTML = '''
<body style="background:#010409; color:white; font-family:sans-serif; padding:20px;">
    <h2>Panel de Control - Pagos Pendientes</h2>
    <table border="1" style="width:100%; border-collapse:collapse; background:#0d1117;">
        <tr>
            <th>Usuario</th><th>Monto Original</th><th>USDT a Cargar</th><th>Referencia</th><th>Acción</th>
        </tr>
        {% for d in depositos %}
        <tr>
            <td>{{d[1]}}</td><td>{{d[2]}} {{d[3]}}</td><td>{{d[4]}} USDT</td><td>{{d[5]}}</td>
            <td><a href="/aprobar/{{d[0]}}" style="color:#3fb950; font-weight:bold;">APROBAR Y CARGAR</a></td>
        </tr>
        {% endfor %}
    </table>
    <br><a href="/" style="color:gray;">Volver a la Terminal</a>
</body>'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

