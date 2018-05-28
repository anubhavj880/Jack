class Order():
    def __init__(self, exchCode, sym_, _sym, orderType, price, side, qty, stopPrice=''):
        self.odid = None
        self.status = None
        self.tempOdid = None
        self.sym_ = sym_
        self._sym = _sym
        self.symbol = sym_ + _sym
        self.exchCode = exchCode.upper()
        self.orderType = orderType
        self.price = price
        self.fair = -1.0
        self.side = side.upper()
        self.sign = '+' if self.side == 'BUY' else '-' # for logging only
        # self.order_type_id = None # Only for Coinigy
        # self.price_type_id = None # Only for Coinigy
        self.qty = qty
        self.stop_price = stopPrice
        self.orderExposure = -1.0
        # timestamp
        self.createTs = -1.0
        self.activeTs = -1.0
        self.cxlTs = -1.0
        self.cxledTs = -1.0
        self.filledTs = -1.0
        # for pricing
        self.eq = -1.0
        # for order handling
        self.nbFillQ = 0
        self.nbMissingAck = 0
        self.nbExtRej = 0
        self.nbNone = 0
        self.nbFalseActive = 0
