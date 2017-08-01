from kaleidoscope.globals import OrderStatus
from kaleidoscope.options.option_strategy import OptionStrategy


class Order(object):
    def __init__(self, date, order_strat, action,
                 quantity, order_type, tif, limit_price
                 ):

        # Order specific properties
        self.order_strat = order_strat

        if isinstance(self.order_strat, OptionStrategy):
            self.underlying_symbol = order_strat.underlying_symbol
            self.name = order_strat.name

        self.date = date
        self.executed_price = None
        self.status = OrderStatus.CREATED
        self.quantity = quantity
        self.action = action.name
        self.limit_price = limit_price
        self.order_type = order_type
        self.tif = tif

        self.mark = order_strat.mark

    def __str__(self):
        price = '@%s' % '{:.2f}'.format(self.limit_price) \
            if self.limit_price is not None else "MKT"

        return f"{self.quantity} {self.action} {price} {self.order_strat}"
