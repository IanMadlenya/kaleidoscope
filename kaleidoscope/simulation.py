import datetime
import os

import pandas as pd
from pandas.core.base import PandasObject

import kaleidoscope.globals as gb


class Simulation(object):
    def __init__(self, prices, strategy):
        """
        Simulation is a class that simulates trading mechanics on a specific
        set of options for each expiration cycle. This class
        """
        self.prices = prices

        # normalize option prices and sort into dict of expiry dates
        self._normalize()

    def _normalize(self):
        """
        Takes a dataframe of option prices by quote dates and expiries and
        constructs a dictionary of expiries and option spread prices by quote dates
        :return: None
        """
        expiries = self.prices['expiration'].unique()
        dates = [pd.to_datetime(str(t)).strftime('%Y-%m-%d') for t in expiries]
        print(dates)


def simulate(prices, strategy):
    """
    This method creates a new dataframe that contains all option spreads
    that expired worthless.

    :param prices: Dataframe to find all expired spreads on expiration date. This
                      dataframe should have been processed by an OptionStrategy method
                      and contains prices for options spreads.
    :param strategy: strategy to apply for options chains in each expiation cycle
    :return: prices with all options that expired worthless (or close to worthless)
    """

    if isinstance(prices, pd.DataFrame):
        return Simulation(prices, strategy)
    else:
        raise NotImplementedError('Unsupported type')


def output_to_csv(prices):
    """
    Thin wrapper method to output this dataframe to csv file
    :param prices: This is the dataframe itself
    :return:
    """
    filename = '%s_%s' % (prices.name, datetime.date.today())
    csv_dir = os.path.join(os.sep, gb.PROJECT_DIR, gb.OUTPUT_DIR, filename + ".csv")
    prices.to_csv(csv_dir)


def extend_pandas():
    """
    Extends pandas' PandasObject (Series, Series,
    DataFrame) with some functions defined in this file.
    This facilitates common functional composition used in quant
    finance.
    Ex:
        prices.to_returns().dropna().calc_clusters()
        (where prices would be a DataFrame)
    """
    PandasObject.simulate = simulate
    PandasObject.output_to_csv = output_to_csv
