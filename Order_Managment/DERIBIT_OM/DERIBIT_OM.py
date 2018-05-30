from deribit import client as deb
import datetime, time
from Order import Order


def nowStr(isDate=False):
    if isDate:
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]


class MyDERBIT():
    def __init__(self):
        self.key = "M7UPSXUFxxnM"
        self.secret = "QGLTLJKX2AWLNHU2OBVGGIGHTOE3363W"

class OM():
    def __init__(self):
        self.exchCode = 'DERBIT'
        self.derbitConfig = MyDERBIT()
        self.trading_client = deb.TradeClient(self.derbitConfig)

    def create(self, o):
        ackMsg = self.trading_client.place_order(market= o.symbol, quantity = o.qty, rate=o.price, side=o.side) # here you have to pass the order side as buy  or sell
        if ackMsg.has_key('result') and ackMsg['success'] == 'False':
            return ackMsg
        else:
            return ackMsg





#print(OM().trading_client.get_openorders())
#print(OM().trading_client.cancel_order("4650077946"))