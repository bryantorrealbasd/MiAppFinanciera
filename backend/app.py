from flask import Flask, render_template_string, request, session, redirect
import os, sqlite3, requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_maestra_trading_quantum_2025'

# --- CONFIGURACIÓN GLOBAL ---
NUMERO_CELULAR = "584165696847"
API_KEY_WHA = "ESCRIBE_AQUI_TU_CODIGO_DE_6_DIGITOS" # Reemplaza esto cuando el bot te responda

def enviar_alerta_whatsapp(mensaje):
    if API_KEY_WHA == "ESCRIBE_AQUI_TU_CODIGO_DE_6_DIGITOS" or API_KEY_WHA == "PENDIENTE":
        print(f"Log: {mensaje} (WhatsApp no configurado)")
        return
    url = f"https://api.callmebot.com/whatsapp.php?phone={NUMERO_CELULAR}&text={mensaje}&apikey={API_KEY_WHA}"
    try: requests.get(url)
    except: print("Error de conexión con WhatsApp")

# --- GESTIÓN DE BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    # Tabla de usuarios con billetera y autoridad de bot
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                      (id INTEGER PRIMARY KEY, email TEXT, saldo REAL, bot_autoridad INTEGER)''')
    # Tabla de depósitos para auditoría legal
    cursor.execute('''CREATE TABLE IF NOT EXISTS depositos 
                      (id INTEGER PRIMARY KEY, usuario TEXT, monto REAL, ref TEXT, estado TEXT, fecha TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user' not in session: return render_template_string(LOGIN_HTML)
    
    conn = sqlite3.connect('datos.db')
    user_data = conn.execute("SELECT saldo, bot_autoridad FROM usuarios WHERE email=?", (session['user'],)).fetchone()
    conn.close()
    
    saldo = user_data[0] if user_data else 0.0
    
    # REGLA DE ORO: El bot necesita $2 para despertar
    bot_activo = saldo >= 2.0
    estado_texto = "SISTEMA ACTIVO" if bot_activo else "BOT APAGADO (Saldo < $2)"
    estado_color = "#3fb950" if bot_activo else "#f85149"
    
    return render_template_string(DASHBOARD_HTML, user=session['user'], saldo=saldo, estado_texto=estado_texto, estado_color=estado_color)

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    session['user'] = email
    conn = sqlite3.connect('datos.db')
    # Si es nuevo, le damos un bono de $5 para que vea el bot activo de una vez
    if not conn.execute("SELECT email FROM usuarios WHERE email=?", (email,)).fetchone():
        conn.execute("INSERT INTO usuarios (email, saldo, bot_autoridad) VALUES (?, 5.0, 1)", (email,))
        conn.commit()
    conn.close()
    return redirect('/')

@app.route('/notificar', methods=['POST'])
def notificar():
    if 'user' not in session: return redirect('/')
    monto = request.form.get('monto')
    ref = request.form.get('ref')
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    conn = sqlite3.connect('datos.db')
    conn.execute("INSERT INTO depositos (usuario, monto, ref, estado, fecha) VALUES (?,?,?,?,?)",
                 (session['user'], monto, ref, 'Pendiente', fecha))
    conn.commit()
    conn.close()
    
    enviar_alerta_whatsapp(f"🚀 *NUEVO DEPÓSITO:* {monto} USDT de {session['user']}. Ref: {ref}")
    return "<h1>Notificación enviada al Asistente Legal.</h1><a href='/'>Volver</a>"

# --- INTERFACES VISUALES (APP MÓVIL) ---
LOGIN_HTML = '''
<body style="background:#010409; color:white; font-family:sans-serif; text-align:center; padding-top:80px;">
    <h1 style="color:#58a6ff;">QUANTUM AI <br><small style="color:gray;">Trading Terminal</small></h1>
    <div style="background:#0d1117; padding:30px; border-radius:20px; border:1px solid #30363d; display:inline-block; width:80%;">
        <form action="/login" method="POST">
            <input name="email" type="email" placeholder="Usuario / Email" required style="width:90%; padding:15px; margin-bottom:15px; background:#010409; color:white; border:1px solid #30363d; border-radius:10px;">
            <button style="width:100%; padding:15px; background:#238636; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">INICIAR ALGORITMO</button>
        </form>
    </div>
</body>'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background:#010409; color:#c9d1d9; font-family:sans-serif; margin:0; padding:15px; }
        .card { background:#0d1117; border:1px solid #30363d; border-radius:15px; padding:20px; margin-bottom:15px; }
        .bot-status { background:{{estado_color}}; color:white; padding:5px 12px; border-radius:20px; font-size:12px; font-weight:bold; }
        input { width:100%; padding:12px; background:#010409; color:white; border:1px solid #30363d; border-radius:8px; margin-bottom:10px; box-sizing:border-box; }
        button { width:100%; padding:12px; background:#238636; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer; }
    </style>
</head>
<body>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
        <b style="color:#58a6ff; font-size:18px;"><i class="fas fa-brain"></i> Quantum AI</b>
        <span class="bot-status">{{estado_texto}}</span>
    </div>

    <div class="card" style="text-align:center;">
        <p style="color:gray; margin:0;">Billetera Disponible</p>
        <h1 style="margin:10px 0; font-size:40px;">${{saldo}} <small style="font-size:16px; color:#3fb950;">USDT</small></h1>
    </div>

    <div class="card">
        <h4 style="margin:0 0 15px 0;"><i class="fas fa-bolt" style="color:#e3b341;"></i> Ejecución Automática</h4>
        <div style="height:150px; background:#010409; border-radius:10px; display:flex; flex-direction:column; align-items:center; justify-content:center; border:1px dashed #30363d;">
             <span style="color:#58a6ff; font-size:14px;">Conectado a Binance Cloud</span>
             <small style="color:gray; margin-top:10px;">Escaneando oportunidades...</small>
        </div>
    </div>

    <div class="card">
        <h4 style="margin:0 0 15px 0;"><i class="fas fa-university"></i> Recargar Fondos</h4>
        <form action="/notificar" method="POST">
            <input name="monto" type="number" placeholder="Monto USDT" required>
            <input name="ref" type="text" placeholder="Referencia de Operación" required>
            <button type="submit">INFORMAR DEPÓSITO</button>
        </form>
        <p style="font-size:10px; color:gray; text-align:center; margin-top:10px;">Toda operación es auditada legalmente.</p>
    </div>
</body>
</html>'''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
