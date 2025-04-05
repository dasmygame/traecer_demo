from flask import Flask, render_template, request, redirect, flash
from flask_cors import CORS
from alpaca_trade_api.rest import REST
from config import API_KEY_A, API_SECRET_A, API_KEY_B, API_SECRET_B

app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'

BASE_URL = "https://paper-api.alpaca.markets"
api_a = REST(API_KEY_A, API_SECRET_A, BASE_URL)
api_b = REST(API_KEY_B, API_SECRET_B, BASE_URL)

@app.route('/', methods=['GET'])
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit_order():
    try:
        symbol = request.form['symbol'].upper()
        expiration = request.form['expiration']
        strike = request.form['strike']
        option_type = request.form['type'].upper()
        side = request.form['side']
        qty = int(request.form['qty'])
        order_type = request.form['order_type']
        tif = request.form['tif']
        limit_price = request.form.get('limit_price', '').strip()

        # Format OCC options symbol: "AAPL  240419C00150000"
        occ = option_type[0]  # 'C' or 'P'
        yymmdd = expiration.replace('-', '')[2:]
        strike_int = int(float(strike) * 100)
        occ_symbol = f"{symbol} {yymmdd}{occ}{strike_int:08d}"

        order = {
            "symbol": occ_symbol,
            "qty": qty,
            "side": side,
            "type": order_type,
            "time_in_force": tif,
        }
        if order_type == 'limit' and limit_price:
            order['limit_price'] = float(limit_price)

        api_a.submit_order(**order)
        api_b.submit_order(**order)

        flash("✅ Order submitted successfully to both accounts!", "success")
    except Exception as e:
        flash(f"❌ Error: {e}", "error")

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)