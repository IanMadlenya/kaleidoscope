from abc import ABC, abstractmethod


class Strategy(ABC):
    """
    This is the base class that holds various functions that implement custom trading
    logic such as entry/exit strategies and other trading mechanics
    based on option greeks and prices.
    """

    def __init__(self, broker):
        self.broker = broker

    def add_options(self, strat, **params):
        """
        Pass the parameters and option strategy to create to the broker
        :param strat: option strategy to create
        :param params: params to create option strategy with
        :return:
        """
        self.broker.construct_datafeed(params)

    def _start(self):
        pass

    def start(self):
        pass

    def _next(self):
        pass

    @abstractmethod
    def next(self):
        """
        Event data passed to strategy
        """
        raise NotImplementedError

    def _stop(self):
        pass

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
