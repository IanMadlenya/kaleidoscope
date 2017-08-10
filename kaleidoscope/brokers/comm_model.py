class CommissionsModel(object):
    def __init__(self):
        pass

    def get_commissions(self):
        raise NotImplementedError


class ThinkOrSwimCommModel(CommissionsModel):
    def __init__(self):
        super().__init__()

    def get_commissions(self, strategy):
        return 0
