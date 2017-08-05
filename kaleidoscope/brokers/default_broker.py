import collections
import random

from kaleidoscope.event import FillEvent, RejectedEvent
from kaleidoscope.globals import OrderType, OrderStatus, OrderAction
from .base import BaseBroker


class DefaultBroker(BaseBroker):
    def __init__(self, datafeed, commissions, margin, queue):

        self.order_list = collections.OrderedDict()
        self.quotes = None

        super().__init__(datafeed, commissions, margin, queue)

    def positions_total(self):
        return len(self.account.positions)

    def working_total(self):
        return sum(1 for order in self.order_list if self.order_list[order].status == OrderStatus.WORKING)

    def _execute(self, order):
        """
        Execute the order, set status and create fill event.

        :param order:
        :return:
        """
        order.status = OrderStatus.FILLED
        order.executed_price = order.mark

        # update account positions
        self.account.process_order(order)

        event = FillEvent(self.current_date, order)
        self.queue.put(event)

    def _executable(self, order):
        """
        Test execution of an order based on available cash and buying power.
        Check that we have enough option buying power/cash to carry out the order

        :param order: The order to test the executable conditions for
        :return: Boolean
        """
        return ((self.account.cash - order.total_cost > 0) and
                (self.account.option_buying_power - order.margin) > 0)

    def process_order(self, event):
        """
        Process a new order received from an order event.
        """

        if self._executable(event.order):
            # reduce buying power as the order is accepted
            self.account.option_buying_power -= event.order.margin
            self.execute_order(event.order)

            # add the order to the order list to keep track
            self.order_list[event.order.ticket] = event.order
        else:
            event.order.status = OrderStatus.REJECTED
            evt = RejectedEvent(self.current_date, event.order)
            self.queue.put(evt)

    def execute_order(self, order):
        """
        Execute the order event without any additional logic as
        this is a basic implementation.

        :param order: The order created by strategy to execute
        :return: None
        """

        # set the order status, as it is accepted
        order.status = OrderStatus.WORKING

        if order.order_type == OrderType.MKT:
            # this is a market order, execute it immediately at current mark price
            self._execute(order)
        elif order.order_type == OrderType.LMT:
            # this is a limit order, check the limits and execute if able
            if ((order.action == OrderAction.BUY and order.limit_price >= order.mark) or
                    (order.action == OrderAction.SELL and order.limit_price <= order.mark)):
                # if market conditions meet limit requirements execute it
                self._execute(order)

    def update_data(self, quotes):
        """
        Using fresh quotes from data source, update current values
        for pending orders and positions held in accounts.

        :param quotes: fresh quotes in DataFrame format
        """
        self.quotes = quotes.fetch()

        # update the broker's working orders' option prices
        for order_item in self.order_list:
            order = self.order_list[order_item]
            if order.status == OrderStatus.WORKING:
                order.update(self.quotes)
                self.execute_order(order)

        # update the account's position values
        self.account.update(self.quotes)

        # print(f"Cash: {self.account.cash:0.2f}"
        #       f" Net Liquidating Value: {self.account.net_liquidating_value:0.2f}"
        #       f" Option Buying Power: {self.account.option_buying_power:0.2f}"
        #       f" Commissions: {self.account.comm_agg:0.2f}"
        #       )

    def generate_ticket(self):
        """
        Returns a ticket number based on the current orders already
        processed by the broker.

        """
        return random.randint(100000, 999999)
