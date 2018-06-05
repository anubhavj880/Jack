from GEMINI_OM import GEMINI_OM as om
import json


class y:
    def __init__(self, symbol, qty, price, side):
        self.symbol = symbol
        self.qty = qty
        self.price = price
        self.side = side

obj = om.OM()
a = y('BTCUSD',0.00001, 0.01, 'buy')
print(obj.create(a))

data = '''{
    "order_id": "22333",
    "client_order_id": "20150102-4738721",
    "symbol": "btcusd",
    "price": "34.23",
    "avg_execution_price": "34.24",
    "side": "buy",
    "type": "exchange limit",
    "timestamp": "128938491",
    "timestampms": 128938491234,
    "is_live": true,
    "is_cancelled": false,
    "options": ["maker-or-cancel"], 
    "executed_amount": "12.11",
    "remaining_amount": "16.22",
    "original_amount": "28.33"
}'''

datastore = json.loads(data)
#print(obj.isActive(datastore))

#print(obj.cxl('3825292680'))


cxl_data = '''{
    "order_id":"330429304",
    "id":"330429304",
    "symbol":"btcusd",
    "exchange":"gemini",
    "avg_execution_price":
    "0.00","side":"sell","type":
    "exchange limit",
    "timestamp":"1519853415",
    "timestampms":1519853415234,
    "is_live":false,
    "is_cancelled":true,
    "is_hidden":false,"was_forced":false,
    "executed_amount":"0",
    "remaining_amount":"0.001",
    "options":["maker-or-cancel"],
    "price":"50000.00",
    "original_amount":"0.001"
}
'''

cancelmess = json.loads(cxl_data)
#print(obj.isCxlSuccess(cancelmess))

#print(obj.isCxlAllSuccess())




class x:
    def __init__(self, odid):
        self.odid = odid


b = x(8228499)
#print(obj.checkOrderStatus(b))



data = '''{
  "order_id" : "44375901",
  "id" : "44375901",
  "symbol" : "btcusd",
  "exchange" : "gemini",
  "avg_execution_price" : "400.00",
  "side" : "buy",
  "type" : "exchange limit",
  "timestamp" : "1494870642",
  "timestampms" : 1494870642156,
  "is_live" : false,
  "is_cancelled" : false,
  "is_hidden" : false,
  "was_forced" : false,
  "executed_amount" : "3",
  "remaining_amount" : "0",
  "options" : [ ],
  "price" : "400.00",
  "original_amount" : "3"
}'''


#print(obj.readOrderStatus(json.loads(data)))

#print(obj.get_balance())

#print(obj.trading_client.get_ticker('btcusd'))

open_order = '''
[ {
  "order_id" : "44375938",
  "id" : "44375938",
  "symbol" : "ethusd",
  "exchange" : "gemini",
  "avg_execution_price" : "0.00",
  "side" : "buy",
  "type" : "exchange limit",
  "timestamp" : "1494871426",
  "timestampms" : 1494871426935,
  "is_live" : true,
  "is_cancelled" : false,
  "is_hidden" : false,
  "was_forced" : false,
  "executed_amount" : "0",
  "remaining_amount" : "500",
  "options" : [ "maker-or-cancel" ],
  "price" : "30.50",
  "original_amount" : "500"
}, {
  "order_id" : "44375906",
  "id" : "44375906",
  "symbol" : "ethusd",
  "exchange" : "gemini",
  "avg_execution_price" : "31.72",
  "side" : "sell",
  "type" : "exchange limit",
  "timestamp" : "1494871242",
  "timestampms" : 1494871242386,
  "is_live" : true,
  "is_cancelled" : false,
  "is_hidden" : false,
  "was_forced" : false,
  "executed_amount" : "3.152585",
  "remaining_amount" : "3.422815",
  "options" : [ "maker-or-cancel" ],
  "price" : "30.12",
  "original_amount" : "6.5754"
} ]
'''


open = json.loads(open_order)
#print(obj.getInitActiveOrders(open)[0].side)

