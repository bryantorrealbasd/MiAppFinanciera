import requests # Asegúrate de tenerlo instalado con: pip install requests
from flask import Flask, render_template_string, request, session, redirect
import os, sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_maestra_trading_pro_2025'

# --- CONFIGURACIÓN DE TU WHATSAPP ---
NUMERO_CELULAR = "TU_NUMERO_CON_CODIGO_PAIS" # Ejemplo: 584120000000
API_KEY_WHA = "TU_API_KEY"

def enviar_alerta_pago(usuario, monto, ref):
    mensaje = f"🚀 *Trading Pro: NUEVO PAGO*\n\n👤 Usuario: {usuario}\n💰 Monto: {monto} USDT\n🔢 Ref: {ref}\n\n⚠️ Verifique su banco antes de aprobar."
    url = f"https://api.callmebot.com/whatsapp.php?phone={NUMERO_CELULAR}&text={mensaje}&apikey={API_KEY_WHA}"
    try:
        requests.get(url)
    except:
        print("Error enviando WhatsApp")

# --- (El resto del código se mantiene igual, pero añadimos la llamada en /notificar) ---

@app.route('/notificar', methods=['POST'])
def notificar():
    if 'user' not in session: return redirect('/')
    monto = request.form.get('monto')
    ref = request.form.get('ref')
    user = session['user']
    
    # ENVIAR ALERTA A TU CELULAR
    enviar_alerta_pago(user, monto, ref)
    
    # GUARDAR EN BASE DE DATOS
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO depositos (usuario, monto, ref, estado, fecha, auditoria) VALUES (?,?,?,?,?,?)",
                   (user, monto, ref, 'Pendiente', datetime.now().strftime("%Y-%m-%d %H:%M"), "AUDITORÍA OK"))
    conn.commit()
    conn.close()
    return "<h1>Notificación enviada. Revisaremos su pago.</h1><a href='/'>Volver</a>"

# ... (Mantén las variables LOGIN_HTML y DASHBOARD_HTML que ya teníamos) ...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

