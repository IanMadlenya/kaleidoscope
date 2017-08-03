import collections
import random

from kaleidoscope.event import FillEvent
from kaleidoscope.globals import OrderType, OrderStatus, OrderAction
from .base import BaseBroker


class DefaultBroker(BaseBroker):
    def __init__(self, datafeed, commissions, margin, queue):

        self.order_list = collections.OrderedDict()

        super().__init__(datafeed, commissions, margin, queue)

    def _execute(self, order):
        """
        Execute the order, set status and create fill event.

        :param order:
        :return:
        """
        order.status = OrderStatus.FILLED
        order.executed_price = order.mark

        event = FillEvent(self.current_date, order)
        self.queue.put(event)

    def _execute_order(self, order):
        """
        Executes an order based on order type

        :param order:
        :return:
        """
        if order.order_type == OrderType.MKT:
            # this is a market order, execute it immediately at current mark price
            self._execute(order)
        elif order.order_type == OrderType.LMT:
            # this is a limit order, check the limits and execute if able
            if ((order.action == OrderAction.BUY and order.limit_price >= order.mark) or
                    (order.action == OrderAction.SELL and order.limit_price <= order.mark)):
                # if market conditions meet limit requirements execute it
                self._execute(order)

    def execute_order(self, event):
        """
        Execute the order event without any additional logic as
        this is a basic implementation.

        :param event: The order event created by strategy
        :return: None
        """
        # save some typing
        order = event.order
        strategy = order.order_strat
        quantity = order.quantity
        action = order.action

        # calculate cost and margin requirements for the order
        commissions = self.commissions(strategy, quantity)
        order_margin = abs(self.margin(strategy, action) * quantity * 100)
        order.update_costs(commissions, order_margin)

        # Check that we have enough option buying power/cash to carry out the order
        if ((self.account.cash - order.final_cost > 0) and
                    (self.account.option_buying_power - order.order_margin) > 0):
            # set the order status, as it is accepted
            order.status = OrderStatus.WORKING
            self._execute_order(order)
        else:
            order.status = OrderStatus.REJECTED

        # add the order to the order list to keep track
        self.order_list[order.ticket] = order

    def generate_ticket(self):
        return random.randint(100000, 999999)
