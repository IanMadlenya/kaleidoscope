from kaleidoscope.event import FillEvent, RejectedEvent
from kaleidoscope.globals import OrderType, OrderStatus, OrderAction
from kaleidoscope.order import Order
from .base import BaseBroker


class DefaultBroker(BaseBroker):
    def __init__(self, datafeed, comm_model, margin_model, queue):
        super().__init__(datafeed, comm_model, margin_model, queue)

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

        # create an order object to keep track of it
        order = Order(event.date, event.strategy, event.action,
                      event.quantity, event.order_type,
                      event.order_tif, event.limit_price)

        # calculate the order's commissions
        order.commissions = self.comm_model.get_commissions(order.strategy)

        # calculate the order's margin
        order.margin = self.margin_model.get_init_margin(order.strategy, order.action)

        # test if order execution is possible
        if self._executable(order):
            # create a ticket for this order
            order.ticket = self.generate_ticket()

            # execute this order if possible
            self.execute_order(order)

            # add the order to the order list to keep track
            self.order_list[order.ticket] = order
        else:
            order.status = OrderStatus.REJECTED
            evt = RejectedEvent(self.current_date, order)
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



