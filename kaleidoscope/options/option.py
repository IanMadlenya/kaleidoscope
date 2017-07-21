# pylint: disable=E1101

"""
Class to represent an option
"""
import numpy as np


class Option(object):
    """
    This class takes a dictionary of option attributes from OptionQuery's fetch
    methods and creates an option object.
    """

    def __init__(self, kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def get_mark_price(self):
        """ get the option's mark price """
        return np.mean([self.bid, self.ask])
