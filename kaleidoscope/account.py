class Account(object):
    def __init__(self, cash=10000):
        self.cash = cash

    def on_fill(self, event):
        pass

    def update_account(self, event):
        pass

    def set_cash(self, amt):
        """
        Set the cash balance of this broker account instance

        :param amt: The cash amount to set for the trading account
        :return:
        """
        self.cash = amt
