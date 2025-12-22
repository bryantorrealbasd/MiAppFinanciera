import os
import sqlite3
from flask import Flask, render_template_string

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'datos.db')

def get_balance():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, nombre TEXT, saldo REAL)")
    cursor.execute("SELECT saldo FROM usuarios WHERE nombre = 'Admin'")
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO usuarios (nombre, saldo) VALUES ('Admin', 0.0)")
        conn.commit()
        saldo = 0.0
    else:
        saldo = row[0]
    conn.close()
    return saldo

@app.route('/')
def home():
    saldo = get_balance()
    # Diseño HTML con estilo profesional (Binance Style)
    html_template = f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mi App Financiera | Dashboard</title>
        <style>
            body {{ font-family: sans-serif; background-color: #0b0e11; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .card {{ background-color: #1e2329; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); width: 300px; }}
            h1 {{ color: #f3ba2f; font-size: 1.5rem; }}
            .balance {{ font-size: 2.5rem; margin: 1rem 0; font-weight: bold; }}
            .currency {{ color: #848e9c; font-size: 1rem; }}
            .btn {{ background-color: #f3ba2f; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Broker Principal</h1>
            <p class="currency">Saldo Disponible (USDT)</p>
            <div class="balance">$ {saldo:.2f}</div>
            <button class="btn">Depositar</button>
            <button class="btn" style="background-color: #2b3139; color: white;">Retirar</button>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

