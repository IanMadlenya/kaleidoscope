from kaleidoscope.globals import SecType


class OrderLeg(object):
    def __init__(self, quantity, contract):
        """
        This class is an abstraction of an order leg of an option strategy. It holds the information
        for a single order leg as part of an entire option strategy.
        """

        self.quantity = quantity
        self.contract = contract

    def reverse(self):
        """ reverse the the position by negating the quantity """
        self.quantity *= -1


class OptionLeg(OrderLeg):
    """ Holds information of an option leg """

    def __init__(self, option, quantity):
        self.sec_type = SecType.OPT
        super().__init__(quantity, option)


class StockLeg(OrderLeg):
    """ Holds information of an stock leg """

    def __init__(self, symbol, quantity):
        self.sec_type = SecType.STK
        super().__init__(quantity, symbol)
