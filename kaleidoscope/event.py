from enum import Enum
from datetime import datetime

EventType = Enum("EventType", "DATA ORDER FILL")


class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    pass


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

    def __init__(self, date, order):
        """
        Initialises the OrderEvent.

        :param order:
        :param action:
        :param order_type:
        :param tif:
        :param quantity:
        """
        self.type = EventType.ORDER
        self.date = date
        self.order = order

        self.print_event()

    def print_event(self):
        """
        Outputs the values within the OrderEvent.
        """
        print(f"Order Event on: {self.date}: {self.order}")


class FillEvent(Event):
    """
    Encapsulates the notion of a filled order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(self, date, order, ticket,
                 action, quantity, cost, margin, commission
                 ):
        """
         Initialises the FillEvent object.

        :param date:
        :param order:
        :param ticket:
        :param action:
        :param quantity:
        :param price:
        :param commission:
        """
        self.type = EventType.FILL
        self.date = date
        self.order = order
        self.mark = self.order.mark
        self.ticket = ticket
        self.action = action
        self.quantity = quantity
        self.cost = cost
        self.margin = margin
        self.commission = commission

        self.print_event()

    def print_event(self):
        """
        Outputs the values within the OrderEvent.
        """
        t = self.ticket
        d = self.date
        a = self.action
        q = self.quantity
        m = self.mark
        n = self.order.name
        s = self.order.underlying_symbol

        exps = self.order.expirations
        p_e = [datetime.strptime(exp, "%Y-%m-%d") for exp in exps]
        e = "".join('%s/' % p.strftime('%d %b %y') for p in p_e)[0: -1]

        sts = self.order.strikes
        st = "".join('%s/' % '{0:g}'.format(st) for st in sts)[0: -1]

        print(f"Fill Event #{t} on: {d}: {q} {a} @{m:.2f} {n} {s} {e} {st}")
