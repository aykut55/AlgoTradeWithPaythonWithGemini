class CVarlikManager:
    def __init__(self):
        self.IlkBakiyeFiyat = 0.0
        self.IlkBakiyePuan = 0.0
        self.KomisyonCarpan = 0.0
        self.KomisyonuDahilEt = False
        self.KaymaMiktari = 0.0
        self.KaymayiDahilEt = False
        self.KomisyonVarlikAdedSayisi = 0
        self.VarlikAdedSayisi = 0
        self.VarlikAdedCarpani = 0
        self.KontratSayisi = 0
        self.HisseSayisi = 0
        self.GetiriFiyatTipi = ""
        self.MarketIndex = 0

    def __del__(self):
        pass

    def initialize(self):
        self.set_komisyon_params()
        self.set_kayma_params()
        self.set_bakiye_params()
        self.reset()
        return self

    def reset(self):
        return self

    def set_komisyon_params(self, KomisyonCarpan=3.0):
        self.KomisyonCarpan = KomisyonCarpan
        self.KomisyonuDahilEt = KomisyonCarpan != 0.0
        return self

    def set_kayma_params(self, KaymaMiktari=0.0):
        self.KaymaMiktari = KaymaMiktari
        self.KaymayiDahilEt = KaymaMiktari != 0.0
        return self

    def set_bakiye_params(self, IlkBakiye=100000.0, IlkBakiyePuan=0.0):
        self.IlkBakiyeFiyat = IlkBakiye
        self.IlkBakiyePuan = IlkBakiyePuan
        return self

    def set_kontrat_params_bist_hisse(self, HisseSayisi=1000, VarlikAdedCarpani=1):
        self.HisseSayisi = HisseSayisi
        self.VarlikAdedCarpani = VarlikAdedCarpani
        self.VarlikAdedSayisi = HisseSayisi * VarlikAdedCarpani
        self.KomisyonVarlikAdedSayisi = HisseSayisi
        self.GetiriFiyatTipi = "TL"
        return self

    def set_kontrat_params_viop_endeks(self, KontratSayisi=1, VarlikAdedCarpani=10):
        self.KontratSayisi = KontratSayisi
        self.VarlikAdedCarpani = VarlikAdedCarpani
        self.VarlikAdedSayisi = KontratSayisi * VarlikAdedCarpani
        self.KomisyonVarlikAdedSayisi = KontratSayisi
        self.GetiriFiyatTipi = "TL"
        return self

    def set_kontrat_params_viop_hisse(self, KontratSayisi=1, VarlikAdedCarpani=100):
        self.KontratSayisi = KontratSayisi
        self.VarlikAdedCarpani = VarlikAdedCarpani
        self.VarlikAdedSayisi = KontratSayisi * VarlikAdedCarpani
        self.KomisyonVarlikAdedSayisi = KontratSayisi
        self.GetiriFiyatTipi = "TL"
        return self

    def set_kontrat_params_viop_dolar(self, KontratSayisi=1, VarlikAdedCarpani=1000):
        self.KontratSayisi = KontratSayisi
        self.VarlikAdedCarpani = VarlikAdedCarpani
        self.VarlikAdedSayisi = KontratSayisi * VarlikAdedCarpani
        self.KomisyonVarlikAdedSayisi = KontratSayisi
        self.GetiriFiyatTipi = "TL"
        return self

    def set_kontrat_params_viop_euro(self, KontratSayisi=1, VarlikAdedCarpani=1000):
        self.KontratSayisi = KontratSayisi
        self.VarlikAdedCarpani = VarlikAdedCarpani
        self.VarlikAdedSayisi = KontratSayisi * VarlikAdedCarpani
        self.KomisyonVarlikAdedSayisi = KontratSayisi
        self.GetiriFiyatTipi = "TL"
        return self

    def set_kontrat_params_viop_gram_altin(self, KontratSayisi=1, VarlikAdedCarpani=1):
        self.KontratSayisi = KontratSayisi
        self.VarlikAdedCarpani = VarlikAdedCarpani
        self.VarlikAdedSayisi = KontratSayisi * VarlikAdedCarpani
        self.KomisyonVarlikAdedSayisi = KontratSayisi
        self.GetiriFiyatTipi = "TL"
        return self

    def set_kontrat_params_banka_dolar(self, KontratSayisi=1, VarlikAdedCarpani=1):
        self.KontratSayisi = KontratSayisi
        self.VarlikAdedCarpani = VarlikAdedCarpani
        self.VarlikAdedSayisi = KontratSayisi * VarlikAdedCarpani
        self.KomisyonVarlikAdedSayisi = KontratSayisi
        self.GetiriFiyatTipi = "TL"
        return self

    def set_kontrat_params_banka_euro(self, KontratSayisi=1, VarlikAdedCarpani=1):
        self.KontratSayisi = KontratSayisi
        self.VarlikAdedCarpani = VarlikAdedCarpani
        self.VarlikAdedSayisi = KontratSayisi * VarlikAdedCarpani
        self.KomisyonVarlikAdedSayisi = KontratSayisi
        self.GetiriFiyatTipi = "TL"
        return self

    def set_kontrat_params_banka_gram_altin(self, KontratSayisi=1, VarlikAdedCarpani=1):
        self.KontratSayisi = KontratSayisi
        self.VarlikAdedCarpani = VarlikAdedCarpani
        self.VarlikAdedSayisi = KontratSayisi * VarlikAdedCarpani
        self.KomisyonVarlikAdedSayisi = KontratSayisi
        self.GetiriFiyatTipi = "TL"
        return self

    def set_kontrat_params_fx_ons_altin_micro(self, KontratSayisi=1, VarlikAdedCarpani=1):
        self.KontratSayisi = KontratSayisi
        self.VarlikAdedCarpani = VarlikAdedCarpani
        self.VarlikAdedSayisi = KontratSayisi * VarlikAdedCarpani
        self.KomisyonVarlikAdedSayisi = KontratSayisi
        self.GetiriFiyatTipi = "$"
        return self
