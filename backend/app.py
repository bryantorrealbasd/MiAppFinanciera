from flask import 
Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trading Pro - Bot & Billetera</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body { background-color: #0d1117; color: #c9d1d9; font-family: sans-serif; text-align: center; padding: 20px; }
            .card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
            .up { color: #3fb950; } .down { color: #f85149; } .wallet { color: #d29922; }
            .btn-bot { background-color: #238636; color: white; border: none; padding: 15px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; }
            input { width: 85%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #30363d; background: #0d1117; color: white; text-align: center; }
        </style>
    </head>
    <body>
        <h1><i class="fas fa-chart-line"></i> MiApp Financiera</h1>
        <div style="font-size: 40px; margin: 20px 0;">
            <i class="fas fa-chart-bar up"></i>
            <i class="fas fa-wallet wallet"></i>
            <i class="fas fa-chart-area down"></i>
        </div>
        <div class="card">
            <h3><i class="fas fa-robot"></i> Bot de Trading Automático</h3>
            <p>Estrategia: <strong>70% Éxito / 30% Riesgo</strong></p>
            <button class="btn-bot" onclick="alert('Conectando con señales del mercado...')">ACTIVAR BOT</button>
        </div>
        <div class="card">
            <h3><i class="fas fa-calculator"></i> Calculadora de Comisión</h3>
            <input type="number" id="monto" placeholder="Ingresa monto $" oninput="calc()">
            <p id="res" style="color: #58a6ff;">Comisión (3%): $0.00</p>
        </div>
        <script>
            function calc() {
                let v = document.getElementById('monto').value;
                document.getElementById('res').innerHTML = "Comisión (3%): $" + (v * 0.03).toFixed(2);
            }
        </script>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)



