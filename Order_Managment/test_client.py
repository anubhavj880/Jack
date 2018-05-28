from ccex import client as c

#ob = c.Client()
#print(ob.market_data_pair('DASH-BTC'))
#print(ob.coinnames())
#print(ob.pairs())
#print(ob.prices())
#print(ob.volume_last24hrs('btc'))
#print(ob.getmarkets())
#print(ob.getmarketsummaries())
#print(ob.get_order_book('USD-BTC','both',10))
#print(ob.getfullorderbook(5))
#print(ob.getmarkethistory('USD-BTC',5))
#print(ob.getfullmarkethistory(3))
#print(ob.getbalancedistribution('grc'))


#oe = c.TradeClient()
#print(oe.get_balance('BTC'))
#print(oe.get_all_balances())
#print(oe.get_openorders())
#print(oe.get_orderhistory())
#print(oe.get_tradehistory('GRC-BTC'))



from CCEX_OM import CCEX_OM as om
import json


class y:
    def __init__(self, symbol, qty, price, side):
        self.symbol = symbol
        self.qty = qty
        self.price = price
        self.side = side

obj = om.OM()
#a = y('grc-btc',100, 0.00001, 'buy')
#print(obj.create(a))

datastore = json.loads("{\r\n\"success\": true,\r\n\"message\": \"\",\r\n\"result\": {\r\n\"uuid\": \"8228499\"\r\n}\r\n}")
print(obj.isActive(datastore))

#print(obj.cxl('8228499'))

cancelmess = json.loads('{\r\n\"success\" : true,\r\n\"message\" : \"\",\r\n\"result\" : null\r\n}')
#print(obj.isCxlSuccess(cancelmess))

#print(obj.isCxlAllSuccess())

class x:
    def __init__(self, odid):
        self.odid = odid


#b = x(8228499)
#print(obj.checkOrderStatus(b))


#print(obj.getInitActiveOrders())

#print(obj.getInitActiveOrders())

print(obj.get_balance())


















































