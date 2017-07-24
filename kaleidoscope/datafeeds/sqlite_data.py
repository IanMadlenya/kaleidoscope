from .base import AbstractDataFeed
import kaleidoscope.globals as gb
import os
import sqlite3
import pandas as pd


class SQLiteDataFeed(AbstractDataFeed):
    def __init__(self, path=None):
        self.path = path

        self.opt_params = (
            ('symbol', 0),
            ('underlying_symbol', -1),
            ('quote_date', 2),
            ('root', 1),
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
            ('delta', 18),
            ('gamma', 19),
            ('theta', 20),
            ('vega', 21),
            ('rho', 22),
            ('open_interest', -1)
        )

        if self.path is None:
            # use default path if no path given
            self.path = os.path.join(os.sep, gb.PROJECT_DIR, gb.DATA_SUB_DIR, gb.DB_NAME + ".db")

    def get(self, symbol, start=None, end=None,
            exclude_splits=True, option_type=None):
        """
        Data provider wrapper around pandas read_sql_query for sqlite database.

        :param symbol: symbol to download option data for
        :param start: start date to retrieve data from
        :param end: end date to retrieve data to
        :param exclude_splits: exclude options created from the underlying's stock splits
        :param option_type: If None, or not passed in, will retrieve both calls and puts of option chain
        :return: dataframe containing option chains
        """
        # TODO: allow for various start and end date configurations

        params = {}

        # exclude option chains created from the underlying's stock split
        if exclude_splits:
            params['root'] = symbol

        if option_type == 'c':
            params['option_type'] = 'c'

        if option_type == 'p':
            params['option_type'] = 'p'

        try:
            data_conn = sqlite3.connect(self.path)

            query = "SELECT * FROM %s_option_chain" % symbol

            # Build the query components as needed
            if start is not None and end is None:
                query += " WHERE expiration >= '%s'" % start
            elif start is None and end is not None:
                query += " WHERE expiration <= '%s'" % end
            elif start is not None and end is not None:
                query += " WHERE expiration >= '%s' AND expiration <= '%s'" % (start, end)

            # loop through opt_params, assign filter by column if applicable
            if params is not None:
                query += " AND"
                for k, v in params.items():
                    query += " %s = '%s' AND" % (k, v)
                # remove the trailing 'AND'
                query = query[:-4]

            # may need to apply chunk size if loading large option chain set
            data = pd.read_sql_query(query, data_conn)

            # normalize dataframe columns
            data = self._normalize(data, self.opt_params)
            return data

        except IOError as err:
            raise IOError(err)
