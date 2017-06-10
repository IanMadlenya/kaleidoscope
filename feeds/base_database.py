import sqlite3
from feeds.base_data import BaseData
from abc import ABC, abstractmethod

class BaseDatabase(BaseData, ABC):

    def __init__(self, data_type, conn_str):

        self.option_chains = {}

        try:
            if data_type == 'sqlite':
                self.data_conn = sqlite3.connect(conn_str)
            elif data_type == 'postgresql':
                pass
            elif data_type == 'mysql':
                pass
            elif data_type == 'mongodb':
                pass
        except IOError as err:
            print("Database Connection Error: ", err)

        super().__init__()

    def subscribe_options(self, ticker):
        """ load all option chains for this ticker if available """
        self.load_option_chains(ticker)

    @abstractmethod
    def load_option_chains(self, ticker):
        """
        Load option chain data into data feed object
        """
        raise NotImplementedError("Must override load_option_chains")

    def get_option_chains(self, ticker, date):
        """
        Retrieves the option chains already loaded into this datafeed
        by ticker and quote date
        """
        raise NotImplementedError("Must override get_option_chains")

