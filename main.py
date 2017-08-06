import kaleidoscope as kd


class SampleStrategy(kd.Strategy):
    """
    This Strategy will perform a simple buy/sell or sell/buy for an option spread.
    The target prices for each transaction are specified by the user or optimization params.
    """

    def on_init(self, **params):
        self.set_strategy_name("Sample Strategy")
        self.set_cash(10000)
        self.set_start_date(2016, 2, 19)
        self.set_end_date(2016, 2, 26)

        # Subscribe to the options data specified from params
        self.add_option(self.symbol)

    def on_data(self, data):
        """
        Define custom strategy rules in this function.

        :param data: OptionQuery object containing today's option quotes
        :return: None
        """

        # create vertical spreads with today's quotes
        call_spreads = kd.OptionStrategies.vertical(data,
                                                    option_type=kd.OptionType.CALL,
                                                    width=self.width,
                                                    DTE=self.DTE
                                                    )

        # filter the strikes to trade by looking at the spread's mark value
        contract = call_spreads.nearest_mark(self.price)

        # we sell the spread using a default market order,
        # quantity will be determined automatically by sizer
        # unless quantity is specified
        self.place_order(contract, action=kd.OrderAction.BUY)

        # for testing purposes, we send only one order at a time.
        self.tradable = False

    def on_fill(self, event):
        # for testing purposes, we allow trading again once an order was filled.
        self.tradable = True


# initialize the backtest
bt = kd.Backtest(data=kd.datafeeds.SQLiteDataFeed)
bt.add_opt_strategy(SampleStrategy,
                    symbol=("VXX",),
                    DTE=(kd.Period.SEVEN_WEEKS,),
                    width=(2,),
                    price=(1,)
                    )
bt.run()

