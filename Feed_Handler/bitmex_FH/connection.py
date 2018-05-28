import websocket
import Utils
import json, base64, hashlib, urlparse, hmac, time
log = Utils.getLogger(loggerName='BitmexConnection',logLevel='INFO')

nonce = int(round(time.time() * 1000))
VERB = "GET"
ENDPOINT = "/realtime"
API_SECRET = "wIgYaZHZXFx5it5mefwmilK2VQJcbnkftfjR8HNZBZ0v--EF"
API_KEY = "_loCqEYQjeSAZFY_VescfuMO"


class Connection():

    def __init__(self, url, schema, onUpdate,onPrivateUpdate):
        self.url = url
        self.socket = self.onConnected = self.onReconnected = self.onDisconnected = self.onConnectError = None
        self.bidOrderBook = {}
        self.askOrderBook = {}
        self.schema = schema
        self.onUpdate = onUpdate
        self.onPrivateUpdate = onPrivateUpdate
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
        exchData = json.loads(message)
        if type(exchData) is dict and ('table' in exchData) and (exchData['table'] == 'orderBookL2'):
            self.prepareOrderBook(exchData)

        elif type(exchData) is dict and ('table' in exchData) and (exchData['table'] == 'trade'):
            self.onUpdate([float(exchData['data'][0]['price']),float(exchData['data'][0]['size']),exchData['data'][0]['trdMatchID']], 'tradebook_' + str(exchData['data'][0]['symbol']).upper())

        elif type(exchData) is dict and ('table' in exchData)and (exchData['table'] in ('order','position','wallet','transact','execution','margin')):
            self.onPrivateUpdate(exchData)


    def prepareOrderBook(self, orderData):
        bids = []
        bidSizes = []
        asks = []
        askSizes = []
        symbol = str(orderData['data'][0]['symbol']).upper()

        if orderData['action'] == 'partial':
            '''
            The snapshot of order data will be identified by orderData['action'] == 'partial 
            '''
            self.bidOrderBook[symbol] = []
            self.askOrderBook[symbol] = []
            for oData in orderData['data']:
                if str(oData['side']).lower() == 'buy':
                    self.bidOrderBook[symbol].append(oData)
                elif str(oData['side']).lower() == 'sell':
                    self.askOrderBook[symbol].append(oData)
        elif orderData['action'] == 'insert':
            for insertData in orderData['data']:
                if str(insertData['side']).lower() == 'buy':
                    self.bidOrderBook[symbol].append(insertData)
                elif str(insertData['side']).lower() == 'sell':
                    self.askOrderBook[symbol].append(insertData)
        elif orderData['action'] == 'update':
            for updateData in orderData['data']:
                if str(updateData['side']).lower() == 'buy':
                    for bidData in self.bidOrderBook[symbol]:
                        if bidData['id'] == updateData['id']:
                            bidData.update((k, updateData['size'])for k, v in bidData.iteritems() if k == "size")
                elif str(updateData['side']).lower() == 'sell':
                    for askData in self.askOrderBook[symbol]:
                        if askData['id'] == updateData['id']:
                            askData.update((k, updateData['size'])for k, v in askData.iteritems() if k == "size")
        elif orderData['action'] == 'delete':
            for deleteData in orderData['data']:
                if str(deleteData['side']).lower() == 'buy':
                    for bidData in self.bidOrderBook[symbol]:
                        if bidData['id'] == deleteData['id']:
                            self.bidOrderBook[symbol].remove(bidData)
                    #self.bidOrderBook[symbol] = sorted(self.bidOrderBook[symbol], key=lambda k: k['price'],reverse=True)
                elif str(deleteData['side']).lower() == 'sell':
                    for askData in self.askOrderBook[symbol]:
                        if askData['id'] == deleteData['id']:
                            self.askOrderBook[symbol].remove(askData)
                    #self.askOrderBook[symbol] = sorted(self.askOrderBook[symbol], key=lambda k: k['price'],reverse=False)
        self.bidOrderBook[symbol] = sorted(self.bidOrderBook[symbol], key=lambda k: k['price'], reverse=True)
        self.askOrderBook[symbol] = sorted(self.askOrderBook[symbol], key=lambda k: k['price'], reverse=False)
        for bid in self.bidOrderBook[symbol]:
            bids.append(bid['price'])
            bidSizes.append(bid['size'])
        for ask in self.askOrderBook[symbol]:
            asks.append(ask['price'])
            askSizes.append(ask['size'])
        self.onUpdate([zip(bids, bidSizes)[:5],zip(asks, askSizes)[:5]],'orderbook_' + symbol)

    def bitmex_signature(self, apiSecret, verb, url, nonce):
        """Given an API Secret key and data, create a BitMEX-compatible signature."""
        parsedURL = urlparse.urlparse(url)
        path = parsedURL.path
        if parsedURL.query:
            path = path + '?' + parsedURL.query
        log.info("Computing HMAC: %s" % verb + path + str(nonce))
        message = bytes(verb + path + str(nonce)).encode('utf-8')
        log.info("Signing: %s" % str(message))
        signature = hmac.new(apiSecret, message, digestmod=hashlib.sha256).hexdigest()
        log.info("Signature: %s" % signature)
        return signature

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

        '''
        this subscription is done for authenticating the user
        '''
        self.socket.send(json.dumps({"op": "authKey", "args": [API_KEY, nonce, self.bitmex_signature(API_SECRET, VERB, ENDPOINT, nonce)]}))
        log.info("Sent Auth request")
        '''
        This schema contains all schemas for both public and private user data. which can be done in single subscription.
        '''
        self.socket.send(self.schema)

