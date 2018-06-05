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

    def isActive(self, ackMsg):
        odid = None
        if type(ackMsg) == dict and ackMsg['result'].has_key('order'):
            odid = str(ackMsg['result']['order']['orderId'])
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')
            return odid, timestamp, ackMsg
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            return odid, intAckMsg

    def cxl(self, odid):
        ackMsg = self.trading_client.cancel_order(uuid=odid)
        if ackMsg.has_key('result') and ackMsg['success'] == 'False':
            return ackMsg
        else:
            return ackMsg

    def isCxlSuccess(self, ackMsg):
        if type(ackMsg) == dict and ackMsg['order']['state'] == "cancelled":
            orderStatus = 'CXLED'
            tradedPrice, tradedQty, remainQty = None, None, None
            return (orderStatus, tradedPrice, tradedQty, remainQty)
        else:
            return self.readOrderStatus(ackMsg)

    def isCxlAllSuccess(self):
        ackMsg = self.trading_client.get_openorders()
        if type(ackMsg['result']) == list:
            if  len(ackMsg) == 0:
                return True
            else:
                return False
        else:
            return self.handleUnknownMsg(ackMsg['message'])

    def checkOrderStatus(self, o):
        ackMsg = self.trading_client.get_orderStatus(o.odid)
        if type(ackMsg) == dict and ackMsg['result'].has_key('orderId'):
            return self.readOrderStatus(ackMsg)
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            return intAckMsg

    def readOrderStatus(self, ackMsg):
        if type(ackMsg) != dict:
            return self.handleUnknownMsg(ackMsg)
        orderStatus = None
        tradedPrice, tradedQty, remainQty = None, None, None

        if ackMsg.has_key('order'):
            if type(ackMsg) == dict and ackMsg['order'].has_key('orderId'):

                isTraded = True if ackMsg['order']['state'] == "filled" else False
                isCancelled = True if ackMsg['order']['state'] == "cancelled" else False
                isActive = True if ackMsg['order']['state'] == "open" else False


                if isTraded:
                    tradedPrice = float(ackMsg['order']['price'])
                    tradedQty = float(ackMsg['order']['quantity'])
                    remainQty = float(ackMsg['order']['quantity']- ackMsg['order']['filledQuantity'])
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
        else:
            if type(ackMsg) == dict and ackMsg['result'].has_key('orderId'):

                isTraded = True if ackMsg['result']['state'] == "filled" else False
                isCancelled = True if ackMsg['result']['state'] == "cancelled" else False
                isActive = True if ackMsg['result']['state'] == "open" else False


                if isTraded:
                    tradedPrice = float(ackMsg['result']['price'])
                    tradedQty = float(ackMsg['result']['quantity'])
                    remainQty = float(ackMsg['result']['quantity']- ackMsg['result'][0]['filledQuantity'])
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
        if type(ackMsg) == dict:
            if len(ackMsg['result']) == 0:
                return ackMsg
            else:
                tmpActiveOrderList = []

                for i in range(len(ackMsg['result'])):
                    obj         = ackMsg['result'][i]
                    odid        = str(obj['orderId'])
                    symbol      = str(obj['instrument'])
                    sym_        = symbol.split('-')[0]
                    _sym        = symbol.split('-')[1]
                    orderType   = str(obj['type'])
                    price       = float(obj['price'])
                    side        = str(obj['direction'])
                    qty         = float(obj['quantity'])
                    o = Order(self.exchCode, sym_, _sym, orderType, price, side, qty)
                    o.odid = odid
                    o.status = 'ACTIVE'
                    o.activeTs = nowStr()
                    tmpActiveOrderList.append(o)
                return tmpActiveOrderList
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            return intAckMsg

    def handleUnknownMsg(self, ackMsg):
        if ackMsg is None:
            return 'INT_ERR_0'
        elif type(ackMsg) == str or type(ackMsg) == unicode:
            ackMsg = ackMsg.lower()
            return ('INT_ERR_999: ' + ackMsg)
        else:
            return 'Unexpected ackMsg: %s, waiting to handle it in handleUnknownMsg()' % ackMsg


#print(OM().trading_client.get_openorders())
#print(OM().trading_client.cancel_order("4680272953"))
#print(OM().trading_client.get_balance())