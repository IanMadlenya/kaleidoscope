from kaleidoscope.position import Position


class Account(object):

    def __init__(self, cash=10000):

        # initialize account balances
        self.cash = cash
        self.net_liquidating_value = cash
        self.option_buying_power = cash

        self.comm_agg = 0
        self.positions = list()

        """
        self.positions = {'VXX160219C00030000': -20, 'VXX160219C00025000': 20}
        """

    def set_cash(self, amt):
        """
        Set the cash balance of this broker account instance

        :param amt: The cash amount to set for the trading account
        :return: None
        """
        self.cash = amt

    def has_positions(self):
        """
        Return true if account has positions otherwise return false
        :return: boolean
        """
        if len(self.positions) > 0:
            return True
        return False

    def process_order(self, event):
        """
        Append the new options positions to the account.

        :param event: Fill event to process
        :return: None
        """
        self.cash -= event.cost
        self.option_buying_power -= event.margin
        self.comm_agg += event.commission

        for leg in event.order.contracts:
            self.positions.append(Position(leg['contract'], leg['quantity']))

        print(f"Cash: {self.cash}"
              f" Net Liquidating Value: {self.net_liquidating_value}"
              f" Option Buying Power: {self.option_buying_power}")

    def update_account(self, event):
        """
        Update the current prices for all options held in the account.

        :param event: Data event to process
        :return: None
        """
        pass
