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
        self.add_option("VXX")

    def on_data(self, data):
        # filter for call spreads currently price closest to specified price
        # expiring within seven weeks
        chain = (data
                 .calls()
                 .lte('expiration', kd.Period.SEVEN_WEEKS)
                 )

        # construct call spreads with current day's quotes
        call_spreads = (kd.OptionStrategies.vertical(chain.fetch(), width=self.width)
                        .closest('spread_mark', self.price)
                        )

        # we sell the spread using a default market order,
        # quantity will be determined automatically by sizer
        # unless quantity is specified
        self.sell(call_spreads, quantity=10)


# initialize the backtest
bt = kd.Backtest(data=kd.datafeeds.SQLiteDataFeed)
bt.add_opt_strategy(SampleStrategy,
                    symbol=("VXX",),
                    width=range(1, 6),
                    price=(0.5, 0.75, 1)
                    )
bt.run()

