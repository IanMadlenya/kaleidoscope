import datetime
from abc import ABC, abstractmethod


class Strategy(ABC):
    """
    This is the base class that holds various functions that implement custom trading
    logic such as entry/exit strategies and other trading mechanics
    based on option greeks and prices.
    """

    def __init__(self, broker, account, **params):
        self.broker = broker
        self.account = account
        self.start_date = None
        self.end_date = None

        self._init(**params)

    def set_cash(self, amt):
        """
        Set the cash balance of brokerage account

        :param amt: The cash amount to set for the trading account
        :return:
        """
        self.account.set_cash(amt)

    def add_option(self, symbol, strat, **params):
        """
        Pass the parameters and option strategy to create to the broker

        :param symbol: symbol to add option for
        :param strat: option strategy to create
        :param params: params to create option strategy with
        :return:
        """
        self.broker.source(symbol, strat, self.start_date, self.end_date, **params)

    def set_start_date(self, year, month, day):
        """
        Set start date of backtest

        :param year: year of start date
        :param month: month of start date
        :param day: day of start date
        :return:
        """
        self.start_date = datetime.date(year=year, month=month, day=day).strftime("%Y-%m-%d")

    def set_end_date(self, year, month, day):
        """
        Set end date of backtest

        :param year: year of end date
        :param month: month of end date
        :param day: day of end date
        :return:
        """

        self.end_date = datetime.date(year=year, month=month, day=day).strftime("%Y-%m-%d")

    def _init(self, **params):
        """
        Perform any strategy class specific initialization logic here, then
        initialize the actual custom strategy class.

        :param params: params to be passed into custom strategy
        :return:
        """
        self.on_init(**params)

    @abstractmethod
    def on_init(self, **params):
        raise NotImplementedError

    @abstractmethod
    def on_data(self, data):
        raise NotImplementedError

    def on_order_event(self, order_event):
        raise NotImplementedError

    def on_fill_event(self, order_event):
        raise NotImplementedError

    def stop(self):
        pass

    def buy(self):
        pass

    def sell(self):
        pass

    def close(self):
        pass

    def cancel(self):
        pass
