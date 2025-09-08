class CTimeFilter:
    def __init__(self):
        self.Trader = None
        pass

    def __del__(self):
        pass

    def initialize(self, Trader):
        self.Trader = Trader
        return self

    def reset(self):
        return self