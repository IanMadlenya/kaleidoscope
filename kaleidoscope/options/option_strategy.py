# pylint: disable=E1101
import re

from kaleidoscope.options.order_leg import OptionLeg, StockLeg
from kaleidoscope.globals import OrderAction
from kaleidoscope.helpers import parse_symbol
from kaleidoscope.options.option_query import OptionQuery
from kaleidoscope.options.option import Option


class OptionStrategy(object):
    """
    This class holds all constructed option strategies created from OptionStrategies
    class' static methods. The provided convenience methods will return a single strategy
    that matches the method requirements.
    """

    def __init__(self, chains, name=None):
        """
        This class holds an instance of an option strategy and it's
        components and provides methods to manipulate the option legs
        contained within.

        :params: chains: Dataframe containing shifted columns representing an option leg
        """
        self.chains = chains
        self.name = name

        if self.chains is not None:
            self.underlying_symbol = chains['underlying_symbol'][0]

        # attributes to be filled when 'nearest' methods are used
        self.legs = None
        self.expirations = None
        self.strikes = None
        self.option_types = None
        self.mark = None
        self.max_strike_width = None

    def _map(self, strat_sym):
        """
        Takes an array or parsed option spread symbol and create option legs
        as per symbol's arrangement

        :param sym_array: Array containing the components of an option spread's symbol
        :return:
        """

        trimmed_sym = strat_sym.replace(".", "")
        parsed = re.findall('\W+|\w+', trimmed_sym)

        strat_legs = list()
        exps = list()
        strikes = list()

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
                # TODO: use regex to parse quantity, stock/option symbol
                try:
                    quantity = int(piece)
                    continue
                except ValueError:
                    pass

            if len(piece) >= 18:
                # this is an option symbol, parse it
                sym_group = parse_symbol(piece)
                exp = sym_group[2]
                option_type = sym_group[3]
                strike = sym_group[4]

                option = Option(symbol=piece, expiration=exp, option_type=option_type, strike=strike)

                if option.expiration not in exps:
                    exps.append(option.expiration)

                if option.strike not in strikes:
                    strikes.append(option.strike)

                strat_legs.append(OptionLeg(option, quantity=quantity * side.value))

                quantity = 1
                side = OrderAction.BUY

        self.expirations = exps
        self.strikes = strikes

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

    def nearest_mark(self, mark, tie='roundup'):
        """
        Returns the object itself with the legs attribute containing the option legs
        that matches the mark value and 'expiration', 'strikes' and 'symbol' attributes
        assigned.

        :param mark: Mark value to match option spread with
        :param tie: how to handle multiple matches for mark value
        :return: Self
        """
        spread = OptionQuery(self.chains).closest('mark', mark).fetch()

        if len(spread) != 1:
            max_mark_idx = spread['mark'].idxmax()
            min_mark_idx = spread['mark'].idxmin()

            if tie == 'roundup':
                self.legs = self._map(spread['symbol'][max_mark_idx])
                self.mark = spread['mark'][max_mark_idx]
            else:
                self.legs = self._map(spread['symbol'][min_mark_idx])
                self.mark = spread['mark'][min_mark_idx]
        else:
            self.legs = self._map(spread['symbol'][0])
            self.mark = spread['mark'][0]

        self.max_strike_width = self._max_strike_width()
        return self

    def nearest_delta(self, price):
        """

        :param price:
        :return:
        """
        pass

    def filter(self, func, **params):
        """

        :param func:
        :param params:
        :return:
        """
        pass
