"""
module doc string
"""

from decimal import Decimal
from abc import ABC, abstractmethod
from kaleidoscope.event import BarEvent

import pandas as pd
pd.set_option('display.expand_frame_repr', False)

class BaseData(ABC):
    """
    Base class for classes implementing data feeds
    This class will take care of reading the lines and storing them in a pandas
    dataframe and merging multiple tickers if applicable.

    Subclasses only need to implement load_data method.

    SQLite is the only implemented database type at this time. conn_str
    should be the absolute path of the database file or the file path
    leading to a csv file.
    """
    def __init__(self):

        self.continue_backtest = True
        self.tickers = {}
        self.tickers_data = {}
        self.option_chains = {}
        self.bar_stream = None
        self.events_queue = None

    def set_queue(self, queue):
        """
        Give this datafeed the instance of the events queue from backtest
        """
        self.events_queue = queue

    def _merge_sort_ticker_data(self):
        """
        Concatenates all of the separate equities DataFrames
        into a single DataFrame that is time ordered, allowing tick
        data events to be added to the queue in a chronological fashion.

        Note that this is an idealised situation, utilised solely for
        backtesting. In live trading ticks may arrive "out of order".
        """
        dataframe = pd.concat(self.tickers_data.values()).sort_index()

        # We will sort by index (Date), and the ticker
        dataframe['colFromIndex'] = dataframe.index
        dataframe = dataframe.sort_values(by=["colFromIndex", "Ticker"])
        return dataframe.iterrows()

    @abstractmethod
    def stream_next(self):
        """
        Subclasses should implement this method
        """
        raise NotImplementedError("Must override stream_next")



