"""
Module doc string
"""
class Kaleidoscope(object):

    def __init__(self):
        """
        Constructor for kaleidoscope object to process
        options data.
        """
        self.datafeed = None
        self.pattern = None

        print("hello from kaleidoscope!")

    def add_datafeed(self, datafeed):
        """ Sets this instance to use provided datafeed object """
        self.datafeed = datafeed

    def add_pattern(self, pattern, **kwargs):
        """
        Adds a Pattern class for optimization.
        Instantiation will happen during run time. Args and kwargs MUST BE tuples
        which hold the values to check.

        Example: if a Pattern accepts a parameter period, for optimization purposes
        the call to add_pattern looks like:

        kaleidoscope.add_pattern(MyPattern, period=(15, 25))
        This will execute an optimization for values 15 and 25.
        """
        self.pattern = pattern(**kwargs)

    def add_opt_pattern(self, pattern, **kwargs):
        """
        Adds a Pattern class for optimization.
        Instantiation will happen during run time. Args and kwargs MUST BE iterables
        which hold the values to check.

        kaleidoscope.add_opt_pattern(MyPattern, period=range(15, 25))
        will execute MyPattern with period values 15 -> 25 (25 not included,
        because ranges are semi-open in Python)

        If a parameter is passed but shall not be optimized the call looks like:

        kaleidoscope.add_opt_pattern(MyPattern, period=(15,))
        Notice that period is still passed as an iterable ... of just 1 element
        """
        self.pattern = pattern(**kwargs)

    def run(self, pattern):
        """ Runs the patter analyze method to start analysis """
        self.pattern.analyze()
