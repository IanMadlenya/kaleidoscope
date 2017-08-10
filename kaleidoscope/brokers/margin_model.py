from kaleidoscope.globals import OrderAction


class SecurityMarginModel(object):
    def __init__(self):
        pass

    def get_init_margin(self, strategy, direction):
        raise NotImplementedError

    def get_remaining_margin(self, account):
        pass

    def _explain_margin(self, positions):
        pass

    def _identify_positions(self, positions):
        pass


class ThinkOrSwimMarginModel(SecurityMarginModel):
    def __init__(self):
        super().__init__()

    def get_init_margin(self, strategy, direction):
        """
        Calculate the margin required for a single order
        :param strategy:
        :param direction:
        :return:
        """

        if strategy.name == "single":
            return strategy.mark
        elif strategy.name == "calendar":
            pass
        elif strategy.name == "combo":
            pass
        else:
            if direction == OrderAction.BTO:
                # debit spread, margin is % of debit
                return strategy.mark
            else:
                # credit spread
                return strategy.max_strike_width - strategy.mark

    def get_remaining_margin(self, account):
        """
        Calculate the remaining margin available or option buying power
        :param account:
        :return:
        """
        return 0
