# pylint: disable=E1101

"""
This class holds an instance of an option strategy and it's
components and provides methods to manipulate the option legs
contained within.
"""
import numpy as np
import pandas as pd


class OptionStrategy(object):
    """
    This class holds information regarding an option strategy that is
    being traded. This class will generate a human readable name for
    reference and contain the option legs that make up the option strategy
    """

    def __init__(self, name, symbol, legs, side):
        self.name = name
        self.symbol = symbol
        self.legs = legs
        self.side = side

    def reverse(self):
        """
        Reverse the position of this leg but reversing the sign
        of the quantity amount
        """
        for leg in self.legs:
            leg.reverse()

        if self.side == OrderAction.BUY:
            side = OrderAction.SELL
        else:
            side = OrderAction.BUY

        return OptionStrategy(self.name, self.symbol, self.legs, side)

    def _calls(self, attr):
        """Returns all call options in this strategy"""
        calls = []
        for leg in self.legs:
            if leg.sec_type == SecType.OPT and leg.option.iscall():
                calls.append(getattr(leg.option, attr))

        return calls

    def _puts(self, attr):
        """Returns all put options in this strategy"""
        puts = []
        for leg in self.legs:
            if leg.sec_type == SecType.OPT and leg.option.isput():
                puts.append(getattr(leg.option, attr))

        return puts

    def _stocks(self):
        """Returns the stock in this strategy"""
        for leg in self.legs:
            if leg.sec_type == SecType.STK:
                return leg

    def strike_distance(self):
        """
        Return the maximun absolute distance between all strikes of the same
        option type
        """
        # get all call strikes
        call_strikes = self._calls("strike")
        # get all put strikes
        put_strikes = self._puts("strike")

        calls = np.absolute(np.diff(call_strikes))
        puts = np.absolute(np.diff(put_strikes))

        # if either calls or puts array are empty, just take the max of the non-empty array
        if not puts:
            max_dist = np.max(calls)
        elif not calls:
            max_dist = np.max(puts)
        elif puts and calls:
            max_dist = np.maximum(calls, puts)

        return max_dist

    def get_nat_price(self):
        """
        Calculate the nat price of the option strategy. The nat price is the sum of each
        option leg's bid or ask spread depending on the quantity of the option leg
        """
        nat = 0
        for order_leg in self.legs:
            if order_leg.sec_type == SecType.OPT:
                price = order_leg.option.bid if order_leg.quantity < 0 else order_leg.option.ask
                # TODO: should factor out the 100 multiplier to either at database or elsewhere
                nat += price * order_leg.quantity

        return round(abs(nat), 2)

    def get_mid_price(self):
        """
        Calculate the mid price of the option strategy. The mid price is the sum of each
        option's mark price multiplied by the quantity of the option leg.
        """
        mid = 0
        for order_leg in self.legs:
            if order_leg.sec_type == SecType.OPT:
                option = order_leg.option
                price = np.mean([option.bid, option.ask])
                # TODO: should factor out the 100 multiplier to either at database or elsewhere
                mid += price * order_leg.quantity

        return round(abs(mid), 2)

    def legs_to_df(self):
        """
        Convert the option legs array for this strategy to a dataframe.
        Stock legs are not converted
        """
        option_legs = []

        for leg in self.legs:
            if leg.sec_type == SecType.OPT:
                option_legs.append(leg.contract.__dict__)

        option_df = pd.DataFrame(option_legs)
        return option_df
