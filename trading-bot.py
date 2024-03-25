from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException

api_key="7mKs2i0osnp0LcXxGvh6UNxBLpEzVeFpKhjdcbogte4A8MSjwINKsMP3Ea8ZNZsQ"
api_secret="92tfpqq7qV6IuXK3c0yL05Yo8059brllLcqE3lLiByxTSACirebnlJsaZM5LyQW1"

client = Client(api_key, api_secret)

from http.server import BaseHTTPRequestHandler, HTTPServer

# import ngrok python sdk
# import ngrok

# Establish connectivity
# listener = ngrok.forward(8000, authtoken="2YAdfhBhwZ9MIyyC5K2PK6Ze8Cg_5RPwNY851oq6RzRCwMGcz")

# start = True
start = False

# Output ngrok url to console
# print(f"Ingress established at {listener.url()}")

coins_op = {
    'BTCUSDT': {'leverage':125, 'quantity': 0.003},
    'ETHUSDT': {'leverage':100, 'quantity': 0.015},
    'BNBUSDT': {'leverage':60, 'quantity': 0.02},
    'DOGEUSDT': {'leverage':60, 'quantity': 45},
    'SOLUSDT': {'leverage':80, 'quantity': 1},
    'MATICUSDT': {'leverage':60, 'quantity': 10},
    'XRPUSDT': {'leverage':60, 'quantity': 15},
    'ADAUSDT': {'leverage':60, 'quantity': 15},
    'FILUSDT': {'leverage':60, 'quantity': 1},
    'CAKEUSDT': {'leverage':20, 'quantity': 3},
    'DOTUSDT': {'leverage':60, 'quantity': 1},
    'NEARUSDT': {'leverage':50, 'quantity': 3},
    'AAVEUSDT': {'leverage':45, 'quantity': 0.3},
    'MINAUSDT': {'leverage':45, 'quantity': 6},
    'FTMUSDT': {'leverage':45, 'quantity': 17},
    'SANDUSDT': {'leverage':45, 'quantity': 15},
    'IMXUSDT': {'leverage':45, 'quantity': 4},
    'ICPUSDT': {'leverage':25, 'quantity': 3},
    'PERPUSDT': {'leverage':10, 'quantity': 5},
    'STXUSDT': {'leverage':20, 'quantity': 4},
    'RNDRUSDT': {'leverage':20, 'quantity': 1},
}

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.send_response(200)

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        rawData = json.loads((self.rfile.read(content_length).decode("utf-8")))
        data = json.loads(rawData["payload"]["body-plain"])
        self._set_headers()
        print(data)
        
        entry_position(data)

        self.send_response(200)


def entry_position(data):
    if (data['side'] == 'buy'):
            side = 'BUY'
    if (data['side'] == 'sell'):
        side = 'SELL'

    symbol = data['symbol']
    params = {
        'symbol': symbol,
        'type': 'MARKET',
        'side':  side,
        'quantity': coins_op[symbol]['quantity'], # EQUITY * LEVERAGE
        # 'timestamp': time.time(),
        'recvWindow': 10000
    }

    if 'exit' in data['id']:
        try:
            # Checks for existing positions
            positions = client.futures_account()['positions']
            positionAmt = float(next((item for item in positions if item.get('symbol') == symbol), None)['positionAmt'])
            
            if (positionAmt == 0): return

            order = client.futures_create_order(**params)
            print(order)
        except BinanceAPIException as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.code, error.message
                )
            )
    else:
        try:
            client.futures_change_leverage(symbol=symbol, leverage=coins_op[symbol]['leverage'])
            client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')
            order = client.futures_create_order(**params)
            print(order)

        except BinanceAPIException as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.code, error.message
                )
            )

def run(server_class=HTTPServer, handler_class=Handler, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
