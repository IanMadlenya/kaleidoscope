# pylint: disable=E1101
import numpy as np
import pandas as pd

from kaleidoscope.options.order_leg import OptionLeg, StockLeg
from kaleidoscope.globals import SecType, OrderType
from kaleidoscope.options.option_query import OptionQuery


class OptionStrategy(object):
    """
    This class holds information regarding an option strategy that is
    being traded. This class will generate a human readable name for
    reference and contain the option legs that make up the option strategy
    """

    def __init__(self, chains):
        """
        This class holds an instance of an option strategy and it's
        components and provides methods to manipulate the option legs
        contained within.

        :params: chains: Dataframe containing shifted columns representing an option leg
        """
        self.chains = chains
        self.legs = list()

    def _map(self, spread):
        """
        Map the dataframe columns to its corresponding option leg
        
        :param chains: Dataframe containing columns of option legs
        :return: 
        """
        pass

    def parse_strategy(strat_sym):
        """
        Parse the strategy symbols which is made up of multiple option symbols
        :param strat_sym: option symbol representing the option strategy, eg. VXX160219C00035000
        :return:
        """
        pass

    def mark_nearest(self, price):
        """
        Returns a
        :param price:
        :return:
        """
        spread = OptionQuery(self.chains).closest('spread_mark', price)
        return self._map(spread)

    def mark_nearest_above(self, price):
        pass

    def mark_nearest_below(self, price):
        pass

    def fetch(self):
        return self.chains
