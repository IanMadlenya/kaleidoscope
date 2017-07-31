# pylint: disable=E1101

"""
Class to represent an option
"""
import datetime
import numpy as np


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

        exp = datetime.datetime.strptime(expiration, "%y%m%d")
        self.expiration = exp.strftime("%Y-%m-%d")

        self.option_type = option_type
        self.strike = int(strike) / 1000

        self.bid = bid
        self.ask = ask

        self.delta = delta
        self.theta = theta
        self.gamma = gamma
        self.vega = vega
        self.rho = rho
