from kaleidoscope.options.option_strategy import OptionStrategy


class Order(object):
    def __init__(self, date, order_strat, action,
                 quantity, order_type, tif, limit_price,
                 commission, margin
                 ):

        # Order ticket, to be created by broker
        self.ticket = None

        if isinstance(order_strat, OptionStrategy):
            self.name = order_strat.__str__()

        self.order_strat = order_strat
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
        self.commissions = commission(self.order_strat.legs)

        self.total_cost = self.order_cost + self.commissions
        self.margin = margin(self.order_strat, self.action) * abs(self.quantity) * 100

    def update(self, quotes):
        """
        Update the order's symbols with current market values

        :params quotes: DataFrame of updated option symbols from broker
        """
        for leg in self.order_strat.legs:
            quote = quotes[quotes['symbol'] == leg['contract'].symbol].to_dict(orient='records')[0]
            leg['contract'].update(quote)

        # update the mark value of the order
        self.mark = self.order_strat.calc_mark()

    def expiring(self, date):
        """
        Return true if any legs of this order is expiring, else return false
        :return: Boolean
        """
        for leg in self.order_strat.legs:
            if leg['contract'].get_expiration() == date:
                return True

        return False

    def __str__(self):
        if self.executed_price == 0 and self.limit_price is None:
            price = "MKT"
        elif self.executed_price == 0 and self.limit_price is not None:
            price = '@%s' % '{:.2f}'.format(self.limit_price)
        else:
            price = '@%s' % '{:.2f}'.format(self.executed_price)

        return f"{self.quantity} {self.action.name} {price} {self.name}"
