import os, os.path, pathlib, pandas as pd
from bonzai.core.datareader.base_data import BaseData
from bonzai.core.utils import option_util
from bonzai.core.event import BarEvent

class CSVReader(BaseData):
    """
    This class acts as a CSV adapter to import stock data from
    a CSV file.
    """
    # project root path
    PROJECT_DIR = pathlib.Path(__file__).parents[3]
    # directory where csv data files are stored
    FILE_DIR = os.path.join(os.sep, PROJECT_DIR, "data")
    STOCK_FILE_NAME_SUFFIX = "stock.csv"

    def __init__(self, start_date=None, end_date=None):

        self.start_date = start_date
        self.end_date = end_date

        super().__init__()

    def load_bars(self, ticker):
        """
        Read in stock data from csv file, set the 'Date' to be index of
        pandas dataframe.
        """
        file_name = "%s_%s" % (ticker, CSVReader.STOCK_FILE_NAME_SUFFIX)
        file_dir = os.path.join(os.sep, CSVReader.FILE_DIR, file_name)

        data = pd.read_csv(file_dir, index_col=0, parse_dates=True)

        # round all digits to 2 decimals
        data = data.round(2)
        data = data.sort_index()

        if self.start_date is not None and self.end_date is None:
            data = data[self.start_date:]
        elif self.start_date is None and self.end_date is not None:
            data = data[:self.end_date]
        else:
            data = data[self.start_date:self.end_date]

        if ticker not in self.tickers_data:
            self.tickers_data[ticker] = data
            self.tickers_data[ticker]["Ticker"] = ticker

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
        adj_close_price = float(row["Adj Close"])
        volume = float(row["Volume"])

        bev = BarEvent(
            ticker, index, open_price,
            high_price, low_price, close_price,
            volume, adj_close_price
        )
        # Send event to queue
        self.events_queue.put(bev)

