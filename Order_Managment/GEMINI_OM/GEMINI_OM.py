from gemini import client as gem
import datetime, time
from Order import Order

def nowStr(isDate=False):
    if isDate:
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]


class MyGEMINI():
    def __init__(self):
        self.key = "P5BDs6mjLEi5IbXHXKIy"
        self.secret = "25Uio9hQZjpp3iYLpQ1AhLgc7zV4"

class OM():
    def __init__(self):
        self.exchCode = 'GEMINI'
        self.geminiConfig = MyGEMINI()
        self.trading_client = gem.TradeClient(self.geminiConfig)

    def create(self, o):
        ackMsg = self.trading_client.place_order(market= o.symbol, quantity = o.qty, rate=o.price, side=o.side) # here you have to pass the order side as buy  or sell
        if ackMsg.has_key('result') and ackMsg['result'] == 'error':
            return ackMsg
        else:
            return ackMsg

    def isActive(self, ackMsg):
        odid = None
        if type(ackMsg) == dict and ackMsg.has_key('result')== False:
            odid = str(ackMsg['order_id'])
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')
            return odid, timestamp, ackMsg
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            return odid, intAckMsg


    def cxl(self, odid):
        ackMsg = self.trading_client.cancel_order(uuid=odid)
        if type(ackMsg) == dict and ackMsg.has_key('result') == False:
            return ackMsg
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            return intAckMsg

    def isCxlSuccess(self, ackMsg):
        if type(ackMsg) == dict and ackMsg['is_cancelled'] == True:
            orderStatus = 'CXLED'
            tradedPrice, tradedQty, remainQty = None, None, None
            return (orderStatus, tradedPrice, tradedQty, remainQty)
        else:
            return self.readOrderStatus(ackMsg)

    def isCxlAllSuccess(self):
        ackMsg = self.trading_client.get_openorders()
        if type(ackMsg) == list:
            if not len(ackMsg):
                return True
            else:
                return False
        else:
            return self.handleUnknownMsg(ackMsg['message'])

    def checkOrderStatus(self, o):
        ackMsg = self.trading_client.get_orderStatus(o.odid)
        if type(ackMsg) == dict and ackMsg.has_key('order_id'):
            return self.readOrderStatus(ackMsg)
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            return intAckMsg

    def readOrderStatus(self, ackMsg):
        if type(ackMsg) != dict:
            return self.handleUnknownMsg(ackMsg)
        orderStatus = None
        tradedPrice, tradedQty, remainQty = None, None, None

        if type(ackMsg) == dict and ackMsg.has_key('order_id'):

            isTraded = not ackMsg['is_live'] and not ackMsg['is_cancelled']
            isCancelled = not ackMsg['is_live'] and ackMsg['is_cancelled']
            isActive = ackMsg['is_live'] and not ackMsg['is_cancelled']
            unknown = ackMsg['is_live'] and ackMsg['is_cancelled']

            if isTraded:
                tradedPrice = float(ackMsg['price'])
                tradedQty = float(ackMsg['executed_amount'])
                remainQty = float(ackMsg['remaining_amount'])
                orderStatus = 'FILLED'
            elif isCancelled:
                orderStatus = 'CXLED'
            elif isActive:
                orderStatus = 'ACTIVE'
            else:
                orderStatus = 'UNKNOWN'
            return (orderStatus, tradedPrice, tradedQty, remainQty)
        else:
            return self.handleUnknownMsg(ackMsg['message'])

    def getInitActiveOrders(self):
        ackMsg = self.trading_client.get_openorders()
        if type(ackMsg) == list:
            if not len(ackMsg):
                return ackMsg
            else:
                tmpActiveOrderList = []

                for i in range(len(ackMsg)):
                    obj         = ackMsg[i]
                    odid        = str(obj['order_id'])
                    symbol      = str(obj['symbol'])
                    sym_        = symbol[0]
                    _sym        = symbol[1]
                    orderType   = str(obj['type'])
                    price       = float(obj['price'])
                    side        = str(obj['side'])
                    qty         = float(obj['executed_amount'])
                    o = Order(self.exchCode, sym_, _sym, orderType, price, side, qty)
                    o.odid = odid
                    o.status = 'ACTIVE'
                    o.activeTs = nowStr()
                    tmpActiveOrderList.append(o)
                return tmpActiveOrderList
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            return intAckMsg


    def get_balance(self):

        ackMsg = self.trading_client.get_all_balances()

        if type(ackMsg) == list and len(ackMsg) !=0:
            self.balances = {}
            self.available = {}
            for pdt in ackMsg:
                self.balances[str(pdt['currency'].upper())] = float(pdt['amount'])
                self.available[str(pdt['currency'].upper())] = float(pdt['available'])
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            return intAckMsg
        return self.balances, self.available

    def handleUnknownMsg(self, ackMsg):
        if ackMsg is None:
            return 'INT_ERR_0'
        elif type(ackMsg) == str or type(ackMsg) == unicode:
            ackMsg = ackMsg.lower()
            return ('INT_ERR_999: ' + ackMsg)
        else:
            return 'Unexpected ackMsg: %s, waiting to handle it in handleUnknownMsg()' % ackMsg















