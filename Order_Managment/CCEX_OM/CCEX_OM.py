from ccex import client as cex
import datetime, time
from decimal import Decimal
from Order import Order
import ast
'''
import logging
log = logging.getLogger('myTesting')
log.setLevel(logging.INFO)
log_path = 'C:/tmp/ccex_example.txt'
fh = logging.FileHandler(log_path)
log.addHandler(fh)
'''
'''
Error_code:
0: 'None'
1: 'Nonce is too small.'
999: Others
'''
def nowStr(isDate=False):
    if isDate:
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]

class MyCCEX():
    def __init__(self):
        self.key = "A3322F688CDAACA79DC2A40E79FE8D8C"
        self.secret = "A97E6AF4DEAA508977D0B19BA1A1A2A7"
        
class OM():
    def __init__(self):
        self.exchCode = 'CCEX'
        self.ccexConfig = MyCCEX() 
        self.trading_client = cex.TradeClient(self.ccexConfig)
        self.cxlNb = 0
        self.retryNum = 5
    '''
        passing object should have 4 parameter in constructor of class ('grc-btc',100,0.00001,'sell')
    '''
    def create(self, o):
        ackMsg = self.trading_client.place_order(market= o.symbol, quantity = o.qty, rate=o.price, side=o.side) # here you have to pass the order side as buy  or sell 
        if type(ackMsg) == dict and ackMsg['success'] == True:
            return ackMsg
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            return intAckMsg

    def isActive(self, ackMsg):
        odid = None
        if type(ackMsg) == dict and ackMsg['success'] == True:
            odid = str(ackMsg['result']['uuid'])
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')
            return odid, timestamp, ackMsg
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            return odid, intAckMsg

    def cxl(self, odid):
        ackMsg = self.trading_client.cancel_order(uuid=odid)
        if type(ackMsg) == dict and ackMsg['success'] == True:
            return ackMsg
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            return intAckMsg
    '''
    This is the JSON return by exchange after cancel order
    {
        "success" : true,
        "message" : "",
        "result" : null
    } 
    
    So i don't know tradedPrice, tradedQty, remainQty are there in result or not
    '''
    def isCxlSuccess(self, ackMsg):
        if type(ackMsg) == dict and ackMsg['success'] == True:
            orderStatus = 'CXLED'
            tradedPrice, tradedQty, remainQty = None, None, None
            return (orderStatus, tradedPrice, tradedQty, remainQty)
        else:
            return self.readOrderStatus(ackMsg)

    def isCxlAllSuccess(self):
        ackMsg = self.trading_client.get_openorders()
        if type(ackMsg) == dict and ackMsg['success'] == True:
            if not len(ackMsg['result']):
                return True
            else:
                return False
        else:
            return self.readOrderStatus(ackMsg)

    def checkOrderStatus(self, o):
        ackMsg = self.trading_client.get_orderStatus(o.odid)
        if type(ackMsg) == dict and ackMsg['success'] == True:
            return self.readOrderStatus(ackMsg)
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            return intAckMsg


    def readOrderStatus(self, ackMsg):
        if type(ackMsg) != dict:
            return self.handleUnknownMsg(ackMsg)
        orderStatus = None
        tradedPrice, tradedQty, remainQty = None, None, None

        if type(ackMsg) == dict and ackMsg['success'] == True:
            
            isTraded    = not ackMsg['result'][0]['IsOpen'] and not ackMsg['result'][0]['CancelInitiated']
            isCancelled = not ackMsg['result'][0]['IsOpen'] and ackMsg['result'][0]['CancelInitiated']
            isActive    = ackMsg['result'][0]['IsOpen'] and not ackMsg['result'][0]['CancelInitiated']
            unknown     = ackMsg['result'][0]['IsOpen'] and ackMsg['result'][0]['CancelInitiated']

            if isTraded:
                tradedPrice = float(ackMsg['result'][0]['Price'])
                tradedQty   = float(ackMsg['result'][0]['Quantity'])
                remainQty   = float(ackMsg['result'][0]['QuantityRemaining'])
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



    def getInitActiveOrders(self,market=None):
        ackMsg = self.trading_client.get_openorders(market)
        if type(ackMsg) == dict and ackMsg['success'] == True:
            if not len(ackMsg['result']):
                return ackMsg
            else:
                tmpActiveOrderList = []
                ackResult = ackMsg['result']
                for i in range(len(ackResult)):
                    obj         = ackResult[i]
                    odid        = str(obj['OrderUuid'])
                    symbol      = str(obj['Exchange']).upper().split("-")
                    sym_        = symbol[:3]
                    _sym        = symbol[3:]
                    orderType   = str(obj['OrderType']).upper().split("_")[0]
                    price       = float(obj['Price'])
                    side        = str(obj['OrderType']).upper().split("_")[1]
                    qty         = float(obj['QuantityRemaining'])
                    o = Order(self.exchCode, sym_, _sym, orderType, price, side, qty)
                    o.odid = odid
                    o.status = 'ACTIVE'
                    o.activeTs = nowStr()
                    tmpActiveOrderList.append(o)
                return tmpActiveOrderList
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            '''log.error('Unexpected ackMsg::getInitActiveOrders %s %s' % (self.exchCode, intAckMsg))'''
            return intAckMsg

    def get_balance(self):

        ackMsg = self.trading_client.get_all_balances()

        if type(ackMsg) == dict and ackMsg['success'] == True:
            self.balances = {}
            self.available = {}
            for pdt in ackMsg['result']:
                self.balances[str(pdt['Currency'].upper())] = float(pdt['Balance'])
                self.available[str(pdt['Currency'].upper())] = float(pdt['Available'])
        else:
            intAckMsg = self.handleUnknownMsg(ackMsg['message'])
            '''log.error('Unexpected ackMsg::getBalances %s %s' % (self.exchCode, intAckMsg))'''
            return intAckMsg
        return self.balances, self.available

    def handleUnknownMsg(self, ackMsg):
        if ackMsg is None:
            return 'INT_ERR_0'
        elif type(ackMsg) == str or type(ackMsg) == unicode:
            ackMsg = ackMsg.lower()
            if 'nonce' in ackMsg:
                return 'INT_ERR_1'
            elif 'found' in ackMsg and 'no' in ackMsg:
                return 'INT_ERR_2'
            else:
                return ('INT_ERR_999: ' + ackMsg)
        else:
            return 'Unexpected ackMsg: %s, waiting to handle it in handleUnknownMsg()' % ackMsg




