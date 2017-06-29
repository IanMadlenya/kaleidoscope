class Backtest(object):
    """
    This class will simulate a trading strategy and store the results for a given strategy for analysis.
    """

    def __init__(self, series, strategy, sizer=None, commissions=None, init_balance=10000):
        """
        :param series: An OptionSeries object to run backtest with
        :param strategy: The trading strategy as a function to apply to the series
        :param sizer: A sizer function, that manages position risk
        :param commissions: A commission function, that simulates a brokers' commission schedule
        :param init_balance: The initial balance for the testing account
        """
        pass
