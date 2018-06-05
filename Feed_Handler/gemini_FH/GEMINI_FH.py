import time, datetime
import threading
import Utils
from connection import GeminiConnection
log = Utils.getLogger(loggerName='GEMINIDataRecorder',logLevel='INFO')

books = {}
exchCode = 'Gemini'

class Book():
    def __init__(self, symbol, exchCode):
        self.symbol = symbol
        self.exchCode = exchCode
        self.bids = []
        self.asks = []
        self.bidSizes = []
        self.askSizes = []
        self.ltp = 0.0
        self.lts = 0.0
        self.trade_id = ''

    def bid(self, limit=0):
        if len(self.bids) == 0:
            return 0
        return self.bids[limit]

    def ask(self, limit=0):
        if len(self.asks) == 0:
            return 0
        return self.asks[limit]

    def bidSize(self, limit=0):
        if len(self.bidSizes) == 0:
            return 0
        return self.bidSizes[limit]

    def askSize(self, limit=0):
        if len(self.askSizes) == 0:
            return 0
        return self.askSizes[limit]

    def onQuote(self, limit, isBid, price, qty, ts):
        import numpy as np
        update = []
        if isBid:
            while len(self.bids) <= limit:
                self.bids.append(0)
            while len(self.bidSizes) <= limit:
                self.bidSizes.append(0)
            if np.not_equal(self.bids[limit], float(price)) or np.not_equal(self.bidSizes[limit], float(qty)):
                update.append((ts, 'B', limit, float(price), float(qty)))
            self.bids[limit] = float(price)
            self.bidSizes[limit] = float(qty)
        else:
            while len(self.asks) <= limit:
                self.asks.append(0)
            while len(self.askSizes) <= limit:
                self.askSizes.append(0)
            if np.not_equal(self.asks[limit], float(price)) or np.not_equal(self.askSizes[limit], float(qty)):
                update.append((ts, 'A', limit, float(price), float(qty)))
            self.asks[limit] = float(price)
            self.askSizes[limit] = float(qty)

    def onTrade(self, price, qty, trade_id, ts):
        if self.trade_id != trade_id:
            self.ltp = price
            self.lts = qty
            self.trade_id = trade_id
        log.info("TradeBook Data  for symbol %s => The ltp is : %s , The lts is : %s , The Trade_id is : %s " % (self.symbol, self.ltp, self.lts, self.trade_id))

    def snapshot(self, ts):
        update = []
        for limit in range(len(self.bids)):
            update.append((ts, 'B', limit, self.bid(limit), self.bidSize(limit)))
        for limit in range(len(self.asks)):
            update.append((ts, 'A', limit, self.ask(limit), self.askSize(limit)))

    def clear(self, bidLimit, askLimit):
        while len(self.bids) > bidLimit:
            self.bids.pop()
        while len(self.bidSizes) > bidLimit:
            self.bidSizes.pop()
        while len(self.asks) > askLimit:
            self.asks.pop()
        while len(self.askSizes) > askLimit:
            self.askSizes.pop()

    def printBook(self):
        msg = 'symbol : %s exchCode : %s nb bids : %d nb asks : %d ltp : %f lts : %f\n' % (
        self.symbol, self.exchCode, len(self.bids), len(self.asks), self.ltp, self.lts)
        for i in range(5):
            msg += '%.8f %.8f | %.8f %.8f\n' % (self.bid(i), self.bidSize(i), self.ask(i), self.askSize(i))
        log.info(msg)
        print(msg)

def onUpdate(data, channel_name, maxNbLimit=None):
    if type(data) is list:
        now = datetime.datetime.now()
        ts = (now - now.replace(hour=0,minute=0,second=0,microsecond=0)).total_seconds()
        symbol = channel_name.split('_')[-1].upper()
        if symbol in books:
            book = books[symbol]
        else:
            book = Book(symbol, exchCode)
            books[symbol] = book
        #start writing info.
        if channel_name.startswith('orderbook'):
            bidList = data[0]
            askList = data[1]
            bidLimit, askLimit =0,0
            for bid in bidList:
                book.onQuote(limit=bidLimit,isBid=True,price=bid[0],qty=bid[1],ts=ts)
                bidLimit += 1
            for ask in askList:
                book.onQuote(limit=askLimit,isBid=False,price=ask[0],qty=ask[1],ts=ts)
                askLimit += 1
            book.clear(bidLimit, askLimit)
        elif channel_name.startswith('tradebook'):
            book.onTrade(price=data[0],qty=abs(data[1]),trade_id=data[2],ts=ts)
        else:
            log.error('onUpdate unsupported message %s: %s' % (channel_name, data))
        book.printBook()
        return

def onPrivateUpdate(data):
    log.info("privateData: " + str(data))


def connect_handler(subscription):
    log.info('Entered connect_handler with schema %s' % (subscription))
    try:
        for SocketUrl in subscription[:-1]:
            socketThread = threading.Thread(target=start,args=(SocketUrl,'m'))
            socketThread.daemon = True
            socketThread.start()

        #socketThread = threading.Thread(target=start, args=(subscription[-1], 'p'))
        #socketThread.daemon = True
        #socketThread.start()



    except Exception as err:
        log.error('The following error has occured in  connect_handler: %s' % (err))

def start(url,type):
    if type == 'm':
        GeminiConnection(url, onUpdate).connect_Socket(1)
    if type == 'p':
        GeminiConnection(url, onPrivateUpdate).connect_Socket(2)

def publicSchema(channels):
    global socketUrlList
    global maxNbLimit
    maxNbLimit = 5
    socketUrlList = []
    for channel in channels:
        socketUrlList.append('wss://api.gemini.com/v1/marketdata/' + str(channel))

    socketUrlList.append('wss://api.gemini.com/v1/order/events')
    return socketUrlList

def main(channels=''):
    publicChannels = Utils.prepareChannels_GEMINI()
    publicSchemaList = publicSchema(publicChannels)
    connect_handler(publicSchemaList)
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
