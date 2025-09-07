from src.Base import CBase
from src.Signals import CSignals
from src.KarAlZararKes import CKarAlZararKes

class CTrader(CBase):
    def __init__(self, Index):
        super().__init__()
        self.Id = Index
        self.Signals = CSignals()
        self.KarAlZararKes = CKarAlZararKes()
        self.StartDateTimeStr = ""
        self.StopDateTimeStr = ""
        self.StartDateStr = ""
        self.StopDateStr = ""
        self.StartTimeStr = ""
        self.StopTimeStr = ""

    def initialize(self, Open, High, Low, Close, Volume, Lot, myVarlik):
        pass

    def reset(self):
        pass

    def reset_date_times(self):
        pass

    def set_date_times(self, dt1, dt2):
        pass

    def is_son_yon_a(self):
        pass

    def is_son_yon_s(self):
        pass

    def is_son_yon_f(self):
        pass

    def dongu_basi_degiskenleri_resetle(self, i):
        pass

    def dongu_basi_degiskenleri_guncelle(self, i):
        pass

    def anlik_kar_zarar_hesapla(self, i):
        pass

    def emirleri_resetle(self, i):
        self.Al = False
        self.Sat = False
        self.FlatOl = False
        self.PasGec = False
        self.KarAl = False
        self.ZararKes = False
        pass

    def gun_sonu_poz_kapat(self, i, enabled):
        pass

    def emirleri_uygula(self, i):
        pass

    def sistem_yon_listesini_guncelle(self, i):
        pass

    def sistem_seviye_listesini_guncelle(self, i):
        pass

    def sinyal_listesini_guncelle(self, i):
        pass

    def islem_listesini_guncelle(self, i):
        pass

    def komisyon_listesini_guncelle(self, i):
        pass

    def bakiye_listesini_guncelle(self, i):
        pass

    def dongu_sonu_degiskenleri_setle(self, i):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def ideal_getiri_hesapla(self):
        pass

    def istatistikleri_hesapla(self):
        pass

    def istatistikleri_ekrana_yaz(self, val):
        pass

    def getiri_istatistikleri_ekrana_yaz(self, val):
        pass

    def istatistikleri_dosyaya_yaz(self, filename):
        pass

    def sinyalleri_ekrana_ciz(self, k):
        return k

    def optimizasyon_istatistiklerinin_basliklarini_dosyaya_yaz(self, filename):
        pass

    def optimizasyon_istatistiklerini_dosyaya_yaz(self, filename, run_index, total_runs):
        pass

    def emirleri_setle(self, i, al, sat, flatol, pasgec, karal, zararkes):
        self.Al = al
        self.Sat = sat
        self.FlatOl = flatol
        self.PasGec = pasgec
        self.KarAl = karal
        self.ZararKes = zararkes

    def emir_oncesi_dongu_foksiyonlarini_calistir(self, bar_index):
        # int i = BarIndex;
        #
        # myTrader.DonguBasiDegiskenleriResetle(Sistem, i);
        #
        # myTrader.DonguBasiDegiskenleriGuncelle(Sistem, i);
        #
        # if (i < 1) return;
        #
        # myTrader.AnlikKarZararHesapla(Sistem, i);
        #
        # myTrader.EmirleriResetle(Sistem, i);
        #
        # bool isYeniGun = (V[i].Date.Day != V[i - 1].Date.Day); if (isYeniGun) Sistem.DikeyCizgiEkle(i, Color.DimGray, 2, 2);
        #
        # bool isYeniSaat = (V[i].Date.Hour != V[i - 1].Date.Hour);  //if (isYeniSaat) Sistem.DikeyCizgiEkle(i, Color.DimGray, 2, 2);
        #
        # if (myTrader.Signals.GunSonuPozKapatildi)
        # {
        #     myTrader.Signals.GunSonuPozKapatildi = false;
        # }
        #
        # if (myTrader.Signals.KarAlindi || myTrader.Signals.ZararKesildi || myTrader.Signals.FlatOlundu)
        # {
        #     myTrader.Signals.KarAlindi = false;
        #     myTrader.Signals.ZararKesildi = false;
        #     myTrader.Signals.FlatOlundu = false;
        #     myTrader.Signals.PozAcilabilir = false;
        # }
        #
        # if (myTrader.Signals.PozAcilabilir == false)
        # {
        #     myTrader.Signals.PozAcilabilir = true;
        #     myTrader.Signals.PozAcildi = false;
        # }
        pass

    def islem_zaman_filtresi_uygula(self, bar_index):
        # // Dısardan
        # set
        # edilen
        # parametreler
        # uzerinde
        # degisiklik
        # yapar
        # ve
        # son
        # hallerini
        # dondurur
        # // Kullanim: mySystem.IslemZamanFiltresiUygula(Sistem, i, ref
        # Al, ref
        # Sat, ref
        # FlatOl, ref
        # PasGec, ref
        # KarAl, ref
        # ZararKes, 0);
        # // mySystem.EmirleriSetle(Sistem, i, Al, Sat, FlatOl, PasGec, KarAl, ZararKes);
        #
        # bool
        # useTimeFiltering = myTrader.Signals.TimeFilteringEnabled ? true: false;
        # if (useTimeFiltering)
        #     {
        #         int
        #     checkResult = 0;
        #     bool
        #     isTradeEnabled = false;
        #     bool
        #     isPozKapatEnabled = false;
        #
        #     myTrader.IslemZamanFiltresiUygula(Sistem, BarIndex, FilterMode, ref
        #     isTradeEnabled, ref
        #     isPozKapatEnabled, ref
        #     checkResult);
        #
        #     if (!isTradeEnabled) Al = false;
        #     if (!isTradeEnabled) Sat = false;
        #     if (isPozKapatEnabled) FlatOl = true;
        #     }
        pass

    def islem_zaman_filtresi_uygula(self, bar_index, filter_mode = 3):
        # // Attribute
        # 'lar uzerinde islem yapar
        # // Kullanım: mySystem.EmirleriSetle(Sistem, i, Al, Sat, FlatOl, PasGec, KarAl, ZararKes);
        # // mySystem.IslemZamanFiltresiUygula(Sistem, i);
        #
        # bool
        # useTimeFiltering = myTrader.Signals.TimeFilteringEnabled ? true: false;
        # if (useTimeFiltering)
        #     {
        #         int
        #     checkResult = 0;
        #     bool
        #     isTradeEnabled = false;
        #     bool
        #     isPozKapatEnabled = false;
        #
        #     myTrader.IslemZamanFiltresiUygula(Sistem, BarIndex, FilterMode, ref
        #     isTradeEnabled, ref
        #     isPozKapatEnabled, ref
        #     checkResult);
        #
        #     if (!isTradeEnabled) Al = false;
        #     if (!isTradeEnabled) Sat = false;
        #     if (isPozKapatEnabled) FlatOl = true;
        #     }
        pass


    def emir_sonrasi_dongu_foksiyonlarini_calistir(self, bar_index):
        # int
        # i = BarIndex;
        #
        # // KarAl = myTrader.KarAlZararKes.SonFiyataGoreKarAlSeviyeHesapla(Sistem, i, 5, 50, 1000) != 0 ? true: false;
        #
        # // ZararKes = myTrader.KarAlZararKes.SonFiyataGoreZararKesSeviyeHesapla(Sistem, i, -1, -10,
        #                                                                         1000) != 0 ? true: false;
        #
        # // KarAl = myTrader.Signals.KarAlEnabled ? KarAl: false;
        #
        # // ZararKes = myTrader.Signals.ZararKesEnabled ? ZararKes: false;
        #
        # myTrader.EmirleriSetle(Sistem, i, Al, Sat, FlatOl, PasGec, KarAl, ZararKes);
        #
        # myTrader.Signals.GunSonuPozKapatildi = myTrader.GunSonuPozKapat(Sistem, i, myTrader.Signals.GunSonuPozKapatEnabled);
        #
        # myTrader.EmirleriUygula(Sistem, i);
        #
        # if (myTrader.Signals.KarAlindi == false & & myTrader.Signals.KarAl) {myTrader.Signals.KarAlindi = true;}
        #
        # if (myTrader.Signals.ZararKesildi == false & & myTrader.Signals.ZararKes) {myTrader.Signals.ZararKesildi = true;}
        #
        # if (myTrader.Signals.FlatOlundu == false & & myTrader.Signals.FlatOl) {myTrader.Signals.FlatOlundu = true;}
        #
        # myTrader.SistemYonListesiniGuncelle(Sistem, i);
        #
        # myTrader.SistemSeviyeListesiniGuncelle(Sistem, i);
        #
        # myTrader.SinyalListesiniGuncelle(Sistem, i);
        #
        # myTrader.IslemListesiniGuncelle(Sistem, i);
        #
        # myTrader.KomisyonListesiniGuncelle(Sistem, i);
        #
        # myTrader.BakiyeListesiniGuncelle(Sistem, i);
        #
        # myTrader.DonguSonuDegiskenleriSetle(Sistem, i);
        pass