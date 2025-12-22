import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'datos.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Creamos la tabla de usuarios/saldos por defecto
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                      (id INTEGER PRIMARY KEY, nombre TEXT, saldo REAL)''')
    # Insertamos un usuario de prueba si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (nombre, saldo) VALUES ('Admin', 0.0)")
    conn.commit()
    conn.close()

@app.route('/')
def home():
    try:
        init_db()
        return "<h1>Broker Activo</h1><p>Conexion a base de datos exitosa.</p>"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

