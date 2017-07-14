from beautifultable import BeautifulTable

from kaleidoscope.statistics.performance import Performance


class GroupPerformance(dict):
    """
    This is a convenience class to provide a way to store multiple
    instances of Performance object for comparison purposes. It is a
    wrapper over a dict. Any new Performance objects entered into this
    object will retain it's order.

    The order of the series passed in will be preserved.
    Individual PerformanceStats objects can be accessed via index
    position or name via the [] accessor.
    """

    def __init__(self, option_chains, period_start, period_end, *spread_values):

        super(GroupPerformance, self).__init__()

        self.perfs = []
        self.period_start = period_start
        self.period_end = period_end
        self.option_chains = option_chains

        for value in spread_values:
            self.perfs.append(Performance(option_chains, value, period_start, period_end))

    def __getitem__(self, key):
        if type(key) == int:
            return self[self.perfs[key]]
        else:
            return self.get(key)

    def add(self, *spread_values):
        """
        Add a performance object into this object to keep track of stats
        :param spread_values:
        :return:
        """
        if isinstance(spread_values, tuple):
            for value in spread_values:
                self.perfs.append(Performance(self.option_chains, value,
                                              self.period_start, self.period_end))
        else:
            raise ValueError("Must add only objects of type Performance")

    def describe(self):
        """
        Display statistics in a neatly formatted table
        :return: None
        """
        table = BeautifulTable()

        # dynamically create column headers
        table.column_headers = [''] + [perf.name for perf in self.perfs]
        table.append_row(['Win %'] + [perf.win_loss_pct[0] for perf in self.perfs])
        table.append_row(['Loss %'] + [perf.win_loss_pct[1] for perf in self.perfs])
        table.append_row(['', ''])
        table.append_row(['Total Trades'] + [perf.total_trades for perf in self.perfs])

        print(table)
