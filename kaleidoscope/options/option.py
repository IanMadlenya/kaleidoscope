# pylint: disable=E1101

"""
Class to represent an option
"""
from datetime import datetime


class Option(object):
    """
    This class takes a dictionary of option attributes from OptionQuery's fetch
    methods and creates an option object.
    """

    def __init__(self, symbol, expiration, option_type, strike,
                 bid=0, ask=0, delta=0, theta=0,
                 gamma=0, vega=0, rho=0
                 ):

        self.symbol = symbol
        self.expiration = datetime.strptime(expiration, "%y%m%d").strftime("%Y-%m-%d")
        self.option_type = option_type
        self.strike = int(strike) / 1000

        self.bid = bid
        self.ask = ask

        self.delta = delta
        self.theta = theta
        self.gamma = gamma
        self.vega = vega
        self.rho = rho

    def __hash__(self):
        return hash(self.symbol)

    def __eq__(self, other):
        return self.symbol == other.symbol

    def __ne__(self, other):
        return not(self == other)
