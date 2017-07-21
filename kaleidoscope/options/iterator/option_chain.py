from kaleidoscope.event import DataEvent
from kaleidoscope.options.option_query import OptionQuery


class OptionChainIterator(object):
    def __init__(self, data):

        self.data = data
        # get all quote dates that can be iterated
        self.dates = sorted(data['quote_date'].unique())
        # turn list of dates into an iterable
        self.dates = iter(self.dates)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            df = self.data
            quote_date = next(self.dates)
            # return a data event containing the daily quote for option chains
            option_chains = df.loc[df['quote_date'] == quote_date]
            # create the data event and return it
            return DataEvent(quote_date, OptionQuery(option_chains))
        except StopIteration:
            raise
