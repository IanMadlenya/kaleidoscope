"""
module doc string
"""

from decimal import Decimal
from abc import ABC, abstractmethod

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

        self.option_chains = {}
        self.date_stream = None


    def subscribe_options(self, symbol):
        """ load all option chains for this ticker if available """
        self.load_option_chains(symbol)
        self.date_stream = sorted(self.option_chains.keys())

    @abstractmethod
    def load_option_chains(self, symbol):
        """
        Override this method in subclasses to implement custom option data
        load from different data sources
        """
        raise NotImplementedError("Must implement load_option_chains() method!")



