class Commission(object):
    @staticmethod
    def tos(quantity, legs):
        """
        Given the quantity to transact and the number of legs in a spread,
        calculate the commissions as per thinkorswim commission schedule

        :param quantity:
        :param legs:
        :return:
        """
