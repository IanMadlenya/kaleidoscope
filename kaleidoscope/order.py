"""
Module doc string
"""
from bonzai.core.globals import OrderStatus
from bonzai.core.options.option_strategy import OptionStrategy


class Order(object):
    """
    Class which holds creation/execution data and type of oder.

    The order may have the following status:

      - Submitted: sent to the broker and awaiting confirmation
      - Filled: fully executed
      - Cancelled: canceled by the user
      - Working: accepted by broker, waiting for execution
      - Expired: expired
      - Rejected: Rejected by the broker

    Member Attributes:
      - detail: human readable representation of the order
      - ticket: unique order identifier
      - created: date the order was created
      - executed: date the order was executed
      - quantity: quantity of the order
      - tif: Time in force indicates how long an order will remain
             active before it is executed or expires.
      - status: status of the order
      - order_type: the execution type of the order, either Market or Limit
      - order_side: the position side of the order, either buy or sell
      - limit_price: the limit price of the order if applicable
      - commission: the calculated commission of the order

    Order pricing types supported by thinkorswim
        LIMIT - default order type for all single option, spread and stock orders.
                The limit price for buy orders is placed below the current market price.
                The limit price for sell orders is placed above the current market price.
                Limit orders will be filled at the limit price or better,
                but are not guaranteed a fill.

        MARKET - (also known as "not held") - order used to guarantee an execution,
                 but not guarantee a price or time of execution. The risk of market
                 orders is that you have no control over what the execution price is.
                 We strongly suggest you avoid using them with options, especially option spreads.

    """

    def __init__(self, ticket, date, order_strat, action,
                 quantity, order_type, tif, limit_price
                 ):

        # Order specific properties
        self.order_strat = order_strat

        if isinstance(self.order_strat, OptionStrategy):
            self.symbol = order_strat.symbol
            self.name = order_strat.name
        else:
            self.symbol = order_strat
            self.name = self.symbol

        self.ticket = ticket
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
