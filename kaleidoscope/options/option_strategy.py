# pylint: disable=E1101
import re
from datetime import datetime
from itertools import groupby

from kaleidoscope.globals import OrderAction
from kaleidoscope.options.option import Option


class OptionStrategy(object):
    """
    This class holds all constructed option strategies created from OptionStrategies
    class' static methods. The provided convenience methods will return a single strategy
    that matches the method requirements.
    """

    def __init__(self, strategy, quotes):
        """
        This class holds an instance of an option strategy and it's
        components and provides methods to manipulate the option legs
        contained within.

        :params: chains: Dataframe containing shifted columns representing an option leg
        """

        self.quotes = quotes
        self.symbol = strategy.fetch().get_value(0, 0, takeable=True)
        self.name = strategy.fetch().get_value(0, 1, takeable=True)
        self.underlying_symbol = strategy.fetch().get_value(0, 2, takeable=True)

        # attributes to be filled by _map

        self.symbols = None
        self.exps = None
        self.strikes = None
        self.option_types = None

        self.max_strike_width = None

        self.legs = self._map(self.symbol)
        self.mark = self.calc_mark()

    def calc_mark(self):
        """
        Calculate the mark value of this option strategy based on current prices
        :return: None
        """
        if self.legs is not None:
            return sum(leg['contract'].mark * leg['quantity'] for leg in self.legs)

    def _map(self, strat_sym):
        """
        Takes an array or parsed option spread symbol and create option legs
        as per symbol's arrangement

        :param strat_sym: Array containing the components of an option spread's symbol
        :return:
        """

        # TODO: Refactor this method

        trimmed_sym = strat_sym.replace(".", "")
        parsed = re.findall('\W+|\w+', trimmed_sym)

        strat_legs = list()
        symbols = list()
        exps = list()
        strikes = list()
        option_types = list()

        # default mapping for each option symbol
        quantity = 1
        side = OrderAction.BUY

        for piece in parsed:
            if piece == "+":
                side = OrderAction.BUY
                continue
            elif piece == "-":
                side = OrderAction.SELL
                continue
            else:
                try:
                    quantity = int(piece)
                    continue
                except ValueError:
                    pass

            if len(piece) >= 18:
                # this is an option symbol, get option info
                sym_info = self.quotes[self.quotes['symbol'] == piece].to_dict(orient='records')[0]
                # convert pandas datetime
                expiration = sym_info['expiration'].date().strftime("%Y-%m-%d")

                option = Option(sym_info)

                if piece not in symbols:
                    symbols.append(piece)

                if expiration not in exps:
                    exps.append(expiration)

                if sym_info['strike'] not in strikes:
                    strikes.append(sym_info['strike'])

                option_types.append(sym_info['option_type'])

                strat_legs.append({'contract': option, 'quantity': quantity*side.value})

                quantity = 1
                side = OrderAction.BUY

        self.symbols = symbols
        self.exps = exps
        self.strikes = strikes
        self.option_types = [t[0] for t in groupby(option_types)]
        self.max_strike_width = self._max_strike_width()

        return strat_legs

    def _max_strike_width(self):
        """
        Calculate the max strike widths stored in strikes list
        :return: Max strike width
        """
        length = len(self.strikes)
        if length == 1:
            return 0
        elif length == 2:
            return abs(self.strikes[1] - self.strikes[0])
        elif length == 3:
            return max(abs(self.strikes[1] - self.strikes[0]),
                       abs(self.strikes[2] - self.strikes[1]))
        elif length == 4:
            return max(abs(self.strikes[1] - self.strikes[0]),
                       abs(self.strikes[3] - self.strikes[2]))
        else:
            raise ValueError("invalid amounts of strikes in option strategy")

    def __str__(self):
        n = self.name.upper()
        s = self.underlying_symbol

        p_e = [datetime.strptime(exp, "%Y-%m-%d") for exp in self.exps]
        e = "".join('%s/' % p.strftime('%d %b %y').upper() for p in p_e)[0: -1]

        st = "".join('%s/' % '{0:g}'.format(st) for st in self.strikes)[0: -1]
        t = "".join('%s/' % t.upper() for t in self.option_types)[0: -1]

        return f"{n} {s} {e} {st} {t}"
