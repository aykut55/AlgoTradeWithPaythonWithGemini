import numpy as np
import datetime as dt

class CBase:
    def __init__(self):
        self.Id = 0
        self.V = None
        self.EpochTime = []
        # DateTime String
        self.DateTime = []
        self.Date =  []
        self.Time = []
        # DateTime Object
        self.DateTimeObj = []
        self.DateObj =  []
        self.TimeObj = []
        self.Open = []
        self.High = []
        self.Low = []
        self.Close = []
        self.Volume = []
        self.Lot = []
        self.Delta = []
        self.DeltaPct = []
        self.BarCount = 0
        self.LastBarIndex = 0

    def __del__(self):
        pass

    def show_message(self, Message):
        print(Message)

    def set_data(self, EpochTime, DateTime : str, Date : str, Time : str, Open, High, Low, Close, Volume, Lot):
        self.EpochTime = EpochTime
        self.DateTime = DateTime
        self.Date = Date
        self.Time = Time
        self.DateTimeObj = [dt.datetime.strptime(date_time_str, "%Y.%m.%d %H:%M:%S") for date_time_str in DateTime]
        self.DateObj = [date_time_obj.date() for date_time_obj in self.DateTimeObj]
        self.TimeObj = [date_time_obj.time() for date_time_obj in self.DateTimeObj]
        self.Open = Open
        self.High = High
        self.Low = Low
        self.Close = Close
        self.Volume = Volume
        self.Lot = Lot
        self.Delta = Close - Open
        self.DeltaPct = np.where(Open != 0, (Close - Open) / Open * 100, 0)
        self.BarCount = len(Close)
        self.LastBarIndex = len(Close) - 1