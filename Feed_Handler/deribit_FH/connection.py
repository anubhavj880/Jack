import websocket
import Utils
import time
import thread
import json
import base64



log = Utils.getLogger(loggerName='DERIBITDataRecorder',logLevel='INFO')

class DerbitConnection():
    gemini_api_key = ""
    gemini_api_secret = ""

    def __init__(self, url,payload, onUpdate):
        self.url = url
        self.payload = payload
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

    def connect_Socket(self):
        websocket.enableTrace(False)

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



    def _on_message(self, ws, message):
        try:
            exchData = json.loads(message)
            print(exchData)
            if type(exchData) is dict and (exchData["success"] == True) and ('bids' in exchData["result"]) and ('asks' in exchData["result"]):
                self.orderBookData(exchData['result'])
            elif type(exchData) is dict and (exchData["success"] == True) and type(exchData["result"]) is list and (len(exchData['result']) > 0) and ('tradeId' in exchData['result'][0].keys()):
                for trade in exchData['result']:
                    self.onUpdate([float(trade['price']), float(trade['quantity']), trade['tradeId']],'tradebook_' + str(trade['instrument']))
            elif type(exchData) is dict and exchData['success'] == True:
                self.onUpdate(exchData)
                print(exchData)
        except Exception as ex:
            log.error("The following Exception has occured in _On_Message method  : " + str(ex))

    def orderBookData(self, rawOrderData):
        bids = []
        bidSizes = []
        asks = []
        askSizes = []
        for orderUpdate in rawOrderData["bids"]:
            self.bidOrderBook.append(orderUpdate)
        for orderUpdate in rawOrderData["asks"]:
            self.askOrderBook.append(orderUpdate)
        self.bidOrderBook = sorted(self.bidOrderBook, key=lambda k: float(k['price']), reverse=True)
        self.askOrderBook = sorted(self.askOrderBook, key=lambda k: float(k['price']), reverse=False)
        for bid in self.bidOrderBook:
            bids.append(bid['price'])
            bidSizes.append(bid['quantity'])
        for ask in self.askOrderBook:
            asks.append(ask['price'])
            askSizes.append(ask['quantity'])
        self.onUpdate([zip(bids, bidSizes)[:5], zip(asks, askSizes)[:5]], 'orderbook_' + rawOrderData['instrument'])

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

        def run(*args):
            while True:
                time.sleep(1)
                ws.send(self.payload)
            time.sleep(1)
            ws.close()

        thread.start_new_thread(run, ())
        if self.onConnected is not None:
            self.onConnected()

