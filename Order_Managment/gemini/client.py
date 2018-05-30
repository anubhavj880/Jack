from __future__ import absolute_import
import requests
import json
import base64
import hmac
import hashlib
import time
from decimal import Decimal

PROTOCOL = "https"
HOST = "api.gemini.com"
VERSION = "v1"


class TradeClient():
    """
    Authenticated client for trading through Gemini API
    """

    def __init__(self,acct):
        self.URL = "{0:s}://{1:s}/{2:s}".format(PROTOCOL, HOST, VERSION)
        self.KEY = acct.key
        self.SECRET = acct.secret

    def get_nonce(self):
        """
        Returns a nonce
        Used in authentication
        """
        nonce = getattr(self, 'nonce', 0)
        if nonce:
            nonce += 1
        self.nonce = max(long(float('%.9f' % time.time())*1000000000) , nonce)
        return str(self.nonce)

    def _sign_payload(self, payload):
        encoded_payload = json.dumps(payload)
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(self.SECRET, b64, hashlib.sha384).hexdigest()

        request_headers = {
            'Content-Type': "text/plain",
            'Content-Length': "0",
            'X-GEMINI-APIKEY': self.KEY,
            'X-GEMINI-PAYLOAD': b64,
            'X-GEMINI-SIGNATURE': signature,
            'Cache-Control': "no-cache"
        }

        return request_headers

    def get_balance(self, symbol):
        '''
        currency	required	Currency name (ex: BTC)
        '''
        payload = {"request": "/v1/balances", "nonce": self.get_nonce()}

        try:
            response = requests.post(self.URL+"/balances", data=None, headers=self._sign_payload(payload), timeout=10, verify=False)
            js =json.loads(response.content)
            if symbol== 'BTC':
                return (js[0]['currency'],js[0]['amount'])
            if symbol== 'USD':
                return (js[1]['currency'],js[1]['amount'])
            if symbol == 'ETH':
                return (js[2]['currency'], js[2]['amount'])

        except Exception as err:
            return {"success" : False,"funcName": str('get_balance'), "error": err.message}



    def get_all_balances(self):

        payload = {"request": "/v1/balances", "nonce": self.get_nonce()}

        try:
            response = requests.post(self.URL + "/balances", data=None, headers=self._sign_payload(payload), timeout=10,
                                     verify=False)
            js = json.loads(response.content)
            return js


        except Exception as err:
            return {"success": False, "funcName": str('get_all_balances'), "error": err.message}

    def place_order(self, market, quantity, rate, side):
        '''
        market	    required	Market name (ex: ethusd)
        quantity    required	Amount to purchase
        rate	    required	Rate at which to place the order
        side        required    order side as buy  or sell
        '''
        if type(quantity) != type(Decimal('0.01')):
            quantity = str(Decimal(str(quantity)))
        if type(rate) != type(Decimal('0.01')):
            rate = str(Decimal(str(rate)))

        payload = {"request": "/v1/order/new", "nonce": self.get_nonce(), "client_order_id": "Jack_ORDER", "symbol" : market,
                       "amount": quantity, "price": rate, "side": side, "type": "exchange limit"}


        try:
            response = requests.post(self.URL + "/order/new", data=None, headers=self._sign_payload(payload), timeout=10,
                                     verify=False)
            js = json.loads(response.content)
            return js


        except Exception as err:
            return {"success": False, "funcName": str('place_order'), "error": err.message}

    def cancel_order(self, uuid):
        '''
        uuid	required	uuid of buy or sell order
        '''
        payload = {"request": "/v1/order/cancel", "nonce": self.get_nonce(), "order_id": uuid}

        try:
            response = requests.post(self.URL + "/order/cancel", data=None, headers=self._sign_payload(payload), timeout=10,
                                     verify=False)
            js = json.loads(response.content)
            return js


        except Exception as err:
            return {"success": False, "funcName": str('cancel_order'), "error": err.message}

    def get_orderStatus(self,uuid):
        '''
        uuid	required	uuid of the buy or sell order
        '''
        payload = {"request": "/v1/order/status", "nonce": self.get_nonce(), "order_id": uuid}

        try:
            response = requests.post(self.URL + "/order/status", data=None, headers=self._sign_payload(payload), timeout=10,
                                     verify=False)
            js = json.loads(response.content)
            return js

        except Exception as err:
            return {"success": False, "funcName": str('get_orderStatus'), "error": err.message}



    def get_openorders(self):

        payload = {"request": "/v1/orders", "nonce": self.get_nonce()}

        try:
            response = requests.post(self.URL + "/orders", data=None, headers=self._sign_payload(payload), timeout=10,
                                     verify=False)
            js = json.loads(response.content)
            return js


        except Exception as err:
            return {"success": False, "funcName": str('get_openorders'), "error": err.message}

    def get_tradehistory(self, marketid, limit=None):

        if type(limit) == type(None):
            payload = {"request": "/v1/mytrades", "nonce": self.get_nonce(), "symbol": marketid}

        payload = {"request": "/v1/mytrades", "nonce": self.get_nonce(), "symbol": marketid, "limit_trades": limit}

        try:
            response = requests.post(self.URL + "/mytrades", data=None, headers=self._sign_payload(payload), timeout=10,
                                     verify=False)
            js = json.loads(response.content)
            return js


        except Exception as err:
            return {"success": False, "funcName": str('get_tradehistory'), "error": err.message}


    def get_ticker(self,symbol):

        try:
            response = requests.get(self.URL + "/pubticker/"+symbol, data=None, timeout=10, verify=False)
            js = json.loads(response.content)
            return js

        except Exception as err:
            return {"success": False, "funcName": str('get_ticker'), "error": err.message}






