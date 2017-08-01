from kaleidoscope.globals import OrderAction


class Margin(object):
    def __init__(self):
        pass

    def get_margin(self, strategy, action):
        raise NotImplementedError("Subclass get_margin method")


class ThinkOrSwimMargin(Margin):
    def get_margin(self, strategy, action):

        if strategy.name == "single":
            return strategy.mark
        elif strategy.name == "calendar":
            pass
        elif strategy.name == "combo":
            pass
        else:
            if action == OrderAction.BUY:
                # debit spread, margin is % of debit
                return strategy.mark
            else:
                # credit spread
                return strategy.max_strike_width - strategy.mark
