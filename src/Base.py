class CBase:
    def __init__(self):
        self.Id = 0
        self.V = None
        self.EpochTime = []
        self.DateTime = []
        self.Date =  []
        self.Time = []
        self.Open = []
        self.High = []
        self.Low = []
        self.Close = []
        self.Volume = []
        self.Lot = []
        self.BarCount = 0
        self.LastBarIndex = 0

    def __del__(self):
        pass

    def show_message(self, Message):
        print(Message)

    def set_data(self, EpochTime, DateTime, Date, Time, Open, High, Low, Close, Volume, Lot):
        self.EpochTime = EpochTime
        self.DateTime = DateTime
        self.Date = Date
        self.Time = Time
        self.Open = Open
        self.High = High
        self.Low = Low
        self.Close = Close
        self.Volume = Volume
        self.Lot = Lot
        self.BarCount = len(Close)
        self.LastBarIndex = len(Close) - 1