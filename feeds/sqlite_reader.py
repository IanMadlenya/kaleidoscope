# pylint: disable=E1101

import sqlite3
import os, os.path, pathlib, pandas as pd
from feeds.base_data import BaseData
from kaleidoscope.options.option_query import OptionQuery

# sqlite database path
PROJECT_DIR = pathlib.Path(__file__).parents[1]
DATABASE_NAME = "securities.db"

class SQLiteReader(BaseData):
    """
    This class acts as a database adapter to import stock and option data from
    a sqlite database.
    """

    # map column index from csv file to the option columns used in the library
    opt_params = (
        ('nullvalue', float('Nan')),
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
        ('ivol', -1),
        ('delta', -1),
        ('gamma', -1),
        ('theta', -1),
        ('vega', -1),
        ('rho', -1),
        ('open_interest', -1)
    )

    def __init__(self, start_date=None, end_date=None, expiration=None,
                 upper_delta=0.9, lower_delta=0.1
                ):

        db_dir = os.path.join(os.sep, PROJECT_DIR, "data", DATABASE_NAME)

        self.start_date = start_date
        self.end_date = end_date
        self.expiration = expiration

        # default expiration dates to strict on end date if not provided
        if self.expiration is None:
            self.expiration = self.end_date

        # default database level filters to optimize database query
        # here we filter out the extreme delta levels that are unlikely
        # to be considered in a strategy
        self.upper_delta = upper_delta
        self.lower_delta = lower_delta

        try:
            self.data_conn = sqlite3.connect(db_dir)

        except IOError as err:
            print("Database Connection Error: ", err)

        super().__init__()

    def load_option_chains(self, symbol):
        """
        Implement the actual query to grab the dataset from the database.
        """

        if symbol not in self.option_chains:

            query = (f"SELECT * FROM {symbol}_option_chain WHERE "
                     f"expiration <= '{self.expiration}' AND "
                     f"(quote_date >= '{self.start_date}' AND quote_date <= '{self.end_date}') "
                     f"AND ((option_type='c' AND delta <= {self.upper_delta} "
                     f"AND delta >= {self.lower_delta}) OR "
                     f"(option_type='p' AND delta <= -{self.lower_delta} "
                     f"AND delta >= -{self.upper_delta}))"
                    )

            # may need to apply chunksize if loading large option chain set
            data = pd.read_sql_query(query, self.data_conn)

            # normalize dataframe columns
            data = self.normalize_df(data)
            # indexed_data = data.set_index('symbol')

            unique_quote_dates = data['quote_date'].unique()
            self.option_chains = {elem : pd.DataFrame for elem in unique_quote_dates}

            # populate the dictionary
            for key in self.option_chains.keys():
                self.option_chains[key] = \
                    {symbol: data[:][data['quote_date'] == key]}

    def normalize_df(self, dataframe):
        """ normalize column names using opt_params defined in this class """
        columns = list()
        col_names = list()

        for col in SQLiteReader.opt_params:
            if col[1] != -1 and col[0] != 'nullvalue':
                # include this column in list
                columns.append(col[1])
                col_names.append(col[0])

        dataframe = dataframe.iloc[:, columns]
        dataframe.columns = col_names

        return dataframe

    def get_option_chains(self, date):
        """
        Return the option chain dataframe for the date and ticker
        from the bar event
        """
        if date in self.option_chains:
            for option_chain_df in self.option_chains[date]:
                option_qy = OptionQuery(self.option_chains[date][option_chain_df])
                self.option_chains[date][option_chain_df] = option_qy
                return self.option_chains[date]

        return None
