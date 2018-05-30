import time, hashlib, requests, base64
from collections import OrderedDict


PROTOCOL = "https"
HOST = "www.deribit.com"

class TradeClient():

    def __init__(self, acct, url=None):
        self.key = acct.key
        self.secret = acct.secret
        self.session = requests.Session()

        if url:
            self.url = url
        else:
            self.url = self.URL = "{0:s}://{1:s}".format(PROTOCOL, HOST)

    def request(self, action, data):
        response = None

        if action.startswith("/api/v1/private/"):
            if self.key is None or self.secret is None:
                raise Exception("Key or secret empty")

            signature = self.generate_signature(action, data)
            response = self.session.post(self.url + action, data=data, headers={'x-deribit-sig': signature},
                                         verify=True)
            print(response.text)

        else:
            response = self.session.get(self.url + action, params=data, verify=True)

        if response.status_code != 200:
            raise Exception("Wrong response code: {0}".format(response.status_code))

        json = response.json()

        if json["success"] == False:
            raise Exception("Failed: " + json["message"])

        if "result" in json:
            return json

        elif "message" in json:
            return json["message"]
        else:
            return "Ok"

    def generate_signature(self, action, data):
        tstamp = int(time.time() * 1000)
        signature_data = {
            '_': tstamp,
            '_ackey': self.key,
            '_acsec': self.secret,
            '_action': action
        }
        signature_data.update(data)
        sorted_signature_data = OrderedDict(sorted(signature_data.items(), key=lambda t: t[0]))

        def converter(data):
            key = data[0]
            value = data[1]
            if isinstance(value, list):
                return '='.join([str(key), ''.join(value)])
            else:
                return '='.join([str(key), str(value)])

        items = map(converter, sorted_signature_data.items())

        signature_string = '&'.join(items)

        sha256 = hashlib.sha256()
        sha256.update(signature_string.encode("utf-8"))
        sig = self.key + "." + str(tstamp) + "."
        sig += base64.b64encode(sha256.digest()).decode("utf-8")
        return sig

    def get_balance(self):
        return self.request("/api/v1/private/account", {})

    def place_order(self, market, quantity, rate, side, postOnly=None, label=None):

        options = {
            "instrument": market,
            "quantity": quantity,
            "price": rate
        }

        if label:
            options["label"] = label

        if postOnly:
            options["postOnly"] = postOnly

        if side == "buy":
            return self.request("/api/v1/private/buy", options)
        if side == "sell":
            return self.request("/api/v1/private/sell", options)

    def cancel_order(self, uuid):
        options = {
            "orderId": uuid
        }

        return self.request("/api/v1/private/cancel", options)

    def get_orderStatus(self, uuid):
        options = {}

        options["orderId"] = uuid
        return self.request("/api/v1/private/orderstate", options)



    def get_openorders(self, instrument=None, uuid=None):
        options = {}

        if instrument:
            options["instrument"] = instrument
        if uuid:
            options["orderId"] = uuid

        return self.request("/api/v1/private/getopenorders", options)

    def get_tradehistory(self, marketid="all", limit=None, startTradeId=None):
        options = {
            "instrument": marketid
        }

        if limit:
            options["count"] = limit
        if startTradeId:
            options["startTradeId"] = startTradeId

        return self.request("/api/v1/private/tradehistory", options)




