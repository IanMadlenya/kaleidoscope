from kaleidoscope.globals import OrderStatus
from kaleidoscope.options.option_strategy import OptionStrategy


class Order(object):
    def __init__(self, date, order_strat, action,
                 quantity, order_type, tif, limit_price
                 ):

        # Order specific properties
        self.order_strat = order_strat

        if isinstance(self.order_strat, OptionStrategy):
            self.symbol = order_strat.symbol
            self.name = order_strat.name

        self.date = date
        self.executed_price = None
        self.status = OrderStatus.CREATED
        self.quantity = quantity
        self.action = action
        self.limit_price = limit_price
        self.order_type = order_type
        self.tif = tif

        # Pricing specific properties
        self.nat_price = None
        self.mid_price = None
        self.executed_price = None

        # broker specific properties
        self.commission = None
        self.margin = None
        self.cost_of_trade = None

        self.update_price()

    def update_price(self):
        """
        Calculate this order's price based on order action and strategy.
        If current price is passed in, calculate order price based on the
        current price instead
        """
        if isinstance(self.order_strat, OptionStrategy):
            self.nat_price = self.order_strat.get_nat_price()
            self.mid_price = self.order_strat.get_mid_price()

    def calculate_margin(self, price):
        """ calculate the margin of this order """
        if isinstance(self.order_strat, OptionStrategy):
            if len(self.order_strat.legs) == 1:
                margin = (price * self.quantity * 100)
            else:
                margin = self.order_strat.strike_distance() * \
                         self.quantity * 100 * self.action.value

        self.margin = margin
        return margin

    def calculate_cost_of_trade(self, price, commission):
        """ Calculate the cost of this order including commissions """
        cost_of_trade = (price * self.quantity * 100) + commission
        self.cost_of_trade = cost_of_trade
        return cost_of_trade

    def __str__(self):
        return "Ticket: %s, Status: %s, Executed Price: %s, Current Price: %s" % \
               (self.ticket, self.status, self.executed_price, self.nat_price)
