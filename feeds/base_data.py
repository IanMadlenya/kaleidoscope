"""
module doc string
"""

from abc import ABC, abstractmethod
from kaleidoscope.options.option_query import OptionQuery


class BaseData(ABC):
    """
    Base class for classes implementing data feeds
    This class will take care of reading the lines and storing them in a pandas
    dataframe and merging multiple tickers if applicable.

    Subclasses only need to implement load_option_chains method.

    SQLite is the only implemented database type at this time. conn_str
    should be the absolute path of the database file or the file path
    leading to a csv file.
    """

    # map columns from data source to the standard option columns used in the library
    opt_params = (
        ('symbol', 0),
        ('underlying_symbol', -1),
        ('quote_date', 2),
        ('root', -1),
        ('expiration', 4),
        ('strike', 5),
        ('option_type', 6),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('trade_volume', 11),
        ('bid_size', -1),
        ('bid', 13),
        ('ask_size', -1),
        ('ask', 15),
        ('underlying_price', 16),
        ('iv', -1),
        ('delta', -1),
        ('gamma', -1),
        ('theta', -1),
        ('vega', -1),
        ('rho', -1),
        ('open_interest', -1)
    )

    def __init__(self):

        self.option_chains = {}
        self.date_stream = None
        self.test_chains = None

    def subscribe_options(self, symbol, **kwargs):
        """
        load all option chains for this ticker if available

        :param symbol: the underlying stock symbol to get option chain data for
        :param kwargs: arguments used to filter option chains retrieved from source
        :return: None
        """

        # call overridden method to retrieve option chain data
        self.option_chains = self.load_option_chains(symbol, **kwargs)
        self.date_stream = sorted(self.option_chains.keys())

    def get_option_chains(self, date):
        """
        Return the option chain dataframe for the parameter date

        :param date: the date to lookup option chains for
        :return: the dataframe containing the option chain for the param date,
                 otherwise, return None
        """

        if date in self.option_chains:
            for option_chain_df in self.option_chains[date]:
                option_qy = OptionQuery(self.option_chains[date][option_chain_df])
                self.option_chains[date][option_chain_df] = option_qy
                return self.option_chains[date]

        return None

    @staticmethod
    def normalize_df(dataframe):
        """
        Normalize column names using opt_params defined in this class. Normalization
        means to map columns from data source that may have different names for the same
        columns to a standard column name that will be used in this program.

        :param dataframe: the pandas dataframe containing data from the data source
        :return: dataframe with the columns renamed with standard column names and unnecessary
                 (mapped with -1) columns dropped
        """
        columns = list()
        col_names = list()

        for col in BaseData.opt_params:
            if col[1] != -1:
                columns.append(col[1])
                col_names.append(col[0])

        dataframe = dataframe.iloc[:, columns]
        dataframe.columns = col_names

        return dataframe

    @abstractmethod
    def load_option_chains(self, symbol, **kwargs):
        """
        Override this method in subclasses to implement custom option data
        load from different data sources
        """
        raise NotImplementedError("Must implement load_option_chains() method!")



