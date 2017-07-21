class Sizer(object):
    def __init__(self, account):
        self.account = account

    def order_size(self, signal):
        raise NotImplementedError("Subclass order_size method!")
