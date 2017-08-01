class BaseSizer(object):
    def __init__(self, account):
        self.account = account

    def order_size(self, order, action):
        raise NotImplementedError("Subclass order_size method!")
