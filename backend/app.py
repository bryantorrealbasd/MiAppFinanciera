from flask import Flask, request, jsonify
import json
app = Flask(__name__)

with open('config/fees.json') as f:
    fees = json.load(f)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    amount = data.get('amount', 0)
    converted = amount * 27000
    return jsonify({'converted': converted})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)