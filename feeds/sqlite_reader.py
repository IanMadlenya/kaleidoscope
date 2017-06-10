import os, os.path, pathlib, pandas as pd
import sqlite3
import kaleidoscope.helpers as helpers
from feeds.base_data import BaseData
from kaleidoscope.event import BarEvent


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
        ('underlying_symbol', 0),
        ('quote_date', 1),
        ('root', 2),
        ('expiration', 3),
        ('strike', 4),
        ('option_type', 5),
        ('open', 6),
        ('high', 7),
        ('low', 8),
        ('close', 9),
        ('trade_volume', 10),
        ('bid_size', 25),
        ('bid', 26),
        ('ask_size', 27),
        ('ask', 28),
        ('delta', 20),
        ('gamma', 21),
        ('theta', 22),
        ('vega', 23),
        ('rho', 24),
        ('open_interest', 30)
    )

    def __init__(self, start_date=None, end_date=None,
                 upper_delta=0.9, lower_delta=0.1
                ):

        db_dir = os.path.join(os.sep, PROJECT_DIR, "data", DATABASE_NAME)

        self.start_date = start_date
        self.end_date = end_date

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

    def subscribe_options(self, ticker):
        """ load all option chains for this ticker if available """
        self._load_option_chains(ticker)

    def _create_event(self, index, ticker, row):
        """
        Obtain all elements of the bar from a row of dataframe
        and return a BarEvent
        """
        index = index.date()

        open_price = float(row["Open"])
        high_price = float(row["High"])
        low_price = float(row["Low"])
        close_price = float(row["Close"])
        adj_close_price = float(row["AdjClose"])
        volume = float(row["Volume"])

        bev = BarEvent(
            ticker, index, open_price,
            high_price, low_price, close_price,
            volume, adj_close_price
        )

        return bev

    def _load_option_chains(self, ticker):
        """
        Implement the actual query to grab the dataset from the database.
        """

        if ticker not in self.option_chains:

            query = (f"SELECT * FROM {ticker}_option_chain WHERE "
                     f"(quote_date >= '{self.start_date}' AND quote_date <= '{self.end_date}') "
                     f"AND ((option_type='c' AND delta <= {self.upper_delta} "
                     f"AND delta >= {self.lower_delta}) OR "
                     f"(option_type='p' AND delta <= -{self.lower_delta} "
                     f"AND delta >= -{self.upper_delta}))"
                    )

            # may need to apply chunksize if loading large option chain set
            data = pd.read_sql_query(query, self.data_conn)

            # sort option chains
            data.sort_values(by=['underlying_symbol', 'quote_date', 'root', 'expiration',
                                 'strike', 'option_type'],
                             inplace=True
                            )

            # generate the option symbol. Skip if this is provided in datafeed
            data['symbol'] = data.apply(
                lambda x: helpers.generate_symbol(
                    x['underlying_symbol'], x['expiration'],
                    x['strike'], x['option_type']
                ), axis=1
            )

            # round numeric columns to 2 decimal places
            data.round({'strike': 2, 'bid': 2, 'ask': 2, 'delta': 2, \
                        'theta': 2, 'gamma': 2, 'vega': 2, 'rho': 2})

            # split the main dataframe into smaller dataframes based on quote_date
            # create unique list of names
            unique_quote_dates = data['quote_date'].unique()

            # create a dictionary to hold dataframes by quote_date
            self.option_chains[ticker] = {elem : pd.DataFrame for elem in unique_quote_dates}

            # populate the dictionary
            for key in self.option_chains[ticker].keys():
                self.option_chains[ticker][key] = data[:][data['quote_date'] == key]

    def get_option_chains(self, ticker, date):
        """
        return the option chain dataframe for the date and ticker
        from the bar event
        """
        if ticker in self.option_chains and \
            date.strftime('%Y-%m-%d') in self.option_chains[ticker]:
            return self.option_chains[ticker][date.strftime('%Y-%m-%d')]

        return None

    def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        try:
            index, row = next(self.bar_stream)
        except (StopIteration, AttributeError):
            self.continue_backtest = False
            return

        # Create the tick event for the queue
        # Obtain all elements of the bar from the dataframe
        ticker = row["Ticker"]
        index = index.date()
        open_price = float(row["Open"])
        high_price = float(row["High"])
        low_price = float(row["Low"])
        close_price = float(row["Close"])
        adj_close_price = float(row["AdjClose"])
        volume = float(row["Volume"])

        bev = BarEvent(
            ticker, index, open_price,
            high_price, low_price, close_price,
            volume, adj_close_price
        )
        # Send event to queue
        self.events_queue.put(bev)

