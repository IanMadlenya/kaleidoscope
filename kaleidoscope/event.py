from enum import Enum
from kaleidoscope.options.option_query import OptionQuery

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
        self.quotes = OptionQuery(quotes)


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a ticker (e.g. SPX), action (BOT or SLD)
    and quantity.
    """

    def __init__(self, symbol, action, quantity):
        """
        Initialises the OrderEvent.

        Parameters:
        ticker - The ticker symbol, e.g. 'GOOG'.
        action - 'BOT' (for long) or 'SLD' (for short).
        quantity - The quantity of shares to transact.
        """
        self.type = EventType.ORDER
        self.symbol = symbol
        self.action = action
        self.quantity = quantity

    def print_order(self):
        """
        Outputs the values within the OrderEvent.
        """
        print(
            "Order: Symbol=%s, Action=%s, Quantity=%s" % (
                self.symbol, self.action, self.quantity
            )
        )


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
