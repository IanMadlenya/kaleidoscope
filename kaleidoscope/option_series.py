import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm

from kaleidoscope.group_performance import GroupPerformance

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_rows', None)


class OptionSeries(object):
    """
    This class contains the time series data for an option strategy.
    """

    def __init__(self, ticker, data, index=None, dropna=False):
        """
        Initialize this class with a dataframe of option strategy prices by
        symbol, quote date, expiration, mark, other metrics, etc

        This class will then store the data in a dictionary by expiration dates
        and provide methods that will act on this data.

        :param ticker: the ticker of the OptionSeries Dataframe
        :param data: Dataframe containing the time series data of an option strategy.
                     This dataframe must contain the following columns:
                     symbol, quote_date, expiration, mark
        :param index: A list containing the index position for the 4 columns listed above,
                      if the columns are not listed in that order in the DataFrame.
                      If None, this function will infer the columns by the default order
        :param dropna: Drop all rows containing NaN in OptionSeries
        """

        # TODO: check index param's length is equal to 3
        if not isinstance(data, pd.DataFrame):
            raise ValueError('data param must be of pandas type DataFrame')
        elif len(data.columns) < 3:
            raise ValueError('Dataframe must contain at least 3 columns')
        elif index is not None and len(index) != 3:
            raise ValueError('index length must be 3')
        else:
            self.ticker = ticker
            self.option_chains = {}

            data.set_index(['expiration'], inplace=True)
            data.sort_index(inplace=True)

            sym_idx = 0
            date_idx = 1
            val_idx = 2

            if index is not None:
                # if index list is passed, infer the expiration column from the list
                sym_idx = index[0]
                date_idx = index[1]
                val_idx = index[2]

            for exp, df in data.groupby(level=0):
                col_names = df.columns.values
                exp = pd.to_datetime(str(exp)).strftime('%Y-%m-%d')

                df = df.pivot(index=col_names[sym_idx], columns=col_names[date_idx], values=col_names[val_idx]).dropna()
                self.option_chains[exp] = df if not dropna else df.dropna()

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

    def calc_stats(self, spread_values, period_start=None, period_end=None):
        """
        Display performance statistics for the chose price points and periods
        
        :param spread_values: A price point to generate statistics for, can also be a list of price points
        :param period_start: Periods range to base statistics on. A list of slice indices
        :param period_end: Periods range to base statistics on. A list of slice indices
        :return: Performance object
        """

        if isinstance(spread_values, tuple):
            return GroupPerformance(self.ticker, self.option_chains, period_start, period_end, spread_values)
        else:
            raise ValueError("spread_value must be of type tuple")

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
        data.drop('spread_symbol', axis=1, inplace=True)

        x = data.columns
        y = data.index

        X, Y = np.meshgrid(x, y)
        Z = data

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0)

        plt.show()
