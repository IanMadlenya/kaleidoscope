import datetime

from kaleidoscope.event import OrderEvent
from kaleidoscope.globals import OrderAction, OrderType, OrderTIF
from kaleidoscope.options.option_query import OptionQuery
from kaleidoscope.options.option_strategy import OptionStrategy
from kaleidoscope.sizers import fixed_quantity_sizer


class Strategy(object):
    """
    This is the base class that holds various functions that implement custom trading
    logic such as entry/exit strategies and other trading mechanics
    based on option greeks and prices.
    """

    def __init__(self, broker, queue, **params):

        self.broker = broker

        self.current_date = None
        self.current_quotes = None

        self.queue = queue
        self.order_list = list()

        self.start_date = None
        self.end_date = None

        if 'sizer' not in params:
            self.sizer = fixed_quantity_sizer

        self.tradable = True
        self.name = "Custom Strategy"

        self._init(**params)

    def positions_total(self):
        return self.broker.positions_total()

    def set_strategy_name(self, name):
        self.name = name

    def set_cash(self, amt):
        """
        Set the cash balance of brokerage account

        :param amt: The cash amount to set for the trading account
        :return:
        """
        self.broker.set_account_balance(amt)

    def add_option(self, symbol, exclude_splits=True, option_type=None):
        """
        Pass the parameters and option strategy to create to the broker

        :param symbol: symbol to add option for
        :param exclude_splits: exclude options created from the underlying's stock splits
        :param option_type: If None, or not passed in, will retrieve both calls and puts of option chain
        :return: None
        """
        self.broker.source(symbol, self.start_date, self.end_date, exclude_splits, option_type)

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

        # register strategy params as instance class attributes
        self.__dict__.update(params)

        self.on_init(**params)
        print(f"{self.name} Initialized with the following parameters:", params)

    def on_init(self, **params):
        raise NotImplementedError

    def on_data_event(self, event):
        """
        Acts as a receiver to the data event passed from backtester
        Set class params from data event and pass data into on_data method.

        :param event: Data event passed from backtester
        :return: None
        """
        # store the event components in instance variables
        self.current_date = event.date
        self.current_quotes = event.quotes.fetch()

        # send a copy of the quotes to custom strategy
        self.on_data(event.quotes)

    def on_data(self, data):
        raise NotImplementedError

    def on_fill_event(self, event):
        """
        Acts as a receiver to the fill event passed from backtester.
        Do any processing logic here before applying user defined logic.

        :param event: Fill event passed from backtester
        :return: None
        """
        self.on_fill(event)

    def on_fill(self, event):
        pass

    def on_rejected_event(self, event):
        """
        Acts as a receiver to the rejected event passed from backtester
        Do any processing logic here before applying user defined logic.

        :param event: Rejected event passed from backtester
        :return: None
        """
        self.on_rejected(event)

    def on_rejected(self, event):
        pass

    def on_expired_event(self, event):

        self.on_expired(event)

    def on_expired(self, event):
        pass

    def place_order(self, strategy, action, quantity=None,
                    order_tif=OrderTIF.GTC, order_type=OrderType.MKT, limit_price=None):
        """
        Create a buy signal event and place it in the queue

        :param strategy: OptionStrategy object containing option legs of an option strategy
        :param action: The order action for this order, OrderAction.BUY or OrderAction.SELL
        :param limit_price: The limit price for this order
        :param order_type: The action of the order, BUY or SELL
        :param order_tif: The 'time in force' for this order, default GTC
        :param quantity: The amount to transaction, > 0 for buy < 0 for sell
        :return: None
        """
        if not isinstance(strategy, OptionQuery):
            raise ValueError("Strategy param must be of type OptionQuery")
        elif not isinstance(action, OrderAction):
            raise ValueError("Action must be of type OrderAction")

        if self.tradable:

            if strategy.fetch().shape[0] != 1:
                raise ValueError("Strategy param must contain one strategy")

            # Initialize an option strategy object from the symbol
            option_strategy = OptionStrategy(strategy, self.current_quotes)

            # use sizer to determine quantity
            if quantity is None:
                quantity = self.sizer(option_strategy, action)

            # create an new order event and place it in the queue
            event = OrderEvent(self.current_date, option_strategy, action,
                               quantity, order_type, order_tif, limit_price)

            self.queue.put(event)

        return

    def close_order(self, ticket, price=None):
        pass

    def cancel(self):
        pass
