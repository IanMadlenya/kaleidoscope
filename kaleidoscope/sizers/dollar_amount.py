from .base import BaseSizer


class DollarAmountSizer(BaseSizer):
    def __init__(self, account, amount):
        self.amount = amount
        super().__init__(account)

    def order_size(self, order, action):
        pass
