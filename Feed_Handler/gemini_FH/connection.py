import websocket
import Utils
import time
import json
import base64
import hmac
from hashlib import sha384


log = Utils.getLogger(loggerName='GEMINIDataRecorder',logLevel='INFO')

class DerbitConnection():
    gemini_api_key = "P5BDs6mjLEi5IbXHXKIy"
    gemini_api_secret = "25Uio9hQZjpp3iYLpQ1AhLgc7zV4"

    payload = base64.b64encode(json.dumps({
        'request': '/v1/order/events',
        'nonce': long(float('%.9f' % time.time()) * 1000000000)
    }, separators=(',', ':')))

    signature = hmac.new(gemini_api_secret, payload, sha384).hexdigest()


    def __init__(self, url, onUpdate):
        self.url = url
        self.currencyPair = str(url).split("/")[-1]
        self.socket = self.onConnected = self.onReconnected = self.onDisconnected = self.onConnectError = None
        self.onUpdate = onUpdate
        self.bidOrderBook = []
        self.askOrderBook = []
        self.disconnect_called = False
        self.needs_reconnect = False
        self.default_reconnect_interval = 3
        self.reconnect_interval = 3

    def setBasicListener(self, onConnected, onDisconnected, onConnectError, onReconnected):
        self.onConnected = onConnected
        self.onDisconnected = onDisconnected
        self.onConnectError = onConnectError
        self.onReconnected = onReconnected

    def disconnect(self):
        self.needs_reconnect = False
        self.disconnect_called = True
        if self.socket:
            self.socket.close()

    def reconnect(self, reconnect_interval=None):
        if self.onReconnected is not None:
            self.onReconnected()
        if reconnect_interval is None:
            reconnect_interval = self.default_reconnect_interval
        log.info("Connection: Reconnect in %s" % reconnect_interval)
        self.reconnect_interval = reconnect_interval
        self.needs_reconnect = True
        if self.socket:
            self.socket.close()

    def connect_Socket(self, num):
        websocket.enableTrace(False)
        if num == 1:
            self.socket = websocket.WebSocketApp(self.url,
                                                 on_message=self._on_message,
                                                 on_error=self._on_error,
                                                 on_close=self._on_close,
                                                 on_open=self._on_open)
            while True:
                try:
                    self.socket.run_forever()
                    break
                except Exception as err:
                    log.error("The Following error occured: %s" % (err))

            while self.needs_reconnect and not self.disconnect_called:
                log.info("Attempting to connect again in %s seconds."% self.reconnect_interval)
                time.sleep(self.reconnect_interval)
                # We need to set this flag since closing the socket will set it to
                # false
                self.socket.keep_running = True
                self.socket.run_forever()

        if num == 2:
            self.socket = websocket.WebSocketApp(self.url,
                                                 on_message=self._on_message,
                                                 on_error=self._on_error,
                                                 on_close=self._on_close,
                                                 on_open=self._on_open,
                                                 header={
                                                     'X-GEMINI-PAYLOAD:%s' % self.payload,
                                                     'X-GEMINI-APIKEY:%s' % self.gemini_api_key,
                                                     'X-GEMINI-SIGNATURE:%s' % self. signature
                                                 }
                                                 )
            while True:
                try:
                    self.socket.run_forever()
                    break
                except Exception as err:
                    log.error("The Following error occured: %s" % (err))

            while self.needs_reconnect and not self.disconnect_called:
                log.info("Attempting to connect again in %s seconds."% self.reconnect_interval)
                time.sleep(self.reconnect_interval)
                # We need to set this flag since closing the socket will set it to
                # false
                self.socket.keep_running = True
                self.socket.run_forever()

    def _on_message(self, ws, message):
        print(message)
        try:
            exchData = json.loads(message)
            if type(exchData) is dict and ('type' in exchData) and (exchData['type'] == 'update') and (exchData['socket_sequence'] == 0):
                self.orderBookData(exchData['events'])
            elif type(exchData) is dict and ('type' in exchData) and (exchData['type'] == 'update') and (exchData['socket_sequence'] > 0):
                for updatejson in exchData['events']:
                    if updatejson['type'] == 'change':
                        self.orderBookData([updatejson])
                    elif updatejson['type'] == 'trade':
                        self.onUpdate([float(updatejson['price']), float(updatejson['amount']),updatejson['tid']],'tradebook_' + self.currencyPair.upper())
            else:
                self.onUpdate(exchData)
        except Exception as ex:
            log.error("The following Exception has occured in _On_Message method  : " + str(ex))

    def orderBookData(self, rawOrderData):
        bids = []
        bidSizes = []
        asks = []
        askSizes = []
        for orderUpdate in rawOrderData:
            if orderUpdate['side'] == 'bid':
                if orderUpdate['reason'] == 'initial':
                    self.bidOrderBook.append(orderUpdate)
                elif orderUpdate['reason'] == 'place':
                    checkBidList = []
                    for bidOrder in self.bidOrderBook:
                        if bidOrder['price'] == orderUpdate['price']:
                            checkBidList.append(bidOrder)
                            bidOrder.update((k, orderUpdate['remaining']) for k, v in bidOrder.iteritems() if k == 'remaining')
                    if len(checkBidList) == 0:
                        self.bidOrderBook.append(orderUpdate)
                elif orderUpdate['reason'] == 'cancel':
                    for bidOrder in self.bidOrderBook:
                        if bidOrder['price'] == orderUpdate['price']:
                            self.bidOrderBook.remove(bidOrder)
                elif orderUpdate['reason'] == 'trade':
                    for bidOrder in self.bidOrderBook:
                        if orderUpdate['remaining'] == "0":
                            self.bidOrderBook.remove(bidOrder)
                        elif bidOrder['price'] == orderUpdate['price']:
                            bidOrder.update((k, orderUpdate['remaining']) for k, v in bidOrder.iteritems() if k == 'remaining')
            elif orderUpdate['side'] == 'ask':
                if orderUpdate['reason'] == 'initial':
                    self.askOrderBook.append(orderUpdate)
                elif orderUpdate['reason'] == 'place':
                    checkAskList = []
                    for askOrder in self.askOrderBook:
                        if askOrder['price'] == orderUpdate['price']:
                            checkAskList.append(askOrder)
                            askOrder.update((k, orderUpdate['remaining']) for k, v in askOrder.iteritems() if k == 'remaining')
                    if len(checkAskList) == 0:
                        self.askOrderBook.append(orderUpdate)
                elif orderUpdate['reason'] == 'cancel':
                    for askOrder in self.askOrderBook:
                        if askOrder['price'] == orderUpdate['price']:
                            self.askOrderBook.remove(askOrder)
                elif orderUpdate['reason'] == 'trade':
                    for askOrder in self.askOrderBook:
                        if orderUpdate['remaining'] == "0":
                            self.askOrderBook.remove(askOrder)
                        elif askOrder['price'] == orderUpdate['price']:
                            askOrder.update((k, orderUpdate['remaining']) for k, v in askOrder.iteritems() if k == 'remaining')
        self.bidOrderBook = sorted(self.bidOrderBook, key=lambda k: k['price'], reverse=True)
        self.askOrderBook = sorted(self.askOrderBook, key=lambda k: k['price'], reverse=False)
        for bid in self.bidOrderBook:
            bids.append(bid['price'])
            bidSizes.append(bid['remaining'])
        for ask in self.askOrderBook:
            asks.append(ask['price'])
            askSizes.append(ask['remaining'])
        self.onUpdate([zip(bids, bidSizes)[:5],zip(asks, askSizes)[:5]],'orderbook_' + self.currencyPair.upper())

    def _on_error(self, ws, error):
        log.info("Connection: Error - %s" % error)
        if self.onConnectError is not None:
            self.onConnectError(error)
        self.needs_reconnect = True

    def _on_close(self, ws):
        log.info("Connection: Connection closed")
        if self.onDisconnected is not None:
            self.onDisconnected()

    def _on_open(self, ws):
        log.info("Connection: Connection opened")
        if self.onConnected is not None:
            self.onConnected()

