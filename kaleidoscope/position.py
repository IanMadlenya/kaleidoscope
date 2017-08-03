from kaleidoscope.options.option import Option


class Position(object):
    def __init__(self, contract, quantity):
        """
        Set up the initial "account" of the Position to be
        zero for most items, with the exception of the initial
        purchase/sale.

        Then calculate the initial values and finally update the
        market value of the transaction.
        """

        self.quantity = quantity

        if isinstance(contract, Option):
            for attr in contract.__dict__:
                # add the option attributes to the position object
                setattr(self, attr, contract.__dict__[attr])
        else:
            self.symbol = contract

        # set initial values
        self.open_pl = 0
        self.net_liquidating_value = 0
        self.mark = 0


