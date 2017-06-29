import numpy as np


class Statistics(object):
    def __init__(self, series, prices, periods=None):

        self.option_series = series
        self.prices = prices
        self.periods = periods

        self.results = self._results(prices, periods)

    def display(self):
        """
        Display statistics in a neatly formatted table
        :return: None
        """
        pass

    def _results(self, price, periods):
        """
        Prepare the prices of an OptionSeries for statistics analysis

        :param periods: periods to look at
        :param price: prices to look at
        :return: array of results
        """
        results = []

        if periods is None:
            periods = [0, -1]

        # TODO: handle multiple price points

        for expiry in self.option_series:
            df = self.option_series[expiry].reset_index(drop=True)

            try:
                min_idx = np.argmin(np.abs(df.iloc[:, periods[0]] - price))
            except:
                continue
            else:
                df = self.option_series[expiry].iloc[min_idx, [periods[0], periods[1]]]
                results.append(df[1] - df[0])

        return results

    def _calculate(self):
        """
        Calculate all stats and store in class instance variables

        :return: None
        """
        # set class default values
        self.long_win_pct = np.nan
        self.long_loss_pct = np.nan
        self.long_profit_count = np.nan
        self.long_loss_count = np.nan

        self.short_win_pct = np.nan
        self.short_loss_pct = np.nan
        self.short_profit_count = np.nan
        self.short_loss_count = np.nan

        self.total_trades = np.nan

        self.long_max_consecutive_wins = np.nan
        self.long_max_consecutive_loss = np.nan
        self.short_max_consecutive_wins = np.nan
        self.short_max_consecutive_loss = np.nan

        self.max_win_amt = np.nan
        self.max_loss_amt = np.nan


def max_consecutive_wins(results):
    pass


def max_consecutive_losses(results):
    pass


def win_pct(results, side):
    pass


def loss_pct(results, side):
    pass
