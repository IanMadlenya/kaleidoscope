from kaleidoscope.options.option_strategies import construct


class Broker(object):
    def __init__(self, data):
        # raw option chain data
        self.data = data
        # processed option chain data representing option spreads
        self.strat_data = list()

    def construct_datafeed(self, strat, **params):
        """
        Create the option spread price data and store it in the strat_data list

        :param strat: option strategy to create price data for
        :param params: params to create option strategy
        :return:
        """
        spreads = construct(strat, self.data, **params)
        self.strat_data.append(spreads)


class DefaultBroker(Broker):
    def __init__(self, data):
        super().__init__(data)
