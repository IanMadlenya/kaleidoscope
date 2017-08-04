def default_commissions(strategy):
    """
    Default Commission simulates an environment with no transaction costs
    :param strategy: Option Strategy to calculate commissions for
    :param quantity: The quantity for the order
    :return: Commissions for the order
    """
    return 0


def tos_commissions(strategy):
    """
    thinkorswim Commission simulates an the commission schedule of a TOS account
    :param strategy: Option Strategy to calculate commissions for
    :param quantity: The quantity for the order
    :return: Commissions for the order
    """

    return 0
