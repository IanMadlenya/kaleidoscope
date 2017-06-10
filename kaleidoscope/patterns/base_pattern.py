from abc import abstractmethod

class BasePattern(object):

    def __init__(self):
        pass

    def plot(self):
        """ plot the data prepared from the on_data method """
        pass

    @abstractmethod
    def on_data(self, data):
        """ Subclasses should implement custom analysis logic """
        raise NotImplementedError("on_data method not implemented!")
        