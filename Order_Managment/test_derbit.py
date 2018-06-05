from DERIBIT_OM import DERIBIT_OM as om
import json

class y:
    def __init__(self, symbol, qty, price, side):
        self.symbol = symbol
        self.qty = qty
        self.price = price
        self.side = side

obj = om.OM()
a = y('BTC-29JUN18',1, 6000, 'buy')
#print(obj.create(a))


place_order = '''{  
   "usIn":1527869732581145,
   "usOut":1527869732581824,
   "usDiff":679,
   "success":true,
   "testnet":false,
   "result":{  
      "order":{  
         "orderId":4676369783,
         "type":"limit",
         "instrument":"BTC-29JUN18",
         "direction":"buy",
         "price":6000.0,
         "label":"",
         "quantity":1,
         "filledQuantity":0,
         "avgPrice":0.0,
         "commission":0.0,
         "created":1527869732581,
         "lastUpdate":1527869732581,
         "state":"open",
         "postOnly":false,
         "api":true,
         "max_show":1,
         "adv":false
      },
      "trades":[  

      ]
   },
   "message":""
}'''

#print(obj.isActive(json.loads(place_order)))


class x:
    def __init__(self, odid):
        self.odid = odid


b = x("4677333909")
#print(obj.checkOrderStatus(b))

print(obj.cxl('4739629142'))


data = '''{  
   "success":true,
   "testnet":false,
   "order":{  
      "orderId":4676369783,
      "type":"limit",
      "instrument":"BTC-29JUN18",
      "direction":"buy",
      "price":6000.0,
      "label":"",
      "quantity":1,
      "filledQuantity":0,
      "avgPrice":0.0,
      "commission":0.0,
      "created":1527869732581,
      "lastUpdate":1527870033729,
      "state":"cancelled",
      "postOnly":false,
      "api":true,
      "max_show":1,
      "adv":false
   },
   "usIn":1527870033728988,
   "usOut":1527870033729562,
   "message":"",
   "result":null
}'''


#print(obj.isCxlSuccess(json.loads(data)))

#print(obj.isCxlAllSuccess())





