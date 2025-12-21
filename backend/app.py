from flask import Flask, render_template_string, request, session, redirect
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_maestra_trading_pro_2025'

# --- INICIALIZACIÓN DE BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS depositos 
                      (id INTEGER PRIMARY KEY, usuario TEXT, monto REAL, ref TEXT, 
                       estado TEXT, fecha TEXT, auditoria TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- LÓGICA DE LOS BOTS ---
def bot_quantum_trading():
    import random
    analisis = ["PATRÓN DE VELAS ALCISTA", "ZONA DE SOPORTE DETECTADA", "RUPTURA DE RESISTENCIA", "CORRECCIÓN EN CURSO"]
    senales = ["COMPRAR", "VENDER", "ESPERAR"]
    return f"{random.choice(analisis)} -> ACCIÓN: {random.choice(senales)}"

# --- INTERFAZ ÚNICA ---
@app.route('/')
def index():
    if 'user' not in session:
        return render_template_string(LOGIN_HTML)
    
    senal_quantum = bot_quantum_trading()
    return render_template_string(DASHBOARD_HTML, user=session['user'], senal=senal_quantum)

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
    # Aquí actúa el ASISTENTE LEGAL (Auditoría)
    ref = request.form['ref']
    monto = request.form['monto']
    veredicto = "REVISIÓN EXITOSA" if len(ref) > 5 else "ALERTA: REF. SOSPECHOSA"
    
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO depositos (usuario, monto, ref, estado, fecha, auditoria) VALUES (?,?,?,?,?,?)",
                   (session['user'], monto, ref, 'Pendiente', datetime.now().strftime("%Y-%m-%d %H:%P"), veredicto))
    conn.commit()
    conn.close()
    return f"<h1>Asistente Legal: Transacción registrada. Veredicto: {veredicto}</h1><a href='/'>Volver</a>"

# --- DISEÑO VISUAL (HTML/CSS) ---
LOGIN_HTML = '''
<body style="background:#010409; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
    <div style="background:#0d1117; padding:40px; border-radius:15px; border:1px solid #30363d; text-align:center; width:300px;">
        <h2 style="color:#58a6ff;">Trading Pro</h2>
        <form action="/login" method="POST">
            <input name="email" type="email" placeholder="Correo" required style="width:100%; padding:10px; margin:10px 0; background:#010409; border:1px solid #30363d; color:white; border-radius:5px;">
            <input type="password" placeholder="Contraseña" required style="width:100%; padding:10px; margin:10px 0; background:#010409; border:1px solid #30363d; color:white; border-radius:5px;">
            <p style="font-size:10px; color:#8b949e;"><input type="checkbox" required> Acepto Términos Legales y Riesgos</p>
            <button style="width:100%; padding:10px; background:#238636; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">ACCEDER</button>
        </form>
    </div>
</body>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Trading Pro | Terminal</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background:#010409; color:#c9d1d9; font-family:sans-serif; margin:0; display:grid; grid-template-rows: 50px 1fr; height:100vh; }
        .nav { background:#161b22; border-bottom:1px solid #30363d; display:flex; justify-content:space-between; align-items:center; padding:0 20px; }
        .main { display:grid; grid-template-columns: 250px 1fr 300px; gap:10px; padding:10px; }
        .panel { background:#0d1117; border:1px solid #30363d; border-radius:8px; padding:15px; overflow-y:auto; }
        .bot-trading { border: 1px solid #58a6ff; background: rgba(88,166,255,0.05); padding:10px; border-radius:8px; margin-bottom:15px; }
        .bot-legal { border: 1px solid #f85149; background: rgba(248,81,73,0.05); padding:10px; border-radius:8px; font-size:12px; }
        .btn { width:100%; padding:10px; border:none; border-radius:5px; cursor:pointer; font-weight:bold; margin-top:5px; color:white; }
    </style>
</head>
<body>
    <div class="nav">
        <strong><i class="fas fa-chart-line"></i> TRADING PRO TERMINAL</strong>
        <span><i class="fas fa-user"></i> {{ user }} | <a href="/logout" style="color:#f85149;">Salir</a></span>
    </div>
    <div class="main">
        <div class="panel">
            <h4><i class="fas fa-globe"></i> Mercados</h4>
            <div style="font-size:13px;">
                <p style="color:#58a6ff;">BTC/USDT: $98,210</p>
                <p>EUR/USD: 1.0845</p>
                <p>VES/USD: 62.50</p>
                <p>Bolsa (NASDAQ): 18,230</p>
            </div>
            <hr style="border:0.5px solid #30363d;">
            <div class="bot-trading">
                <small style="color:#58a6ff;"><strong><i class="fas fa-robot"></i> Algoritmo Quantum:</strong></small>
                <p style="font-size:12px; margin:5px 0;">{{ senal }}</p>
            </div>
        </div>

        <div class="panel" style="background:#010409; display:flex; flex-direction:column; justify-content:center; align-items:center;">
            <i class="fas fa-wave-square fa-3x" style="color:#30363d;"></i>
            <p style="color:#30363d;">Gráfico de Velas Japonesas en Vivo</p>
            <div style="width:100%; background:var(--green); height:2px; margin-top:10px; box-shadow:0 0 10px #3fb950;"></div>
        </div>

        <div class="panel">
            <h4><i class="fas fa-wallet"></i> Billetera P2P</h4>
            <div style="background:#161b22; padding:10px; border-radius:5px; margin-bottom:15px;">
                <small>Saldo Disponible</small>
                <div style="font-size:24px; color:#3fb950; font-weight:bold;">$1,250.00 <small style="font-size:12px;">USDT</small></div>
            </div>
            
            <form action="/notificar" method="POST">
                <select name="moneda" style="width:100%; padding:8px; margin-bottom:5px; background:#010409; color:white; border:1px solid #30363d;">
                    <option>Bolívares (VES)</option>
                    <option>Pesos (COP)</option>
                    <option>Pesos (ARS)</option>
                </select>
                <input name="monto" type="number" placeholder="Monto enviado" style="width:100%; padding:8px; margin-bottom:5px; background:#010409; color:white; border:1px solid #30363d;">
                <input name="ref" type="text" placeholder="Nro Referencia" style="width:100%; padding:8px; margin-bottom:10px; background:#010409; color:white; border:1px solid #30363d;">
                <button class="btn" style="background:#238636;">INFORMAR DEPÓSITO</button>
            </form>

            <div class="bot-legal" style="margin-top:20px;">
                <strong><i class="fas fa-user-shield"></i> Asistente Legal:</strong><br>
                "Verificando integridad de red P2P. Recuerde que el 3% de comisión se aplica al confirmar."
            </div>
        </div>
    </div>
</body>
</html>
'''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

