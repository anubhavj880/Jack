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
print(obj.create(a))