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
        raise NotImplementedError("on_init method not implemented!")

    def process_option_chain(self, date, datas):
        """ Apply this Pattern's filtering logic to the original option chain """
        raise NotImplementedError("on_data method not implemented!")
        