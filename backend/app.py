import os
import sqlite3
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'datos.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Asegurar tablas profesionales
with get_db_connection() as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, nombre TEXT, saldo REAL, balance_btc REAL)")
    if not conn.execute("SELECT * FROM usuarios WHERE nombre = 'Admin'").fetchone():
        conn.execute("INSERT INTO usuarios (nombre, saldo, balance_btc) VALUES ('Admin', 0.0, 0.0)")
    conn.commit()

@app.route('/')
def home():
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM usuarios WHERE nombre = 'Admin'").fetchone()
    
    # INTERFAZ TIPO TRADINGVIEW / BINANCE PRO
    html_template = f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pro Broker | Trading Platform</title>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <style>
            body {{ background-color: #060606; color: #e1e1e1; font-family: 'Roboto', sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; }}
            header {{ background: #121212; padding: 10px 20px; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }}
            .logo {{ color: #f3ba2f; font-weight: bold; font-size: 1.2rem; }}
            .main-container {{ display: flex; flex: 1; overflow: hidden; }}
            .sidebar {{ width: 300px; background: #121212; border-right: 1px solid #333; padding: 20px; display: flex; flex-direction: column; }}
            #chart-container {{ flex: 1; background: #000; }}
            .balance-card {{ background: #1e1e1e; border-radius: 10px; padding: 15px; margin-bottom: 20px; border-left: 4px solid #f3ba2f; }}
            .balance-card h3 {{ font-size: 0.8rem; color: #848e9c; margin: 0; }}
            .balance-amount {{ font-size: 1.8rem; font-weight: bold; margin: 5px 0; color: #fff; }}
            .trading-buttons {{ display: flex; gap: 10px; }}
            .btn {{ flex: 1; padding: 12px; border-radius: 5px; border: none; font-weight: bold; cursor: pointer; }}
            .btn-buy {{ background: #2ebd85; color: white; }}
            .btn-sell {{ background: #f6465d; color: white; }}
        </style>
    </head>
    <body>
        <header>
            <div class="logo">PRO BROKER ADVANCED</div>
            <div>Admin: <span style="color:#f3ba2f">Online</span></div>
        </header>
        <div class="main-container">
            <div class="sidebar">
                <div class="balance-card">
                    <h3>SALDO TOTAL ESTIMADO</h3>
                    <div class="balance-amount">${user['saldo']:,.2f}</div>
                    <span style="color:#848e9c; font-size:0.8rem">≈ {user['balance_btc']} BTC</span>
                </div>
                <div class="trading-buttons">
                    <button class="btn btn-buy">COMPRAR</button>
                    <button class="btn btn-sell">VENDER</button>
                </div>
                <div style="margin-top:20px; font-size:0.8rem; color:#444;">
                    <a href="/admin_panel" style="color:#444; text-decoration:none;">Acceso Interno</a>
                </div>
            </div>
            <div id="chart-container">
                <div id="tradingview_widget"></div>
            </div>
        </div>
        <script>
            new TradingView.widget({{
                "autosize": true,
                "symbol": "BINANCE:BTCUSDT",
                "interval": "D",
                "timezone": "Etc/UTC",
                "theme": "dark",
                "style": "1",
                "locale": "es",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_widget"
            }});
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template)

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        nuevo_saldo = request.form.get('saldo')
        nuevo_btc = request.form.get('btc')
        with get_db_connection() as conn:
            conn.execute("UPDATE usuarios SET saldo = ?, balance_btc = ? WHERE nombre = 'Admin'", (nuevo_saldo, nuevo_btc))
            conn.commit()
        return redirect('/')
    return '''
    <body style="background:#111; color:#fff; padding:50px; font-family:sans-serif;">
        <h2>ADMIN - AJUSTE DE CUENTAS</h2>
        <form method="POST">
            <p>Saldo USDT: <input type="number" step="0.01" name="saldo" style="padding:10px;"></p>
            <p>Saldo BTC: <input type="number" step="0.00000001" name="btc" style="padding:10px;"></p>
            <button type="submit" style="padding:10px; background:#f3ba2f; border:none; cursor:pointer;">ACTUALIZAR BROKER</button>
        </form>
    </body>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

