from flask import Flask, render_template_string, request, session, redirect, url_for
import os, sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'quantum_pro_broker_2025'

TASAS = {'VES': 62.50, 'COP': 4100.0, 'ARS': 1050.0, 'BRL': 5.20}

def init_db():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    # Ahora guardamos saldo_real y saldo_demo por separado
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, email TEXT, saldo_real REAL, saldo_demo REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS depositos (id INTEGER PRIMARY KEY, usuario TEXT, monto REAL, moneda TEXT, usdt_equiv REAL, ref TEXT, estado TEXT, fecha TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user' not in session: return render_template_string(LOGIN_HTML)
    if 'mode' not in session: session['mode'] = 'DEMO' # Por defecto inicia en Demo
    
    conn = sqlite3.connect('datos.db')
    res = conn.execute("SELECT saldo_real, saldo_demo FROM usuarios WHERE email=?", (session['user'],)).fetchone()
    conn.close()
    
    saldo = res[1] if session['mode'] == 'DEMO' else res[0]
    return render_template_string(DASHBOARD_HTML, user=session['user'], saldo=saldo, mode=session['mode'], tasas=TASAS)

@app.route('/switch_mode')
def switch_mode():
    session['mode'] = 'REAL' if session.get('mode') == 'DEMO' else 'DEMO'
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    session['user'] = request.form['email']
    conn = sqlite3.connect('datos.db')
    if not conn.execute("SELECT email FROM usuarios WHERE email=?", (session['user'],)).fetchone():
        # Al crear usuario damos 10,000 en Demo y 0 en Real
        conn.execute("INSERT INTO usuarios (email, saldo_real, saldo_demo) VALUES (?, 0.0, 10000.0)", (session['user'],))
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
    return "<h1>Solicitud enviada.</h1><a href='/'>Volver</a>"

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
        conn.execute("UPDATE usuarios SET saldo_real = saldo_real + ? WHERE email=?", (dep[1], dep[0]))
        conn.execute("UPDATE depositos SET estado='Aprobado' WHERE id=?", (id,))
        conn.commit()
    conn.close()
    return redirect(url_for('admin'))

# --- INTERFACES ---
LOGIN_HTML = '''<body style="background:#010409;color:white;text-align:center;padding:50px;font-family:sans-serif;"><h2>QUANTUM PRO LOGIN</h2><form action="/login" method="POST"><input name="email" type="email" placeholder="Email" style="width:80%;padding:10px;"><br><button style="width:80%;padding:10px;background:#238636;color:white;border:none;margin-top:10px;">ENTRAR</button></form></body>'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { background:#010409; color:#c9d1d9; font-family:sans-serif; margin:0; overflow-x:hidden; }
        .header { display:flex; justify-content:space-between; align-items:center; padding:10px; background:#161b22; border-bottom:1px solid #30363d; }
        .mode-btn { padding:8px 15px; border-radius:20px; border:none; font-weight:bold; cursor:pointer; color:white; background: {{ '#f2994a' if mode == 'DEMO' else '#238636' }}; }
        .chart-box { width: 100%; height: 280px; background: #000; }
        .content { padding: 15px; }
        .card { background:#161b22; border:1px solid #30363d; padding:15px; border-radius:10px; margin-bottom:15px; }
        .saldo-txt { color: {{ '#f2994a' if mode == 'DEMO' else '#3fb950' }}; margin:5px 0; }
        input, select { width:100%; padding:12px; margin:8px 0; background:#010409; color:white; border:1px solid #30363d; border-radius:5px; box-sizing: border-box; }
        .btn-pay { width:100%; padding:15px; background:#238636; color:white; border:none; font-weight:bold; border-radius:5px; }
    </style>
</head>
<body>
    <div class="header">
        <b>QUANTUM AI</b>
        <a href="/switch_mode"><button class="mode-btn">CUENTA {{ mode }}</button></a>
    </div>
    <div class="chart-box">
        <iframe src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:BTCUSDT&theme=dark" style="width:100%; height:100%; border:none;"></iframe>
    </div>
    <div class="content">
        <div class="card">
            <small>SALDO {{ mode }} DISPONIBLE</small>
            <h2 class="saldo-txt">${{ "{:,.2f}".format(saldo) }} USDT</h2>
        </div>
        {% if mode == 'REAL' %}
        <div class="card">
            <h4>RECARGAR CUENTA REAL</h4>
            <form action="/notificar" method="POST">
                <select id="moneda" name="moneda" onchange="calc()">
                    <option value="VES">Bolívares (VES)</option>
                    <option value="COP">Pesos (COP)</option>
                    <option value="ARS">Pesos (ARS)</option>
                </select>
                <input id="monto" name="monto" type="number" placeholder="Monto Local" oninput="calc()" required>
                <div style="color:#3fb950; margin-bottom:10px;">Recibirás: <span id="res">0.00</span> USDT</div>
                <input name="ref" type="text" placeholder="Referencia Bancaria" required>
                <button type="submit" class="btn-pay">INFORMAR PAGO</button>
            </form>
        </div>
        {% else %}
        <div class="card" style="text-align:center; border-color:#f2994a;">
            <p>Estás operando con dinero virtual.</p>
            <p style="font-size:12px; color:gray;">Cambia a cuenta REAL para retirar ganancias.</p>
        </div>
        {% endif %}
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

ADMIN_HTML = '''<body style="background:#010409; color:white; font-family:sans-serif; padding:10px;"><h3>Aprobar Pagos Reales</h3>{% for d in depositos %}<div style="background:#161b22; padding:10px; margin-bottom:10px; border:1px solid #30363d;">Usuario: {{d[1]}}<br>Monto: {{d[4]}} USDT<br>Ref: {{d[5]}}<br><a href="/aprobar/{{d[0]}}" style="color:#3fb950;">[APROBAR PAGO]</a></div>{% endfor %}<br><a href="/" style="color:gray;">Volver</a></body>'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

