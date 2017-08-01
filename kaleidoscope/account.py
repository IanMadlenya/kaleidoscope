class Account(object):
    def __init__(self, cash=10000):
        # initialize account balances
        self.cash = cash
        self.net_liquidating_value = cash
        self.option_buying_power = cash

        # commissions counter
        self.comm_agg = 0

        self.positions = list()

        """
        self.positions = {'VXX160219C00030000': -20, 'VXX160219C00025000': 20}
        
        
        
        
        """

    def set_cash(self, amt):
        """
        Set the cash balance of this broker account instance

        :param amt: The cash amount to set for the trading account
        :return:
        """
        self.cash = amt

    def has_positions(self):
        if len(self.positions) > 0:
            return True
        return False

    def process_order(self, event):
        """
        Append the new options positions to the account.

        :param event:
        :return:
        """
        self.cash -= event.cost
        self.option_buying_power -= event.margin
        self.comm_agg += event.commission

    def update_account(self, event):
        """
        Update the current prices for all options held in the account.

        :param event:
        :return:
        """
        print(f"Cash: {self.cash}"
              f" Net Liquidating Value: {self.net_liquidating_value}"
              f" Option Buying Power: {self.option_buying_power}")
