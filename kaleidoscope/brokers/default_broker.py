import collections
import random

from kaleidoscope.event import FillEvent
from kaleidoscope.globals import OrderType, OrderStatus, OrderAction
from .base import BaseBroker


class DefaultBroker(BaseBroker):
    def __init__(self, datafeed, commissions, margin, queue):

        self.order_list = collections.OrderedDict()
        self.quotes = None

        super().__init__(datafeed, commissions, margin, queue)

    def positions_total(self):
        return len(self.account.positions)

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

    def _execute_order(self, order):
        """
        Test execution of an order based on available cash and buying power

        :param order:
        :return:
        """

        # Check that we have enough option buying power/cash to carry out the order
        if ((self.account.cash - order.total_cost > 0) and
                    (self.account.option_buying_power - order.margin) > 0):
            # reduce buying power as the order is accepted
            self.account.option_buying_power -= order.margin
            return True
        else:
            return False

    def process_order(self, event):
        """
        Process a new order received from an order event.
        """
        self.execute_order(event.order)

        # add the order to the order list to keep track
        self.order_list[event.order.ticket] = event.order

    def execute_order(self, order):
        """
        Execute the order event without any additional logic as
        this is a basic implementation.

        :param event: The order event created by strategy
        :return: None
        """

        if self._execute_order(order):
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
        else:
            order.status = OrderStatus.REJECTED
            print(f"REJECTED ORDER #{order.ticket}: Not enough buying power to execute order!")

    def update_data(self, quotes):
        """
        Using fresh quotes from data source, update current values
        for pending orders and positions held in accounts.

        :param quotes: fresh quotes in DataFrame format
        """
        quotes = quotes.fetch()

        # update the broker's working orders' option prices
        for order in self.order_list:
            if self.order_list[order].status == OrderStatus.WORKING:
                order.update(self.quotes)

        # update the account's position values
        self.account.update(quotes)

        print(f"Cash: {self.account.cash:0.2f}"
              f" Net Liquidating Value: {self.account.net_liquidating_value:0.2f}"
              f" Option Buying Power: {self.account.option_buying_power:0.2f}"
              f" Commissions: {self.account.comm_agg:0.2f}"
              )


    def generate_ticket(self):
        """
        Returns a ticket number based on the current orders already
        processed by the broker.

        """
        return random.randint(100000, 999999)
