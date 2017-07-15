import kaleidoscope as kd


class SimpleBuySell(kd.Strategy):
    """
    This Strategy will perform a simple buy/sell or sell/buy for an option spread.
    The target prices for each transaction are specified by the user or optimization params.
    """

    def __init__(self, kwargs):
        self.add_options(kd.OptionStrategies.vertical,
                         option_type=kd.OptionType.CALL,
                         DTE=kd.Period.SEVEN_WEEKS,
                         width=2
                         )

    def next(self):
        pass
