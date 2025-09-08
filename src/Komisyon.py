class CKomisyon:
    def __init__(self):
        self.Trader = None

    def __del__(self):
        pass

    def initialize(self, Trader):
        self.Trader = Trader
        return self

    def reset(self):
        return self

    def hesapla(self, BarIndex):
        result = 0
        i = BarIndex
        self.Trader.Status.KomisyonFiyat = self.Trader.Lists.KomisyonIslemSayisiList[i] * float(self.Trader.Status.KomisyonCarpan) * self.Trader.Status.KomisyonVarlikAdedSayisi
        self.Trader.Lists.KomisyonFiyatList[i] = self.Trader.Status.KomisyonFiyat
        return result
