from pandas.core.base import PandasObject
import kaleidoscope.globals as gb
import pandas as pd
import os


class PerformanceStats(object):
    def __init__(self, prices):
        """
        PerformanceStats is a convenience class used for the performance
        evaluation of a option price series. It contains various helper functions
        to help with plotting and contains a large amount of descriptive
        statistics.
        """
        self.prices = prices
        self._pivot(self.prices)

        # self._update(self.prices)

    def _pivot(self, obj):
        """
        :param obj:
        :return:
        """

        exp_df = obj[obj['quote_date'] == obj['expiration']]
        # obj = obj.groupby(['quote_date', 'spread_symbol'])

    def _update(self, obj):
        """

        :param prices:
        :return:
        """
        self._calculate(obj)

        st = self._stats()

        self.stats = pd.Series(
            [getattr(self.x[0]) for x in st if x[0] is not None],
            [x[0] for x in st if x[0] is not None]
        )

    def _stats(self):
        stats = [('start', 'Start', 'dt'),
                 ('end', 'End', 'dt'),
                 (None, None, None),
                 ('total_return', 'Total Return', 'p')]

        return stats

    def _calculate(self, obj):
        pass


def calc_stats(prices):
    """
    This method creates a new dataframe that contains all option spreads
    that expired worthless.

    :param prices: Dataframe to find all expired spreads on expiration date. This
                      dataframe should have been processed by an OptionStrategy method
                      and contains prices for options spreads.
    :return: prices with all options that expired worthless (or close to worthless)
    """
    if isinstance(prices, pd.Series):
        return PerformanceStats(prices)
    elif isinstance(prices, pd.DataFrame):
        return PerformanceStats(prices)
        # return GroupStats(*[prices[x] for x in prices.columns])
    else:
        raise NotImplementedError('Unsupported type')


def output_to_csv(prices, name):
    """
    Thin wrapper method to output this dataframe to csv file
    :param prices:
    :param name:
    :return:
    """
    csv_dir = os.path.join(os.sep, gb.PROJECT_DIR, gb.OUTPUT_DIR, name + ".csv")
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
    PandasObject.calc_stats = calc_stats
    PandasObject.output_to_csv = output_to_csv
