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
    'PERPUSDT': {'leverage':10, 'quantity': 5}, # hotmail - 3MIN
    'BTCUSDT': {'leverage':125, 'quantity': 0.003}, # laudin - 15MIN
    'ETHUSDT': {'leverage':100, 'quantity': 0.0015} # gaston - 5MIN
}

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()

        # positions = client.get_all_orders()
        # print(positions)
        self.send_response(200)


    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        print(content_length)

        rawData = json.loads((self.rfile.read(content_length).decode("utf-8")))
        data = json.loads(rawData["payload"]["body-plain"])
        self._set_headers()
        print(data)
        
        if (data['side'] == 'buy'):
            side = 'BUY'
        if (data['side'] == 'sell'):
            side = 'SELL'

        symbol = data['symbol']

        try:
            client.futures_change_leverage(symbol=symbol, leverage=coins_op[symbol]['leverage'])
        except BinanceAPIException as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.code, error.message
                )
            )

        params = {
            'symbol': symbol,
            'type': 'MARKET',
            'side':  side,
            'quantity': coins_op[symbol]['quantity'], # EQUITY * LEVERAGE
            # 'timestamp': time.time(),
            'recvWindow': 10000
        }

            
        params2 = {
            'symbol': symbol,
            'type': 'MARKET',
            'side':  side,
            'quantity': coins_op['PERPUSDT']['quantity'], # EQUITY * LEVERAGE
            # 'timestamp': time.time(),
            'recvWindow': 10000
        }
        try:
            order = client.futures_create_order(**params)
            print(order)

            ## Checks for existing positions
            # positions = client.futures_account()['positions']
            # positionAmt = float(next((item for item in positions if item.get('symbol') == symbol), None)['positionAmt'])
            
            # if (positionAmt == 0): return

            # order2 = client.futures_create_order(**params2)
            # print(order2)
            
            # global start
            # if (not start): 

            # start = False
        except BinanceAPIException as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.code, error.message
                )
            )

        self.send_response(200)

def run(server_class=HTTPServer, handler_class=S, port=3000):
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
