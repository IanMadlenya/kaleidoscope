from kaleidoscope.options.option_strategies import OptionStrategies
from kaleidoscope.globals import OptionType
from .strategy import Strategy


class SimpleBuySell(Strategy):
    """
    This Strategy will perform a simple buy/sell or sell/buy for an option spread.
    The target prices for each transaction are specified by the user or optimization params.
    """

    def on_init(self, **params):
        self.set_cash(10000)
        self.set_start_date(2016, 2, 19)
        self.set_end_date(2016, 2, 19)
        self.add_option("VXX",
                        OptionStrategies.vertical,
                        option_type=OptionType.CALL,
                        width=params['width']
                        )

    def on_data(self, data):
        pass
