from enum import Enum

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

    def __init__(self, date, order):
        """
        The OrderEvent created by strategy class.

        :param date: Date of event
        :param order: Order for the event
        """
        self.type = EventType.ORDER
        self.date = date
        self.order = order

        self.print_event()

    def print_event(self):
        """
        Outputs the values within the OrderEvent.
        """
        print(f"ORDER #{self.order.ticket} OPENED ON {self.date}: {self.order}")


class FillEvent(Event):
    def __init__(self, date, order):
        """
        Initialises the FillEvent object created by broker.

        :param date: Date of event
        :param order: Order for the event
        """
        self.type = EventType.FILL
        self.date = date
        self.order = order
        self.mark = order.mark
        self.ticket = order.ticket
        self.action = order.action
        self.quantity = order.quantity
        self.cost = order.final_cost
        self.margin = order.order_margin
        self.commission = order.commissions

        self.print_event()

    def print_event(self):
        """
        Outputs the values within the OrderEvent.
        """
        print(f"ORDER #{self.order.ticket} FILLED ON {self.date}: {self.order}")
