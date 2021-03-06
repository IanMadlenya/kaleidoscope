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

        # set initial values
        self.trade_price = (self.contract.bid + self.contract.ask) / 2
        self.open_pl = 0

        self.mark = self.trade_price
        self.net_liquidating_value = self.mark * self.quantity * 100

    def update(self, quotes: object) -> object:
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
