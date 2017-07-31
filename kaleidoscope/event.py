from enum import Enum
from datetime import datetime

EventType = Enum("EventType", "DATA ORDER FILL")


class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """

    @property
    def typename(self):
        return self.event_type.name


class DataEvent(Event):
    """
    Handles the event of receiving a new market
    open-high-low-close-volume bar, as would be generated
    via common data providers such as Yahoo Finance.
    """

    def __init__(self, date, quotes):
        """

        :param date: The date of the quotes
        :param quotes: A DataFrame containing option chains for all
                       subscribed symbols
        """
        self.type = EventType.DATA
        self.date = date
        self.quotes = quotes


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a ticker (e.g. SPX), action (BOT or SLD)
    and quantity.
    """

    def __init__(self, ticket, date, order, action, quantity):
        """
        Initialises the OrderEvent.

        :param order:
        :param action:
        :param order_type:
        :param tif:
        :param quantity:
        """
        self.ticket = ticket
        self.type = EventType.ORDER
        self.date = date
        self.order = order
        self.action = action
        self.quantity = quantity

        self.print_order()

    def print_order(self):
        """
        Outputs the values within the OrderEvent.
        """
        t = self.ticket
        d = self.date
        a = self.action.name
        q = self.quantity
        m = self.order.mark
        n = self.order.name
        s = self.order.underlying_symbol

        exps = self.order.expirations
        p_e = [datetime.strptime(exp, "%Y-%m-%d") for exp in exps]
        e = "".join('%s/' % p.strftime('%d %b %y') for p in p_e)[0: -1]

        sts = self.order.strikes
        st = "".join('%s/' % '{0:g}'.format(st) for st in sts)[0: -1]

        print(f"Date: {d} Order #{t}: {a} {q} @ {m:.2f} {n} {s} {e} {st}")


class FillEvent(Event):
    """
    Encapsulates the notion of a filled order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(self, date, symbol,
                 action, quantity, price,
                 commission
                 ):
        """
        Initialises the FillEvent object.

        timestamp - The timestamp when the order was filled.
        ticker - The ticker symbol, e.g. 'GOOG'.
        action - 'BOT' (for long) or 'SLD' (for short).
        quantity - The filled quantity.
        exchange - The exchange where the order was filled.
        price - The price at which the trade was filled
        commission - The brokerage commission for carrying out the trade.
        """
        self.type = EventType.FILL
        self.date = date
        self.ticker = symbol
        self.action = action
        self.quantity = quantity
        self.price = price
        self.commission = commission
