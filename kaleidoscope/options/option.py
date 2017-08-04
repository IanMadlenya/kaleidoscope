# pylint: disable=E1101

"""
Class to represent an option
"""


class Option(object):
    """
    This class takes a dictionary of option attributes from OptionQuery's fetch
    methods and creates an option object.
    """

    def __init__(self, sym_info):
        # use the attributes of option info to populate this instance's attributes
        self.__dict__.update(sym_info)

    def __hash__(self):
        return hash(self.symbol)

    def __eq__(self, other):
        return self.symbol == other.symbol

    def __ne__(self, other):
        return not(self == other)

    def update(self, quote):
        """
        Update values of this option from quote object
        :param quote: Dict containing option attributes from dataframe
        :return:
        """
        print("updating")
