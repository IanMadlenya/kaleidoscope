class BasePattern(object):

    def __init__(self, **kwargs):
        # Attach user defined strategy optimzation params into class
        for k in kwargs:
            setattr(self, k, kwargs[k])

        # store the process option chain by dates
        self.basis = {}
        self.init()

    def plot(self):
        """ plot the data prepared from the on_data method """
        raise NotImplementedError("plot method not implemented!")

    def init(self):
        """ Initialize any instance variables not set by user """
        raise NotImplementedError("init method not implemented!")

    def main(self, date, datas):
        """ Apply this Pattern's filtering logic to the original option chain """
        raise NotImplementedError("main method not implemented!")

    def merge(self):
        """
        This method will merge all option chains stored in the basis into one
        dataframe that contains all option chains for all dates. This is used
        for plotting purposes
        """
        pass