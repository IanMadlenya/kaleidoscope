from kaleidoscope.options.option_strategy import OptionStrategy


class Order(object):
    def __init__(self, ticket, date, order_strat, action,
                 quantity, order_type, tif, limit_price
                 ):
        # Order ticket, to be created by broker
        self.ticket = ticket

        if isinstance(order_strat, OptionStrategy):
            self.order_strat = order_strat
            self.underlying_symbol = order_strat.underlying_symbol
            self.name = order_strat.name
            self.contracts = order_strat.legs

        self.date = date
        self.executed_price = 0
        self.status = None
        self.quantity = quantity
        self.action = action
        self.limit_price = limit_price
        self.order_type = order_type
        self.tif = tif

        # updated by broker
        self.mark = order_strat.mark
        self.order_cost = self.mark * self.quantity * 100
        self.commissions = 0
        self.final_cost = 0
        self.order_margin = 0

    def update_costs(self, comm, margin):
        self.commissions = comm
        self.order_margin = margin
        self.final_cost = self.order_cost + self.commissions

    def __str__(self):

        if self.executed_price == 0 and self.limit_price is None:
            price = "MKT"
        elif self.executed_price == 0 and self.limit_price is not None:
            price = '@%s' % '{:.2f}'.format(self.limit_price)
        else:
            price = '@%s' % '{:.2f}'.format(self.executed_price)

        return f"{self.quantity} {self.action.name} {price} {self.order_strat}"
