import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
from kaleidoscope.options.iterator.option_chain import OptionChainIterator

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_rows', None)


class OptionSeries(object):
    """
    This class contains the time series data for an option strategy.
    """

    def __init__(self, symbol, strategy, data, index=None, dropna=False, **params):
        """
        Initialize this class with a dataframe of option strategy prices by
        symbol, quote date, expiration, mark, other metrics, etc

        This class will then store the data in a dictionary by expiration dates
        and provide methods that will act on this data.

        :param symbol: symbol of option chains contained in this object
        :param data: Dataframe containing the time series data of an option strategy.
                     This dataframe must contain the following columns:
                     symbol, quote_date, expiration, mark
        :param index: A list containing the index position for the 4 columns listed above,
                      if the columns are not listed in that order in the DataFrame.
                      If None, this function will infer the columns by the default order
        :param dropna: Drop all rows containing NaN in OptionSeries
        :param params: Parameters used to construct the spread data for this OptionSeries
        """

        # TODO: check index param's length is equal to 3
        if not isinstance(data, pd.DataFrame):
            raise ValueError('data param must be of pandas type DataFrame')
        elif len(data.columns) < 3:
            raise ValueError('Dataframe must contain at least 3 columns')
        elif index is not None and len(index) != 3:
            raise ValueError('index length must be 3')
        else:

            self.option_chains = {}

            self.symbol = symbol
            self.strategy = strategy
            self.data = data
            self.params = params
            self.index = index

    def iter_quotes(self):
        """
        Return an iterator to iterate through all option chains in the backtesting period

        :return:
        """

        return OptionChainIterator(self.data)

    def head(self, n=5):
        """
        Print the top n amount of expiry dates's option data
        :param n: The amount of expiry date's data to print starting from the first
        :return: None
        """
        for series in sorted(self.option_chains)[:n]:
            print(self.option_chains[series])

    def tail(self, n=5):
        """
        Print the bottom n amount of expiry dates's option data
        :param n: The amount of expiry date's data to print starting from the first
        :return: None
        """
        for series in sorted(self.option_chains)[-n:]:
            print(self.option_chains[series])

    def plot(self, exp):
        """
        Plot this OptionSeries with a surface plot for an expiration cycle.

        :param exp: The expiration to plot for
        :return:
        """

        data = self.option_chains[exp]

        # reset dataframe labels and column names to be numeric
        data.columns = [i for i in range(data.shape[1])]
        data.reset_index(inplace=True)

        # drop either symbol or spread_symbol columns depending on strategy
        data.drop('symbol' if 'spread_symbol' not in data else 'spread_symbol', axis=1, inplace=True)

        x = data.columns
        y = data.index

        X, Y = np.meshgrid(x, y)
        Z = data

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0)

        plt.show()
