class BasePattern(object):

    def __init__(self, datafeed, **kwargs):
        # Attach user defined strategy optimzation params into class
        for k in kwargs:
            setattr(self, k, kwargs[k])

        # set reference to data feed to be accessed by Pattern
        self.datafeed = datafeed

        # store the process option chain by dates
        self.init()

    def plot(self):
        """ plot the data prepared from the main method """
        raise NotImplementedError("plot method not implemented!")

    def init(self):
        """ Initialize any instance variables not set by user """
        raise NotImplementedError("init ethod not implemented!")

    def setup(self, quote_date, option_chains):
        """ Apply this Pattern's filtering logic to the original option chain """
        raise NotImplementedError("main method not implemented!")

    def main(self, test_chain, test_spreads):
        """ Analyse the processed option chain dataframe by the setup method"""
        raise NotImplementedError("analyse method not implemented!")
