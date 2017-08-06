from kaleidoscope.globals import Moneyness
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
        self.contract = contract

        if isinstance(self.contract, Option):
            self.expiration = self.contract.expiration
            self.moneyness = self.get_moneyness()

        # set initial values
        self.trade_price = (self.contract.bid + self.contract.ask) / 2
        self.open_pl = 0

        self.mark = self.trade_price
        self.net_liquidating_value = self.mark * self.quantity * 100

    def get_expiration(self):
        if hasattr(self, 'expiration'):
            return self.expiration.date().strftime("%Y-%m-%d")
        else:
            raise AttributeError("Attribute 'expiration' does not exist.")

    def get_moneyness(self):
        """
        Determines the moneyness of this position. If call option and underlying
        price is above strike price, it is ITM otherwise OTM. If put option and underlying
        price is below strike price, it is ITM otherwise OTM. If strike and underlying
        price are exactly the same for both option types, it is ATM

        :return: None
        """

        c = self.contract

        if ((c.strike < c.underlying_price and c.option_type == 'c') or
                (c.strike > c.underlying_price and c.option_type == 'p')):
            return Moneyness.ITM
        elif ((c.strike > c.underlying_price and c.option_type == 'c') or
                  (c.strike < c.underlying_price and c.option_type == 'p')):
            return Moneyness.OTM
        else:
            return Moneyness.ATM

    def update(self, quotes):
        """
        Update this position's current market values

        :param quotes: Dataframe containing the latest market info for the position's symbol
        :return: None
        """

        # TODO: account for stock legs for covered stocks

        # filter the quotes for this position's symbol and get the dict with all the attributes
        quote = quotes[quotes['symbol'] == self.contract.symbol].to_dict(orient='records')[0]
        self.contract.update(quote)

        # update mark value
        self.mark = (self.contract.bid + self.contract.ask) / 2
        self.net_liquidating_value = self.mark * self.quantity * 100
        self.open_pl = (self.mark - self.trade_price) * self.quantity * 100

        # update moneyness
        self.moneyness = self.get_moneyness()

    def __hash__(self):
        return hash(self.contract.symbol)

    def __eq__(self, other):
        return self.contract.symbol == other.contract.symbol

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        if isinstance(other, Position) and self == other:
            self.quantity += other.quantity
            return self
