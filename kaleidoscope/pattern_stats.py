from pandas.core.base import PandasObject


class PatternStats(object):
    def __init__(self, prices):
        """
        PatternStats is a convenience class used for the performance
        evaluation of a option price series. It contains various helper functions
        to help with plotting and contains a large amount of descriptive
        statistics.

        In future, this class can be decoupled from kaleidoscope and be a library of
        financial functions for options strategy backtesting and analysis.

        """
        self.prices = prices


def to_returns(dataframe):
    """
    This method creates a new dataframe that contains all option spreads
    that expired worthless.

    :param dataframe: Dataframe to find all expired spreads on expiration date. This
                      dataframe should have been processed by an OptionStrategy method
                      and contains prices for options spreads.
    :return: dataframe with all options that expired worthless (or close to worthless)
    """
    pass


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
    PandasObject.to_returns = to_returns
