import random

from kaleidoscope.event import FillEvent
from .base import BaseBroker


class DefaultBroker(BaseBroker):
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
        strategy = event.order.order_strat
        mark = event.order.mark
        quantity = event.order.quantity
        action = event.order.action

        order_cost = mark * quantity * 100
        commissions = self.comm.get_commissions(strategy, quantity)
        final_cost = order_cost + commissions

        order_margin = abs(self.margin.get_margin(strategy, action) * quantity * 100)

        if self.account.cash - final_cost > 0 and \
                                self.account.option_buying_power - order_margin > 0:
            ticket = self.generate_ticket()

            # create a fill event and place it in the queue
            event = FillEvent(self.current_date, strategy,
                              ticket, action,
                              quantity, final_cost,
                              order_margin, commissions)

            self.queue.put(event)

    def generate_ticket(self):
        return random.randint(100000, 999999)
