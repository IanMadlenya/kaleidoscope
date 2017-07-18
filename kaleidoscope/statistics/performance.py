import numpy as np


class Performance(object):
    """
    This class provides statistics for an option chain series across
    multiple expiration cycles. It provides various statistics methods
    that will calculate across multiple expiration cycles
    """

    def __init__(self, series, spread_value=1.00, period_start=None, period_end=None):
        """
        :param series: the OptionSeries object's option_chain to analyse
        :param spread_value: spread_value represents a specific spread to follow
        :param period_start: start of analysis period for each expiration cycle. Expects a slice index
        :param period_end: end of analysis period for each expiration cycle. Expects a slice index
        """
        self.option_series = series

        self.period_start = period_start
        self.period_end = period_end
        self.spread_value = spread_value
        self.name = self._name()

        # array containing the results for each time period
        self.range = self.get_range(self.spread_value, self.period_start, self.period_end)

        self._calculate()

    def _name(self):
        """
        Generate a name for this performance object based on the initialized values
        :return:
        """
        return " at " + str(self.spread_value[0])

    def plot(self):
        pass

    def set_range(self, spread_value, period_start=None, period_end=None):
        """
        Update date range of stats, charts, etc. If None then
        the earliest period and last period is used. So to reset to the original
        range, just call with no args.

        :param spread_value: spread_value represents a specific spread to follow
        :param period_start: Slice index of the start period
        :param period_end: slice index of the end period
        :return:
        """

        self.range = self.get_range(spread_value=spread_value,
                                    period_start=period_start,
                                    period_end=period_end,
                                    )

        self._calculate()

    def get_range(self, spread_value, period_start, period_end):
        """
        Prepare the prices of an OptionSeries for statistics analysis

        :param period_start: start period slice index
        :param period_end: end period slice index
        :param spread_value: prices to look at
        :return: array of results for the specified range
        """
        results = []

        if period_start is None:
            period_start = 0

        if period_end is None:
            period_end = -1

        if spread_value is None:
            spread_value = self.spread_value

        # TODO: handle multiple price points
        for expiry in self.option_series:
            df = self.option_series[expiry].reset_index(drop=True)

            try:
                min_idx = np.argmin(np.abs(df.iloc[:, period_start] - spread_value))
            except:
                continue
            else:
                df = self.option_series[expiry].iloc[min_idx, [period_start, period_end]]
                results.append((df[0], df[1]))

        return results

    def _calculate(self):
        """
        Calculate all stats and store in class instance variables

        :return: None
        """
        # set class default values
        self.win_loss_pct = self.win_loss_percent()
        self.win_loss_count = self.win_loss_count()

        self.total_trades = len(self.range)

        self.max_consecutive_wins = np.nan
        self.max_consecutive_loss = np.nan

        self.max_win_amt = np.nan
        self.max_loss_amt = np.nan

    def max_consecutive_wins(self):
        return 0

    def max_consecutive_losses(self):
        return 0

    def win_loss_percent(self):
        """
        Calculate the win and loss percentage for the selected range
        :return: Tuple (win %, loss %)
        """

        samples = len(self.range)
        profits = [(i[1] - i[0]) for i in self.range]
        wins = len([x for x in profits if x >= 0])
        win_pct = wins / samples

        return win_pct, 1 - win_pct

    def win_loss_count(self):
        """
        Count the amount of profitable and unprofitable trades
        :return: Tuple (profit count, loss count)
        """

        profit = len([(i[1] - i[0]) >= 0 for i in self.range])
        return profit, len(self.range) - profit
