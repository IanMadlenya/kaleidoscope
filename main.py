import kaleidoscope as kd


class SampleStrategy(kd.Strategy):
    """
    This Strategy will perform a simple buy/sell or sell/buy for an option spread.
    The target prices for each transaction are specified by the user or optimization params.
    """

    def on_init(self, **params):
        print('Strategy initialized with params:', params)
        self.set_cash(10000)
        self.set_start_date(2016, 2, 19)
        self.set_end_date(2016, 2, 19)

        # if strategy will execute only one type of option spread, specify
        # the strategy with strategy param in add_option method to improve performance
        self.add_option(self.symbol)

    def on_data(self, data):
        # Data param is an OptionQuery object
        if not self.account.has_positions():
            call_spreads = kd.OptionStrategies.vertical(data,
                                                        option_type=kd.OptionType.CALL,
                                                        width=self.width,
                                                        DTE=self.DTE
                                                        )

            contract = call_spreads.nearest_mark(self.price)
            # we sell the spread using a default market order,
            # quantity will be determined automatically by sizer
            # unless quantity is specified
            self.place_order(contract, action=kd.OrderAction.SELL)


# initialize the backtest
bt = kd.Backtest(data=kd.datafeeds.SQLiteDataFeed)
bt.add_opt_strategy(SampleStrategy,
                    symbol=("VXX",),
                    DTE=(kd.Period.SEVEN_WEEKS,),
                    width=(2,),
                    price=(0.5, 1)
                    )
bt.run()

