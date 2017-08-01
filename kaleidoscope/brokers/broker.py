from kaleidoscope.event import FillEvent
from .base import Broker


class DefaultBroker(Broker):
    def __init__(self, datafeed, comm, margin, queue):
        super().__init__(datafeed, comm, margin, queue)

    def execute_order(self, event):
        """
        Execute the order event without any additional logic as
        this is a basic implementation.

        :param event: The order event created by strategy
        :return: None
        """
        # Check that we have enough option buying power/cash to carry out the order
        order_cost = event.order.mark * event.quantity * 100
        commissions = self.comm.get_commissions(event.order, event.quantity)
        final_cost = order_cost + commissions

        order_margin = abs(self.margin.get_margin(event.order, event.action) * event.quantity * 100)

        if self.account.cash - final_cost > 0 and self.account.option_buying_power - order_margin > 0:
            # create a fill event and place it in the queue
            event = FillEvent(self.current_date, event.order,
                              event.ticket, event.action,
                              event.quantity, final_cost,
                              order_margin, commissions)
            self.queue.put(event)
