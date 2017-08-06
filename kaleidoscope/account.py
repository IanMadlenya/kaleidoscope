from kaleidoscope.position import Position


class Account(object):

    def __init__(self, cash=10000):

        # initialize account balances
        self.initial_cash = cash
        self.cash = cash
        self.net_liquidating_value = cash
        self.option_buying_power = cash

        self.comm_agg = 0
        self.positions = list()

    def check_expiration(self, date):
        """
        Remove positions expiring OTM or close positions at market price
        for positions expiring ITM.

        :param date: Current date, to check against positions' expiration date
        :return: A list of expiring positions
        """

        # find non-expired positions
        active = list()
        expired = False

        for p in self.positions:
            if date != p.get_expiration():
                active.append(p)
            else:
                self.cash += p.net_liquidating_value
                expired = True

        self.positions = active
        return expired

    def set_cash(self, amt):
        """
        Set the cash balance of this broker account instance

        :param amt: The cash amount to set for the trading account
        :return: None
        """
        self.cash = amt

    def process_order(self, order):
        """
        Append the new options positions to the account.

        :param order: order to process
        :return: None
        """
        self.cash -= order.total_cost
        self.comm_agg += order.commissions

        # for each order leg, add the position into the position list
        # if symbols duplicate, merge the quantities together.
        for leg in order.order_strat.legs:
            position = Position(leg['contract'], leg['quantity'] * order.quantity)
            if position not in self.positions:
                # this position does not exist yet, add it
                self.positions.append(position)
            else:
                # update the quantity of the position if already exist
                idx = self.positions.index(position)
                self.positions[idx] = self.positions[idx] + position

                # if the merged quantities of a position equals 0, remove it
                if self.positions[idx].quantity == 0:
                    del self.positions[idx]

    def update(self, quotes):
        """
        Update the account's position's values with latest quotes

        :param quotes: DataFrame containing option chains
        :return: None
        """

        # update all positions held in the account with latest quotes
        for position in self.positions:
            position.update(quotes)

        # update account's net liquidating value
        self.net_liquidating_value = self.calc_net_liquidating_value()

    def calc_net_liquidating_value(self):
        """
        Calculates the account's net liquidating value which is defined:
        Net Liquidating Value = Cash + Market Value of Long - Market Value of Shorts

        :return: None
        """

        return self.cash + sum(p.net_liquidating_value for p in self.positions)
