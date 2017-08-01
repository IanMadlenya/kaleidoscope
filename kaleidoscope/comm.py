class Commission(object):
    def __init__(self):
        pass

    def get_commissions(self, strategy, quantity):
        raise NotImplementedError("Subclass get_commissions method!")


class DefaultCommissions(Commission):
    def get_commissions(self, strategy, quantity):
        """
        Default Commission simulates an environment with no transaction costs
        :param strategy: Option Strategy to calculate commissions for
        :param quantity: The quantity for the order
        :return: Commissions for the order
        """
        return 0


class ThinkOrSwimComm(Commission):
    def get_commissions(self, strategy, quantity):
        """
        thinkorswim Commission simulates an the commission schedule of a TOS account
        :param strategy: Option Strategy to calculate commissions for
        :param quantity: The quantity for the order
        :return: Commissions for the order
        """
        return 0
