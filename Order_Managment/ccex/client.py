from __future__ import absolute_import
import requests
import json
import base64
import hmac
import hashlib
import time
import urllib
from decimal import Decimal

PROTOCOL = "https"
HOST = "c-cex.com"
VERSION = "t"

PATH_PUBLIC = "api_pub.html"
PATH_PRIVATE = "api.html?"
PATH_COINNAMES = "coinnames.json"
PATH_PAIRS = "pairs.json"
PATH_PRICES = "prices.json"

# HTTP request timeout in seconds
TIMEOUT = 50.0

class Client:
    """
    Client for the c-cex.com API.
    See https://c-cex.com/?id=api for API documentation.
    """

    def server(self):
        return u"{0:s}://{1:s}/{2:s}".format(PROTOCOL, HOST, VERSION)


    def url_for(self, path, path_arg=None, parameters=None):

        # build the basic url
        url = "%s/%s" % (self.server(), path)

        # If there is a path_arh, interpolate it into the URL.
        # In this case the path that was provided will need to have string
        # interpolation characters in it, such as PATH_TICKER
        if path_arg:
            url = url % (path_arg)

        # Append any parameters to the URL.
        if parameters:
            url = "%s?%s" % (url, self._build_parameters(parameters))
        #print(url)
        return url
    '''
    Online market data for given trading pair.
    '''
    def market_data_pair(self, pair):
        """
        GET /dash-btc.json
        curl https://c-cex.com/t/dash-btc.json
        {
            "ticker": {
            "high": 0.016,
            "low": 0.01560006,
            "avg": 0.01580003,
            "lastbuy": 0.01560009,
            "lastsell": 0.016,
            "buy": 0.01560012,
            "sell": 0.016999,
            "lastprice": 0.01560009,
            "buysupport": 35.84405079,
            "updated": 1459411200
            }
        }
        """
        return self._get(self.url_for((pair+".json")).lower())

    def coinnames(self):
        """
        GET /coinnames.json
        curl https://c-cex.com/t/coinnames.json
        {
            "usd": "USD",
            "btc": "Bitcoin",
            "1337": "1337",
            ...
            "zny": "BitZeny"
        }
        """
        return self._get(self.url_for(PATH_COINNAMES))

    
    '''
    List of available trading pairs.
    '''
    def pairs(self):
        """
        GET /pairs.json
        curl https://c-cex.com/t/pairs.json
        {
            "pairs": ["usd-btc", "1337-btc", ... "zny-doge"]
        }
        """
        return self._get(self.url_for(PATH_PAIRS))

    '''
    All online trading pairs market data
    '''
    def prices(self):
        """
        GET /prices.json
        curl https://c-cex.com/t/prices.json

        "1337-btc": {
        "high": 0,
        "low": 0,
        "avg": 0,
        "lastbuy": 0.00000007,
        "lastsell": 0.00000008,
        "buy": 0.00000007,
        "sell": 0.00000008,
        "lastprice": 0.00000008,
        "updated": 1459411200
        }
        """
        return self._get(self.url_for(PATH_PRICES))
    
    '''
    Online volume report for last 24 hours at a given coin market.
    '''
    def volume_last24hrs(self, coin):
        """
        GET /volume_btc.json
        curl https://c-cex.com/t/volume_btc.json
        {
        "ticker": {
        "usd": {
        "last": 0.00240391,
        "vol": 0.08700954
        },
        "1337": {
        "last": 0.00000008,
        "vol": 0.05472871
        }, ... }
        }
        """
        return self._get(self.url_for(str("volume_"+coin+".json").lower()))
    
    '''
    Get the open and available trading markets along with other meta data
    '''
    def getmarkets(self, parameters=None):
        data = self._get(self.url_for(PATH_PUBLIC, parameters={'a':'getmarkets'}))
        return data

    '''
    Get the last 24 hour summary of all active markets.
    '''
    def getmarketsummaries(self, parameters=None):
        data = self._get(self.url_for(PATH_PUBLIC, parameters={'a':'getmarketsummaries'}))
        return data

    
    '''
    Retrieve the orderbook for a given market.
    '''
    def get_order_book(self, market,orderType,depth=None):
        '''
        market	required	Market name (ex: USD-BTC)
        type	required	Type of orders to return: "buy", "sell" or "both"
        depth	optional	Depth of an order book to retrieve. Default is 50, max is 100
        '''
        parameters = {'a':'getorderbook','market':str(market).lower(),'type':str(orderType).lower(),'depth':depth}
        if depth == None:
            parameters = {'a':'getorderbook','market':market,'type':orderType}
        data = self._get(self.url_for(PATH_PUBLIC, parameters=parameters))
        datadict_ = {}
        for type_ in data.keys():
            if isinstance(data[type_], dict):
                 datadict_ = data[type_]
                 for list_ in datadict_.keys():
                     for content_ in datadict_[list_]:
                         for key, value in content_.items():
                             content_[key] = float(value)

        return datadict_

    '''
    Retrieve the orderbook for all markets.
    '''
    def getfullorderbook(self,depth=None):
        '''
        depth	optional	Depth of an order book to retrieve. Default is 50, max is 100
        '''
        parameters = {'a':'getfullorderbook','depth':depth}
        if depth == None:
            parameters = {'a':'getfullorderbook'}
        data = self._get(self.url_for(PATH_PUBLIC, parameters=parameters))
        return data
    
    '''
    Latest trades that have occured for a specific market.
    '''
    def getmarkethistory(self, market,count = None):
        '''
        market	required	Market name (ex: USD-BTC)
        count	optional	Number of entries to return. Range 1-100, default is 50
        '''
        parameters = {'a':'getmarkethistory','market':str(market).lower(),'count':count}
        if count == None:
            parameters = {'a':'getmarkethistory','market':market}
        data = self._get(self.url_for(PATH_PUBLIC, parameters=parameters))
        return data

    '''
    Latest trades that have occured for all markets.
    '''
    def getfullmarkethistory(self,count = None):
        '''
        count	optional	Number of entries to return. Range 1-100, default is 50
        '''
        parameters = {'a':'getfullmarkethistory','count':count}
        if count == None:
            parameters = {'a':'getfullmarkethistory'}
        data = self._get(self.url_for(PATH_PUBLIC, parameters=parameters))
        return data
        
    '''
    Exchange's wallet balance distribution for specific currency.
    '''
    def getbalancedistribution(self, currencyname):
        '''
        currencyname	required	Name of currency (ex: GRC)
        '''
        parameters = {'a':'getbalancedistribution','currencyname':str(currencyname).lower()}
        data = self._get(self.url_for(PATH_PUBLIC, parameters=parameters))
        return data
    
    def _convert_to_floats(self, data):
        """
        Convert all values in a dict to floats
        """
        for key, value in data.items():
            data[key] = float(value)

        return data


    def _get(self, url):
        try:
            return requests.get(url, timeout=TIMEOUT).json()
        except:
            return {"success" : False,"message" : "no responce from Server"}




    def _build_parameters(self, parameters):
        # sort the keys so we can test easily in Python 3.3 (dicts are not
        # ordered)
        keys = list(parameters.keys())
        keys.sort()

        return '&'.join(["%s=%s" % (k, parameters[k]) for k in keys])

class TradeClient(Client):
    """
    Authenticated client for trading through C-Cex API
    """
    
    def __init__(self, acct):
        self.URL = "{0:s}://{1:s}/{2:s}/{3:s}".format(PROTOCOL, HOST, VERSION,PATH_PRIVATE)
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
        req_kwargs = {}
        url_encoded_params = urllib.urlencode(payload)
        url = self.URL + url_encoded_params
        sig = hmac.new(self.SECRET.encode('utf-8'), url.encode('utf-8'),hashlib.sha512).hexdigest()
        # update req_kwargs keys
        req_kwargs['headers'] = {'apisign': sig}
        req_kwargs['url'] = url
        return req_kwargs


    '''
    Retrieve the balance from your account for a specific currency.
    
    {
    "success" : true,
    "message" : "",
    "result" : {
    "Currency" : "BTC",
    "Balance" : 20,
    "Available" : 3.78231923,
    "Pending" : 0.00000000,
    "CryptoAddress" : "1Euo2hfrw9cSWZGstPcRwDaHtcvL8iyJXP",
    "Requested" : false,
    "Uuid" : null
    }
    }
    '''
    def get_balance(self, symbol):
        '''
        currency	required	Currency name (ex: BTC)
        '''
        payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'currency': symbol,'a': 'getbalance'}
        signed_payload = self._sign_payload(payload)

        try:
            balance_resp = requests.request('GET', **signed_payload)
            json_bal_resp = balance_resp.json()
            return json_bal_resp
        except:
            return {"success" : False,"message" : "no responce from Server"}




    '''
    Retrieve all balances from your account.
    
    {
    "success": true,
    "message": "",
    "result": [{
    "Currency": "USD",
    "Balance": 0.00000000,
    "Available": 0,
    "Pending": 0.00000000,
    "CryptoAddress": ""
    }, {
    "Currency": "BTC",
    "Balance": 53.04269984,
    "Available": 3.41248203,
    "Pending": 0.00000000,
    "CryptoAddress": "1Euo2hfrw9cSWZGstPcRwDaHtcvL8iyJXP"
    }, ... ]
    }
    '''
    def get_all_balances(self):
        payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'a': 'getbalances'}
        signed_payload = self._sign_payload(payload)

        try:
            r = requests.request('GET', **signed_payload)
            json_resp = r.json()

            return json_resp
        except:
            return {"success" : False,"message" : "no responce from Server"}


    

    '''
    The response message after placing the order is as follows:
    {
    "success": true,
    "message": "",
    "result": {
    "uuid": "8228499"
    }
    }
    '''
    def place_order(self, market, quantity, rate, side):
        '''
        market	    required	Market name (ex: USD-BTC)
        quantity    required	Amount to purchase
        rate	    required	Rate at which to place the order
        side        required            order side as buy  or sell
        '''
        if type(quantity) != type(Decimal('0.01')):
            quantity = str(Decimal(str(quantity)))
        if type(rate) != type(Decimal('0.01')):
            rate = str(Decimal(str(rate)))
        
        payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'a': str(side).lower()+'limit','market':market.lower(),'quantity':quantity,'rate':rate}
        signed_payload = self._sign_payload(payload)

        try:
            r = requests.request('GET', **signed_payload)

            json_resp = r.json()
            return json_resp
        except:
            return {"success" : False,"message" : "no responce from Server"}

    '''
    The response message after calling the cancel order method if the cancel is success is as follows:
    {
    "success" : true,
    "message" : "",
    "result" : null
    }
    '''
    def cancel_order(self,uuid):
        '''
        uuid	required	uuid of buy or sell order
        '''
        payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'a': 'cancel','uuid':uuid}
        signed_payload = self._sign_payload(payload)

        try:
            r = requests.request('GET', **signed_payload)

            json_resp = r.json()
            return json_resp
        except:
            return {"success" : False,"message" : "no responce from Server"}

    '''
    Retrieve a single order by uuid.
    
    {
    "success": true,
    "message": "",
    "result": [{
    "AccountId": null,
    "OrderUuid": "2137716",
    "Exchange": "NVC-BTC",
    "Type": "LIMIT_SELL",
    "Quantity": 228.70070713,
    "QuantityRemaining": 228.70070713,
    "Limit": 0.00289999,
    "Reserved": 228.70070713,
    "ReserveRemaining": 228.70070713,
    "CommissionReserved": 0.00000000,
    "CommissionReserveRemaining": 0.00000000,
    "CommissionPaid": 0.00000000,
    "Price": 0.00000000,
    "PricePerUnit": null,
    "Opened": "2015-12-28 23:20:04",
    "Closed": null,
    "IsOpen": true,
    "Sentinel": "2137716",
    "CancelInitiated": false,
    "ImmediateOrCancel": false,
    "IsConditional": false,
    "Condition": "NONE",
    "ConditionTarget": null
    }]
    }'''
    def get_orderStatus(self,uuid):
        '''
        uuid	required	uuid of the buy or sell order
        '''
        payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'a': 'getorder','uuid':uuid}
        signed_payload = self._sign_payload(payload)
        #print(signed_payload)

        try:
            r = requests.request('GET', **signed_payload)

            json_resp = r.json()
            return json_resp
        except:
            return {"success" : False,"message" : "no responce from Server"}



    '''
    Get all orders that you currently have opened. A specific market can be requested.
    
    {
    "success": true,
    "message": "",
    "result": [{
    "Uuid": null,
    "OrderUuid": "2227714",
    "Exchange": "NVC-BTC",
    "OrderType": "LIMIT_SELL",
    "Quantity": 200,
    "QuantityRemaining": 200,
    "Limit": 0.00215000,
    "CommissionPaid": 0.00000000,
    "Price": 0.00000000,
    "PricePerUnit": null,
    "Opened": "2015-11-28 23:19:22",
    "Closed": null,
    "CancelInitiated": false,
    "ImmediateOrCancel": false,
    "IsConditional": false,
    "Condition": "NONE",
    "ConditionTarget": null
    }, {
    "Uuid": null,
    "OrderUuid": "2071587",
    "Exchange": "LTC-BTC",
    "OrderType": "LIMIT_BUY",
    "Quantity": 999.99999999,
    "QuantityRemaining": 999.99999999,
    "Limit": 0.00300000,
    "CommissionPaid": 0.00000000,
    "Price": 0.00000000,
    "PricePerUnit": null,
    "Opened": "2015-11-16 02:25:29",
    "Closed": null,
    "CancelInitiated": false,
    "ImmediateOrCancel": false,
    "IsConditional": false,
    "Condition": "NONE",
    "ConditionTarget": null
    }, ... ]
    }'''
    def get_openorders(self,market=None):
        '''
        market	optional	Market name (ex: USD-BTC)
        '''
        payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'a': 'getopenorders','market':market}
        if type(market) == type(None):
            payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'a': 'getopenorders'}
        
        signed_payload = self._sign_payload(payload)

        try:
            r = requests.request('GET', **signed_payload)

            json_resp = r.json()
            return json_resp
        except:
            return {"success" : False,"message" : "no responce from Server"}


    '''
    Retrieve your order history.
    
    {
    "success": true,
    "message": "",
    "result": [{
    "OrderUuid": "2228451",
    "Exchange": "GRC-BTC",
    "TimeStamp": "2015-11-29 01:55:54",
    "OrderType": "LIMIT_BUY",
    "Limit": 0.00002096,
    "Quantity": 0.00020960,
    "QuantityRemaining": 0.00000000,
    "Commission": 0.00000042,
    "Price": 0,
    "PricePerUnit": 0.00002096,
    "IsConditional": false,
    "Condition": null,
    "ConditionTarget": null,
    "ImmediateOrCancel": false
    }, {
    "OrderUuid": "2202320",
    "Exchange": "BTC-DASH",
    "TimeStamp": "2015-11-25 11:06:23",
    "OrderType": "LIMIT_SELL",
    "Limit": 0.00630000,
    "Quantity": 183.48472577,
    "QuantityRemaining": 178.82359683,
    "Commission": 0.36696945,
    "Price": 1.15595377,
    "PricePerUnit": 0.00630000,
    "IsConditional": false,
    "Condition": null,
    "ConditionTarget": null,
    "ImmediateOrCancel": false
    }]
    }'''
    def get_orderhistory(self, market = None, count = None):
        '''
        market	optional	Market name (ex: USD-BTC). If ommited, will return for all markets
        count	optional	Number of records to return
        '''
        payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'a': 'getorderhistory','market':market,'count':count}
        if type(market) == type(None) and type(count) == type(None):
            payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'a': 'getorderhistory'}
        elif type(market) == type(None):
            payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'a': 'getorderhistory','count':count}
        elif type(count) == type(None):
            payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'a': 'getorderhistory','market':market}
        
        signed_payload = self._sign_payload(payload)

        try:
            r = requests.request('GET', **signed_payload)
            json_resp = r.json()
            return json_resp
        except:
            return {"success" : False,"message" : "no responce from Server"}

    '''
    Retrieve detailed trading history.
    
    {
    "success": true,
    "return": [{
    "tradeid": "248725grc",
    "tradetype": "Sell",
    "datetime": "2015-10-28 03:18:29",
    "marketid": "GRC-BTC",
    "tradeprice": "0.00002900",
    "quantity": "30000.00000000",
    "fee": "0.00174000",
    "total": "0.87000000",
    "initiate_ordertype": "Buy",
    "order_id": "7324857"
    }, {
    "tradeid": "248724grc",
    "tradetype": "Sell",
    "datetime": "2015-10-28 03:18:20",
    "marketid": "GRC-BTC",
    "tradeprice": "0.00002900",
    "quantity": "20000.00000000",
    "fee": "0.00116000",
    "total": "0.58000000",
    "initiate_ordertype": "Buy",
    "order_id": "7324856"
    }]
    }'''
    def get_tradehistory(self, marketid, limit = None):
        '''
        marketid	required	Market name (ex: GRC-BTC)
        '''
        payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'a': 'mytrades','marketid':marketid,'limit':limit}
        if type(limit) == type(None):
            payload = {'apikey': self.KEY,'nonce': self.get_nonce(),'a': 'mytrades','marketid':marketid}
        
        signed_payload = self._sign_payload(payload)

        try:
            r = requests.request('GET', **signed_payload)
            json_resp = r.json()
            return json_resp
        except:
            return {"success" : False,"message" : "no responce from Server"}
