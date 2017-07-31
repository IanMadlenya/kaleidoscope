from .base import Sizer


class DollarAmountSizer(Sizer):
    def __init__(self, account, amount):
        self.amount = amount
        super().__init__(account)

    def order_size(self, signal):
        pass


class FixedQuantitySizer(Sizer):
    def __init__(self, account, quantity=10):
        self.quantity = quantity
        super().__init__(account)

    def order_size(self, order, action):
        """
        Return default quantity
        :param order:
        :param action:
        :return:
        """
        return self.quantity * action.value
