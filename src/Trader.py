from src.Base import CBase
from src.Signals import CSignals
from src.Status import CStatus
from src.Flags import CFlags
from src.Lists import CLists
from src.KarZarar import CKarZarar
from src.Komisyon import CKomisyon
from src.Bakiye import CBakiye
from src.VarlikManager import CVarlikManager
from src.Statistics import CStatistics
from src.KarAlZararKes import CKarAlZararKes
from src.TimeFilter import CTimeFilter
from src.TimeUtils import CTimeUtils
from src.FileUtils import CFileUtils
import datetime
import pandas as pd

class CTrader(CBase):
    def __init__(self,  Id=0):
        self.GrafikSembol = ""
        self.GrafikPeriyot = ""
        self.SistemAdi = ""
        super().__init__()
        self.Adi = ""
        self.Id = Id
        self.Signals = CSignals()
        self.Status = CStatus()
        self.Flags = CFlags()
        self.Lists = CLists()
        self.KarZarar = CKarZarar()
        self.Komisyon = CKomisyon()
        self.Bakiye = CBakiye()
        self.VarlikManager = None
        self.Statistics = CStatistics()
        self.KarAlZararKes = CKarAlZararKes()
        self.TimeFilter = CTimeFilter()
        self.BakiyeInitialized = False
        self.ExecutionStepNumber = 0
        self.LastResetTime = None
        self.LastExecutionTime = None
        self.LastExecutionTimeStart = None
        self.LastExecutionTimeStop = None
        self.LastStatisticsCalculationTime = None
        self.TimeUtils = CTimeUtils()
        self.ExecutionTimeInMSec = 0
        self.DateTimeStringFormat = "%d.%m.%Y %H:%M:%S"
        self.DateStringFormat = "%d.%m.%Y"
        self.TimeStringFormat = "%H:%M:%S"
        self.StartDateTime = None
        self.StopDateTime = None
        self.StartDate = None
        self.StopDate = None
        self.StartTime = None
        self.StopTime = None
        self.StartDateTimeStr = None
        self.StopDateTimeStr = None
        self.StartDateStr = None
        self.StopDateStr = None
        self.StartTimeStr = None
        self.StopTimeStr = None
        self.EnableDateTime = None
        self.DisableDateTime = None
        self.EnableDate = None
        self.DisableDate = None
        self.EnableTime = None
        self.DisableTime = None
        self.EnableDateTimeStr = None
        self.DisableDateTimeStr = None
        self.EnableDateStr = None
        self.DisableDateStr = None
        self.EnableTimeStr = None
        self.DisableTimeStr = None
        # dataframe
        self._df: pd.DataFrame | None = None

    def initialize(self, EpochTime, DateTime, Date, Time, Open, High, Low, Close, Volume, Lot, VarlikManager):
        self.VarlikManager = VarlikManager
        self.set_data(EpochTime, DateTime, Date, Time, Open, High, Low, Close, Volume, Lot)
        self.Signals.initialize()
        self.Status.initialize()
        self.Flags.initialize()
        self.Lists.initialize()
        self.Lists.create_lists(self.BarCount)
        self.KarZarar.initialize(self)
        self.Komisyon.initialize(self)
        self.Bakiye.initialize(self)
        self.Statistics.initialize(self)
        self.KarAlZararKes.initialize(self)
        self.TimeFilter.initialize(self)
        self.TimeUtils.initialize( EpochTime, DateTime, Date, Time, Open, High, Low, Close, Volume, Lot)
        self.reset()
        self.BakiyeInitialized = False
        return self

    def reset(self):
        self.Signals.reset()
        self.Status.reset()
        self.Flags.reset()
        self.Lists.reset()
        self.KarZarar.reset()
        self.Komisyon.reset()
        self.Bakiye.reset()
        self.Statistics.reset()
        self.KarAlZararKes.reset()
        self.TimeFilter.reset()
        self.TimeUtils.reset()
        self.ExecutionStepNumber = 0
        self.LastResetTime = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        self.LastExecutionTime = ""
        self.LastExecutionTimeStart = ""
        self.LastExecutionTimeStop = ""
        self.LastStatisticsCalculationTime = ""
        self.ExecutionTimeInMSec = 0
        # self.reset_date_times
        return self

    def start(self):
        self.LastExecutionTimeStart = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        self.LastExecutionTime = self.LastExecutionTimeStart
        self.TimeUtils.start_timer()

    def stop(self):
        self.LastExecutionTimeStop = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        self.TimeUtils.stop_timer()
        self.ExecutionTimeInMSec = self.TimeUtils.get_execution_time_in_msec()

    def dongu_basi_degiskenleri_resetle(self, BarIndex):
        result = 0
        i = BarIndex
        self.Lists.BarIndexList[i] = i
        self.Lists.YonList[i] = ""
        self.Lists.SeviyeList[i] = 0.0
        self.Lists.SinyalList[i] = 0.0
        self.Lists.KarZararPuanList[i] = 0.0
        self.Lists.KarZararFiyatList[i] = 0.0
        self.Lists.KarZararFiyatYuzdeList[i] = 0.0
        self.Status.KarZararFiyat = 0.0
        self.Status.KarZararPuan = 0.0
        self.Status.KarZararFiyatYuzde = 0.0
        self.Lists.KarAlList[i] = 0.0
        self.Lists.IzleyenStopList[i] = 0.0
        self.Lists.IslemSayisiList[i] = 0.0
        self.Lists.AlisSayisiList[i] = 0.0
        self.Lists.SatisSayisiList[i] = 0.0
        self.Lists.FlatSayisiList[i] = 0.0
        self.Lists.PassSayisiList[i] = 0.0
        self.Lists.KontratSayisiList[i] = 0.0
        self.Lists.VarlikAdedSayisiList[i] = 0.0
        self.Lists.KomisyonVarlikAdedSayisiList[i] = 0.0
        self.Lists.KomisyonIslemSayisiList[i] = 0.0
        self.Lists.KomisyonFiyatList[i] = 0.0
        self.Lists.KardaBarSayisiList[i] = 0.0
        self.Lists.ZarardaBarSayisiList[i] = 0.0
        self.Lists.BakiyeFiyatList[i] = self.Status.BakiyeFiyat
        self.Lists.GetiriFiyatList[i] = self.Lists.BakiyeFiyatList[i] - self.Status.BakiyeFiyat
        self.Lists.BakiyePuanList[i] = self.Status.BakiyePuan
        self.Lists.GetiriPuanList[i] = self.Lists.BakiyePuanList[i] - self.Status.BakiyePuan
        self.Lists.EmirKomutList[i] = 0.0
        self.Lists.EmirStatusList[i] = 0.0
        if self.ExecutionStepNumber == 0:
            pass
        self.ExecutionStepNumber += 1
        return result

    def dongu_basi_degiskenleri_guncelle(self, BarIndex):
        result = 0
        i = BarIndex
        self.Status.KomisyonVarlikAdedSayisi = self.VarlikManager.KomisyonVarlikAdedSayisi
        self.Status.KomisyonCarpan = self.VarlikManager.KomisyonCarpan
        self.Flags.KomisyonuDahilEt = self.VarlikManager.KomisyonuDahilEt
        self.Status.KaymaMiktari = self.VarlikManager.KaymaMiktari
        self.Flags.KaymayiDahilEt = self.VarlikManager.KaymayiDahilEt
        self.Status.VarlikAdedSayisi = self.VarlikManager.VarlikAdedSayisi
        self.Status.VarlikAdedCarpani = self.VarlikManager.VarlikAdedCarpani
        self.Status.KontratSayisi = self.VarlikManager.KontratSayisi
        self.Status.HisseSayisi = self.VarlikManager.HisseSayisi
        self.Status.IlkBakiyeFiyat = self.VarlikManager.IlkBakiyeFiyat
        self.Status.IlkBakiyePuan = self.VarlikManager.IlkBakiyePuan
        self.Status.GetiriFiyatTipi = self.VarlikManager.GetiriFiyatTipi
        if not self.BakiyeInitialized:
            self.BakiyeInitialized = True
            self.Status.BakiyeFiyat = self.Status.IlkBakiyeFiyat
            self.Status.BakiyePuan = self.Status.IlkBakiyePuan
            self.Lists.BakiyeFiyatList[i] = self.Status.BakiyeFiyat
            self.Lists.GetiriFiyatList[i] = self.Lists.BakiyeFiyatList[i] - self.Status.BakiyeFiyat
            self.Lists.BakiyePuanList[i] = self.Status.BakiyePuan
            self.Lists.GetiriPuanList[i] = self.Lists.BakiyePuanList[i] - self.Status.BakiyePuan
        return result

    def anlik_kar_zarar_hesapla(self, BarIndex, Type="C"):
        return self.KarZarar.anlik_kar_zarar_hesapla(BarIndex, Type)

    def emirleri_resetle(self, BarIndex):
        result = 0
        i = BarIndex
        self.Signals.Al = False
        self.Signals.Sat = False
        self.Signals.FlatOl = False
        self.Signals.PasGec = False
        self.Signals.KarAl = False
        self.Signals.ZararKes = False
        return result

    # def emirleri_resetle(self, i):
    #     self.Al = False
    #     self.Sat = False
    #     self.FlatOl = False
    #     self.PasGec = False
    #     self.KarAl = False
    #     self.ZararKes = False
    #     pass

    def emirleri_setle(self, BarIndex, Al, Sat, FlatOl=False, PasGec=False, KarAl=False, ZararKes=False):
        result = 0
        i = BarIndex
        self.Signals.Al = Al
        self.Signals.Sat = Sat
        self.Signals.FlatOl = FlatOl
        self.Signals.PasGec = PasGec
        self.Signals.KarAl = KarAl
        self.Signals.ZararKes = ZararKes
        return result

    # def emirleri_setle(self, i, al, sat, flatol, pasgec, karal, zararkes):
    #     self.Al = al
    #     self.Sat = sat
    #     self.FlatOl = flatol
    #     self.PasGec = pasgec
    #     self.KarAl = karal
    #     self.ZararKes = zararkes


    def emirleri_uygula(self, BarIndex):
        result = 0
        i = BarIndex
        self.Flags.AGerceklesti = False
        self.Flags.SGerceklesti = False
        self.Flags.FGerceklesti = False
        self.Flags.PGerceklesti = False
        AnlikKapanisFiyati = self.Close[i]
        AnlikYuksekFiyati = self.High[i]
        AnlikDusukFiyati = self.Low[i]
        if self.Signals.Al:
            self.Signals.Sinyal = "A"
            self.Signals.EmirKomut = 1
            self.Status.AlKomutSayisi += 1
        if self.Signals.Sat:
            self.Signals.Sinyal = "S"
            self.Signals.EmirKomut = 2
            self.Status.SatKomutSayisi += 1
        if self.Signals.PasGec:
            self.Signals.Sinyal = "P"
            self.Signals.EmirKomut = 3
            self.Status.PasGecKomutSayisi += 1
        if self.Signals.KarAl:
            self.Signals.Sinyal = "F"
            self.Signals.EmirKomut = 4
            self.Status.KarAlKomutSayisi += 1
        if self.Signals.ZararKes:
            self.Signals.Sinyal = "F"
            self.Signals.EmirKomut = 5
            self.Status.ZararKesKomutSayisi += 1
        if self.Signals.FlatOl:
            self.Signals.Sinyal = "F"
            self.Signals.EmirKomut = 6
            self.Status.FlatOlKomutSayisi += 1
        self.Status.KarAlSayisi = self.Status.KarAlKomutSayisi
        self.Status.ZararKesSayisi = self.Status.ZararKesKomutSayisi
        if self.Signals.Sinyal == "A" and self.Signals.SonYon != "A":
            self.Signals.PrevAFiyat = self.Signals.SonAFiyat
            self.Signals.PrevABarNo = self.Signals.SonABarNo
            self.Signals.PrevYon = self.Signals.SonYon
            self.Signals.PrevFiyat = self.Signals.SonFiyat
            self.Signals.PrevBarNo = self.Signals.SonBarNo
            if self.Signals.PrevYon == "F":
                pass
            if self.Signals.PrevYon == "S":
                pass
            self.Lists.YonList[i] = "A"
            self.Signals.SonYon = self.Lists.YonList[i]
            self.Signals.SonFiyat = AnlikKapanisFiyati
            if self.Flags.KaymayiDahilEt:
                self.Signals.SonFiyat = AnlikYuksekFiyati
            self.Lists.SeviyeList[i] = self.Signals.SonFiyat
            self.Signals.SonBarNo = i
            self.Signals.SonAFiyat = self.Signals.SonFiyat
            self.Signals.SonABarNo = self.Signals.SonBarNo
            if self.Signals.PrevYon == "F":
                self.Status.KomisyonIslemSayisi += 1
                self.Signals.EmirStatus = 1
            if self.Signals.PrevYon == "S":
                fark = self.Signals.SonFiyat - self.Signals.SonSFiyat
                if fark < 0:
                    self.Status.KazandiranSatisSayisi += 1
                elif fark > 0:
                    self.Status.KaybettirenSatisSayisi += 1
                else:
                    self.Status.NotrSatisSayisi += 1
                self.Status.KomisyonIslemSayisi += 2
                self.Signals.EmirStatus = 2
            self.Flags.BakiyeGuncelle = True
            self.Flags.KomisyonGuncelle = True
            self.Flags.DonguSonuIstatistikGuncelle = True
            self.Status.IslemSayisi += 1
            self.Status.AlisSayisi += 1
            self.Flags.AGerceklesti = True
        elif self.Signals.Sinyal == "S" and self.Signals.SonYon != "S":
            self.Signals.PrevSFiyat = self.Signals.SonSFiyat
            self.Signals.PrevSBarNo = self.Signals.SonSBarNo
            self.Signals.PrevYon = self.Signals.SonYon
            self.Signals.PrevFiyat = self.Signals.SonFiyat
            self.Signals.PrevBarNo = self.Signals.SonBarNo
            if self.Signals.PrevYon == "F":
                pass
            if self.Signals.PrevYon == "A":
                pass
            self.Lists.YonList[i] = "S"
            self.Signals.SonYon = self.Lists.YonList[i]
            self.Signals.SonFiyat = AnlikKapanisFiyati
            if self.Flags.KaymayiDahilEt:
                self.Signals.SonFiyat = AnlikDusukFiyati
            self.Lists.SeviyeList[i] = self.Signals.SonFiyat
            self.Signals.SonBarNo = i
            self.Signals.SonSFiyat = self.Signals.SonFiyat
            self.Signals.SonSBarNo = self.Signals.SonSBarNo
            if self.Signals.PrevYon == "F":
                self.Status.KomisyonIslemSayisi += 1
                self.Signals.EmirStatus = 3
            if self.Signals.PrevYon == "A":
                fark = self.Signals.SonFiyat - self.Signals.SonAFiyat
                if fark > 0:
                    self.Status.KazandiranAlisSayisi += 1
                elif fark < 0:
                    self.Status.KaybettirenAlisSayisi += 1
                else:
                    self.Status.NotrAlisSayisi += 1
                self.Status.KomisyonIslemSayisi += 2
                self.Signals.EmirStatus = 4
            self.Flags.BakiyeGuncelle = True
            self.Flags.KomisyonGuncelle = True
            self.Flags.DonguSonuIstatistikGuncelle = True
            self.Status.IslemSayisi += 1
            self.Status.SatisSayisi += 1
            self.Flags.SGerceklesti = True
        elif self.Signals.Sinyal == "F" and self.Signals.SonYon != "F":
            self.Signals.PrevFFiyat = self.Signals.SonFFiyat
            self.Signals.PrevFBarNo = self.Signals.SonFBarNo
            self.Signals.PrevYon = self.Signals.SonYon
            self.Signals.PrevFiyat = self.Signals.SonFiyat
            self.Signals.PrevBarNo = self.Signals.SonBarNo
            if self.Signals.PrevYon == "A":
                pass
            if self.Signals.PrevYon == "S":
                pass
            self.Lists.YonList[i] = "F"
            self.Signals.SonYon = self.Lists.YonList[i]
            self.Signals.SonFiyat = AnlikKapanisFiyati
            if self.Flags.KaymayiDahilEt:
                if self.Signals.PrevYon == "A":
                    self.Signals.SonFiyat = AnlikDusukFiyati
                if self.Signals.PrevYon == "S":
                    self.Signals.SonFiyat = AnlikYuksekFiyati
            self.Lists.SeviyeList[i] = self.Signals.SonFiyat
            self.Signals.SonBarNo = i
            self.Signals.SonFFiyat = self.Signals.SonFiyat
            self.Signals.SonFBarNo = self.Signals.SonFBarNo
            if self.Signals.PrevYon == "A":
                fark = self.Signals.SonFiyat - self.Signals.SonAFiyat
                if fark > 0:
                    self.Status.KazandiranAlisSayisi += 1
                elif fark < 0:
                    self.Status.KaybettirenAlisSayisi += 1
                else:
                    self.Status.NotrAlisSayisi += 1
                self.Status.KomisyonIslemSayisi += 1
                self.Signals.EmirStatus = 5
            if self.Signals.PrevYon == "S":
                fark = self.Signals.SonFiyat - self.Signals.SonSFiyat
                if fark < 0:
                    self.Status.KazandiranSatisSayisi += 1
                elif fark > 0:
                    self.Status.KaybettirenSatisSayisi += 1
                else:
                    self.Status.NotrSatisSayisi += 1
                self.Status.KomisyonIslemSayisi += 1
                self.Signals.EmirStatus = 6
            self.Flags.BakiyeGuncelle = True
            self.Flags.KomisyonGuncelle = True
            self.Flags.DonguSonuIstatistikGuncelle = True
            self.Status.IslemSayisi += 1
            self.Status.FlatSayisi += 1
            self.Flags.FGerceklesti = True
        elif self.Signals.Sinyal == "P" or self.Signals.Sinyal == "":
            self.Signals.PrevPFiyat = self.Signals.SonPFiyat
            self.Signals.PrevPBarNo = self.Signals.SonPBarNo
            self.Signals.SonPFiyat = AnlikKapanisFiyati
            self.Signals.SonPBarNo = i
            if self.Signals.SonYon == "A":
                self.Signals.EmirStatus = 7
            if self.Signals.SonYon == "S":
                self.Signals.EmirStatus = 8
            if self.Signals.SonYon == "F":
                self.Signals.EmirStatus = 9
            self.Flags.BakiyeGuncelle = True
            self.Flags.KomisyonGuncelle = True
            self.Flags.DonguSonuIstatistikGuncelle = True
            self.Status.PassSayisi += 1
            self.Flags.PGerceklesti = True
        self.Status.KazandiranIslemSayisi = self.Status.KazandiranAlisSayisi + self.Status.KazandiranSatisSayisi
        self.Status.KaybettirenIslemSayisi = self.Status.KaybettirenAlisSayisi + self.Status.KaybettirenSatisSayisi
        self.Status.NotrIslemSayisi = self.Status.NotrAlisSayisi + self.Status.NotrSatisSayisi
        if self.Flags.AGerceklesti or self.Flags.SGerceklesti or self.Flags.FGerceklesti:
            self.Status.KardaBarSayisi = 0
            self.Status.ZarardaBarSayisi = 0
        if self.Status.IslemSayisi > 0:
            self.Flags.AnlikKarZararHesaplaEnabled = True
            self.Flags.KarAlYuzdeHesaplaEnabled = True
            self.Flags.IzleyenStopYuzdeHesaplaEnabled = True
            self.Flags.ZararKesYuzdeHesaplaEnabled = True
            self.Flags.KarAlSeviyeHesaplaEnabled = True
            self.Flags.ZararKesSeviyeHesaplaEnabled = True
        self.Flags.AGerceklesti = False
        self.Flags.SGerceklesti = False
        self.Flags.FGerceklesti = False
        self.Flags.PGerceklesti = False
        self.Lists.EmirKomutList[i] = self.Signals.EmirKomut
        self.Lists.EmirStatusList[i] = self.Signals.EmirStatus
        return result

    def sistem_yon_listesini_guncelle(self, BarIndex):
        result = 0
        i = BarIndex
        # BURASI YAPILACAK
        # Sistem.Yon[i] = self.Lists.YonList[i]
        return result

    def sistem_seviye_listesini_guncelle(self, BarIndex):
        result = 0
        i = BarIndex
        # BURASI YAPILACAK
        # Sistem.Seviye[i] = self.Lists.SeviyeList[i]
        return result

    def sinyal_listesini_guncelle(self, BarIndex):
        result = 0
        i = BarIndex
        if self.Signals.SonYon == "A":
            self.Lists.SinyalList[i] = 1.0
        elif self.Signals.SonYon == "S":
            self.Lists.SinyalList[i] = -1.0
        elif self.Signals.SonYon == "F":
            self.Lists.SinyalList[i] = 0.0
        return result

    def islem_listesini_guncelle(self, BarIndex):
        result = 0
        i = BarIndex
        self.Lists.IslemSayisiList[i] = self.Status.IslemSayisi
        self.Lists.AlisSayisiList[i] = self.Status.AlisSayisi
        self.Lists.SatisSayisiList[i] = self.Status.SatisSayisi
        self.Lists.FlatSayisiList[i] = self.Status.FlatSayisi
        self.Lists.PassSayisiList[i] = self.Status.PassSayisi
        self.Lists.VarlikAdedSayisiList[i] = self.Status.VarlikAdedSayisi
        self.Lists.KontratSayisiList[i] = self.Status.KontratSayisi
        self.Lists.KomisyonVarlikAdedSayisiList[i] = self.Status.KomisyonVarlikAdedSayisi
        self.Lists.KomisyonIslemSayisiList[i] = self.Status.KomisyonIslemSayisi
        self.Lists.KomisyonFiyatList[i] = self.Status.KomisyonFiyat
        self.Lists.KardaBarSayisiList[i] = self.Status.KardaBarSayisi
        self.Lists.ZarardaBarSayisiList[i] = self.Status.ZarardaBarSayisi
        return result

    def komisyon_listesini_guncelle(self, BarIndex):
        result = 0
        i = BarIndex
        self.Komisyon.hesapla(i)
        if self.Flags.KomisyonGuncelle:
            self.Flags.KomisyonGuncelle = False
        return result

    def bakiye_listesini_guncelle(self, BarIndex):
        result = 0
        i = BarIndex
        self.Bakiye.hesapla(i)
        if self.Flags.BakiyeGuncelle:
            self.Flags.BakiyeGuncelle = False
        return result

    def dongu_sonu_degiskenleri_setle(self, BarIndex):
        result = 0
        i = BarIndex
        return result

    def istatistikleri_hesapla(self):
        result = 0
        self.Statistics.hesapla()
        return result

    def istatistikleri_ekrana_yaz(self, PanelNo=1):
        result = 0
        self.Statistics.istatistikleri_ekrana_yaz(PanelNo)
        return result

    def getiri_istatistikleri_ekrana_yaz(self, PanelNo=2):
        result = 0
        self.Statistics.getiri_istatistikleri_ekrana_yaz(PanelNo)
        return result

    def istatistikleri_dosyaya_yaz(self, FileName):
        self.Statistics.istatistikleri_dosyaya_yaz(FileName)

    def optimizasyon_istatistiklerinin_basliklarini_dosyaya_yaz(self, FileName):
        self.Statistics.optimizasyon_istatistiklerinin_basliklarini_dosyaya_yaz(FileName)

    def optimizasyon_istatistiklerini_dosyaya_yaz(self, FileName, Index, TotalCount):
        self.Statistics.optimizasyon_istatistiklerini_dosyaya_yaz(FileName, Index, TotalCount)

    def is_son_yon_a(self):
        return self.Signals.SonYon == "A"

    def is_son_yon_s(self):
        return self.Signals.SonYon == "S"

    def is_son_yon_f(self):
        return self.Signals.SonYon == "F"

    def ideal_getiri_hesapla(self, KaymaMiktari=0.0, BaslangicTarihi="01/01/1900", BitisTarihi="01/01/2100"):
        if not self.Flags.IdealGetiriHesapla:
            return
        self.Flags.IdealGetiriHesaplandi = True
        # BURASI YAPILACAK
        # Sistem.GetiriHesapla(BaslangicTarihi, KaymaMiktari)
        # BURASI YAPILACAK
        # Sistem.GetiriMaxDDHesapla(BaslangicTarihi, BitisTarihi)

        # BURASI YAPILACAK
        # for i in range(len(Sistem.GetiriKZ)):
        #     self.Lists.GetiriKzSistem[i] = Sistem.GetiriKZ[i]
        #     self.Lists.GetiriKzNetSistem[i] = 0.0
        # self.Status.GetiriKzSistem = self.Lists.GetiriKzSistem[-1]
        # self.Status.GetiriKzNetSistem = 0.0

    def gun_sonu_poz_kapat(self, BarIndex, GunSonuPozKapatEnabled=True):
        i = BarIndex
        GunSonuPozKapatildi = False
        if GunSonuPozKapatEnabled:
            if i < self.BarCount - 1 and self.Date[i] != self.Date[i+1]:
                self.Signals.FlatOl = True
                GunSonuPozKapatildi = True
        return GunSonuPozKapatildi

    def gun_sonu_poz_kapat2(self, BarIndex, GunSonuPozKapatEnabled=True, Hour=18, Minute=0):
        i = BarIndex
        GunSonuPozKapatildi = False
        # if GunSonuPozKapatEnabled:
        #     if self.Time[i] == 18 and self.V[i].Date.minute >= 0:
        #         self.Signals.FlatOl = True
        #         GunSonuPozKapatildi = True
        return GunSonuPozKapatildi



    def sinyalleri_ekrana_ciz(self, k, SistemGetiriKZDahilEt=False):
        # myTrader = self
        # BarIndexList = myTrader.Lists.BarIndexList
        # SeviyeList = myTrader.Lists.SeviyeList
        # SinyalList = myTrader.Lists.SinyalList
        # KarZararPuanList = myTrader.Lists.KarZararPuanList
        # KarZararFiyatList = myTrader.Lists.KarZararFiyatList
        # KarZararFiyatYuzdeList = myTrader.Lists.KarZararFiyatYuzdeList
        # IslemSayisiList = myTrader.Lists.IslemSayisiList
        # AlisSayisiList = myTrader.Lists.AlisSayisiList
        # SatisSayisiList = myTrader.Lists.SatisSayisiList
        # FlatSayisiList = myTrader.Lists.FlatSayisiList
        # PassSayisiList = myTrader.Lists.PassSayisiList
        # KontratSayisiList = myTrader.Lists.KontratSayisiList
        # VarlikAdedSayisiList = myTrader.Lists.VarlikAdedSayisiList
        # KomisyonVarlikAdedSayisiList = myTrader.Lists.KomisyonVarlikAdedSayisiList
        # KomisyonIslemSayisiList = myTrader.Lists.KomisyonIslemSayisiList
        # KomisyonFiyatList = myTrader.Lists.KomisyonFiyatList
        # KardaBarSayisiList = myTrader.Lists.KardaBarSayisiList
        # ZarardaBarSayisiList = myTrader.Lists.ZarardaBarSayisiList
        # BakiyePuanList = myTrader.Lists.BakiyePuanList
        # BakiyeFiyatList = myTrader.Lists.BakiyeFiyatList
        # GetiriPuanList = myTrader.Lists.GetiriPuanList
        # GetiriFiyatList = myTrader.Lists.GetiriFiyatList
        # GetiriPuanYuzdeList = myTrader.Lists.GetiriPuanYuzdeList
        # GetiriFiyatYuzdeList = myTrader.Lists.GetiriFiyatYuzdeList
        # BakiyePuanNetList = myTrader.Lists.BakiyePuanNetList
        # BakiyeFiyatNetList = myTrader.Lists.BakiyeFiyatNetList
        # GetiriPuanNetList = myTrader.Lists.GetiriPuanNetList
        # GetiriFiyatNetList = myTrader.Lists.GetiriFiyatNetList
        # GetiriPuanYuzdeNetList = myTrader.Lists.GetiriPuanYuzdeNetList
        # GetiriFiyatYuzdeNetList = myTrader.Lists.GetiriFiyatYuzdeNetList
        # GetiriKz = myTrader.Lists.GetiriKz
        # GetiriKzNet = myTrader.Lists.GetiriKzNet
        # EmirKomutList = myTrader.Lists.EmirKomutList
        # EmirStatusList = myTrader.Lists.EmirStatusList
        # SistemGetiriKZ = Sistem.GetiriKZ if SistemGetiriKZDahilEt else Sistem.Liste(0)
        # Sistem.Cizgiler[k].Deger = Sistem.GetiriKZ
        # Sistem.Cizgiler[k].Aciklama = "Sistem.GetiriKZ "
        # k += 1
        # Sistem.Cizgiler[k].Deger = KarZararFiyatList
        # Sistem.Cizgiler[k].Aciklama = "KarZararFiyat"
        # k += 1
        # Sistem.Cizgiler[k].Deger = KarZararFiyatYuzdeList
        # Sistem.Cizgiler[k].Aciklama = "KarZararFiyatYuzdeList"
        # k += 1
        # Sistem.Cizgiler[k].Deger = GetiriKz
        # Sistem.Cizgiler[k].Aciklama = "GetiriKz"
        # k += 1
        # Sistem.Cizgiler[k].Deger = GetiriKzNet
        # Sistem.Cizgiler[k].Aciklama = "GetiriKzNet"
        # k += 1
        # Sistem.Cizgiler[k].Deger = GetiriFiyatList
        # Sistem.Cizgiler[k].Aciklama = "GetiriFiyat"
        # k += 1
        # Sistem.Cizgiler[k].Deger = BakiyeFiyatList
        # Sistem.Cizgiler[k].Aciklama = "BakiyeFiyat"
        # k += 1
        # Sistem.Cizgiler[k].Deger = GetiriFiyatNetList
        # Sistem.Cizgiler[k].Aciklama = "GetiriFiyatNet"
        # k += 1
        # Sistem.Cizgiler[k].Deger = BakiyeFiyatNetList
        # Sistem.Cizgiler[k].Aciklama = "BakiyeFiyatNet"
        # k += 1
        # Sistem.Cizgiler[k].Deger = KomisyonFiyatList
        # Sistem.Cizgiler[k].Aciklama = "KomisyonFiyatList"
        # k += 1
        # Sistem.Cizgiler[k].Deger = KomisyonIslemSayisiList
        # Sistem.Cizgiler[k].Aciklama = "KomisyonIslemSayisiList"
        # k += 1
        # Sistem.Cizgiler[k].Deger = IslemSayisiList
        # Sistem.Cizgiler[k].Aciklama = "IslemSayisiList "
        # k += 1
        # Sistem.Cizgiler[k].Deger = EmirKomutList
        # Sistem.Cizgiler[k].Aciklama = "EmirKomutList "
        # k += 1
        # Sistem.Cizgiler[k].Deger = EmirStatusList
        # Sistem.Cizgiler[k].Aciklama = "EmirStatusList "
        # k += 1
        # Sistem.Cizgiler[k].Deger = BarIndexList
        # Sistem.Cizgiler[k].Aciklama = "BarIndexList"
        # k += 1
        return k

    def get_bar_values_description(self):
        delimiter = ";"
        LogMessage = ""
        mode = 1
        if mode == 0:
            LogMessage = f'#  {"Column Names"},{No},{Date},{Time},{Open},{High},{Low},{Close},{Vol},{Size(Lot)}'
        else:
            LogMessage = f'#  {"Sutunlar":<12} {delimiter} {"No"} {delimiter} {"Date"} {delimiter} {"Time"} {delimiter} {"Open"} {delimiter} {"High"} {delimiter} {"Low"} {delimiter} {"Close"} {delimiter} {"Vol"} {delimiter} {"Size(Lot)"}'
        return LogMessage

    def get_bar_values_as_string(self, BarIndex):
        i = BarIndex
        delimiter = ";"
        LogMessage = ""
        mode = 1
        if mode == 0:
            LogMessage = f'{i:<5} 	 {self.Date[i].strftime("%Y.%m.%d %H:%M:%S"):<20} 	 {self.Open[i]:5.2f} 	 {self.High[i]:5.2f} 	 {self.Low[i]:5.2f} 	 {self.Close[i]:5.2f} 	 {self.Vol[i]:10.0f} 	 {self.Size[i]:5.0f}'
        else:
            LogMessage = f'{delimiter} {i:<5} {delimiter} {self.Date[i].strftime("%Y.%m.%d"):>10} {delimiter} {self.Date[i].strftime("%H:%M:%S"):>10} {delimiter} {self.Open[i]:10.2f} {delimiter} {self.High[i]:10.2f} {delimiter} {self.Low[i]:10.2f} {delimiter} {self.Close[i]:10.2f} {delimiter} {self.Vol[i]:10.0f} {delimiter} {self.Size[i]:10.0f} {delimiter}'
        return LogMessage

    def write_data_to_file_ohlc(self, FileName):
        myFileUtils = CFileUtils()
        myTimeUtils = CTimeUtils()
        myTimeUtils.initialize(self.EpochTime, self.DateTime, self.Date, self.Time, self.Open, self.High, self.Low, self.Close, self.Volume, self.Lot)
        myTimeUtils.gecen_zaman_bilgilerini_al()
        aciklama1 = "..."
        aciklama2 = "..."
        aciklama3 = "..."
        aciklama4 = "..."
        aciklama5 = "..."
        aciklama6 = "..."
        logFileFullName = FileName.strip()
        myFileUtils.reset().enable_logging().open_log_file(logFileFullName, False, False)
        logMessage = f'#  {"Aciklama (1)":<14}   ; {aciklama1.strip()}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Aciklama (2)":<14}   ; {aciklama2.strip()}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Aciklama (3)":<14}   ; {aciklama3.strip()}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Aciklama (4)":<14}   ; {aciklama4.strip()}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Aciklama (5)":<14}   ; {aciklama5.strip()}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Aciklama (6)":<14}   ; {aciklama6.strip()}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Log Zamani":<14}   ; {datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Sembol":<14}   ; {self.GrafikSembol}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Periyod":<14}   ; {self.GrafikPeriyot}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Bar Sayisi":<14}   ; {self.BarCount}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Ilk Bar Zamani":<10}   ; {self.V[0].Date.strftime("%Y.%m.%d %H:%M:%S")}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Son Bar Zamani":<10}   ; {self.V[-1].Date.strftime("%Y.%m.%d %H:%M:%S")}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Gecen Sure (A)":<10}   ; {myTimeUtils.gecen_sure("A"):0.1f}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Gecen Sure (G)":<10}   ; {myTimeUtils.gecen_sure("G"):0.0f}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = self.get_bar_values_description()
        myFileUtils.write_to_log_file(logMessage)
        for i in range(self.BarCount):
            logMessage = f'{self.get_bar_values_as_string(i)}'
            myFileUtils.write_to_log_file(logMessage)
        myFileUtils.close_log_file()
        pass

    def write_data_to_file_custom(self, FileName, DataLists, CaptionList):
        delimiter = ";"
        myFileUtils = CFileUtils()
        myTimeUtils = CTimeUtils()
        myTimeUtils.initialize(self.EpochTime, self.DateTime, self.Date, self.Time, self.Open, self.High, self.Low, self.Close, self.Volume, self.Lot)
        myTimeUtils.gecen_zaman_bilgilerini_al()
        aciklama1 = "..."
        aciklama2 = "..."
        aciklama3 = "..."
        aciklama4 = "..."
        aciklama5 = "..."
        aciklama6 = "..."
        logFileFullName = FileName.strip()
        myFileUtils.reset().enable_logging().open_log_file(logFileFullName, False, False)
        logMessage = f'#  {"Aciklama (1)":<14}   ; {aciklama1.strip()}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Aciklama (2)":<14}   ; {aciklama2.strip()}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Aciklama (3)":<14}   ; {aciklama3.strip()}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Aciklama (4)":<14}   ; {aciklama4.strip()}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Aciklama (5)":<14}   ; {aciklama5.strip()}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Aciklama (6)":<14}   ; {aciklama6.strip()}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Log Zamani":<14}   ; {datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Sembol":<14}   ; {self.GrafikSembol}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Periyod":<14}   ; {self.GrafikPeriyot}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Bar Sayisi":<14}   ; {self.BarCount}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Ilk Bar Zamani":<10}   ; {self.Date[0].strftime("%Y.%m.%d %H:%M:%S")}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Son Bar Zamani":<10}   ; {self.Date[-1].strftime("%Y.%m.%d %H:%M:%S")}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Gecen Sure (A)":<10}   ; {myTimeUtils.gecen_sure("A"):0.1f}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Gecen Sure (G)":<10}   ; {myTimeUtils.gecen_sure("G"):0.0f}\t'
        myFileUtils.write_to_log_file(logMessage)
        logMessage = f'#  {"Sutunlar":<12} {delimiter} {"No"}'
        for j in range(len(CaptionList)):
            logMessage = logMessage + delimiter + CaptionList[j]
        myFileUtils.write_to_log_file(logMessage)
        for i in range(self.BarCount):
            logMessage = f'{delimiter} {i:<5}'
            for j in range(len(DataLists)):
                column = DataLists[j]
                logMessage = logMessage + delimiter + str(column[i])
            myFileUtils.write_to_log_file(logMessage)
        myFileUtils.close_log_file()
        pass

    def reset_date_times(self):
        useLastBarDateTime = True
        self.StartDateTime = self.Date[0]
        self.StopDateTime = self.Date[self.BarCount - 1] if useLastBarDateTime else datetime.datetime.now()
        self.StartDate = self.StartDateTime
        self.StopDate = self.StopDateTime
        self.StartTime = self.StartDateTime
        self.StopTime = self.StopDateTime
        self.StartDateTimeStr = self.StartDateTime.strftime(self.DateTimeStringFormat)
        self.StopDateTimeStr = self.StopDateTime.strftime(self.DateTimeStringFormat)
        self.StartDateStr = self.StartDate.strftime(self.DateStringFormat)
        self.StopDateStr = self.StopDate.strftime(self.DateStringFormat)
        self.StartTimeStr = self.StartTime.strftime(self.TimeStringFormat)
        self.StopTimeStr = self.StopTime.strftime(self.TimeStringFormat)
        return self

    def set_date_times(self, StartDateTime, StopDateTime):
        pass

    def set_date_times2(self, StartDate, StartTime, StopDate, StopTime):
        date1 = StartDate.strip()
        time1 = StartTime.strip()
        date2 = StopDate.strip()
        time2 = StopTime.strip()
        dateTime1 = date1 + " " + time1
        dateTime2 = date2 + " " + time2
        suffixDate = "09:30:00"
        prefixTime = "01.01.1900"
        self.StartDateTime = self.TimeUtils.get_date_time(date1, time1)
        self.StopDateTime = self.TimeUtils.get_date_time(date2, time2)
        self.StartDate = self.TimeUtils.get_date_time(date1 + " " + suffixDate)
        self.StopDate = self.TimeUtils.get_date_time(date2 + " " + suffixDate)
        self.StartTime = self.TimeUtils.get_date_time(prefixTime + " " + time1)
        self.StopTime = self.TimeUtils.get_date_time(prefixTime + " " + time2)
        self.StartDateTimeStr = self.StartDateTime.strftime(self.DateTimeStringFormat)
        self.StopDateTimeStr = self.StopDateTime.strftime(self.DateTimeStringFormat)
        self.StartDateStr = self.StartDate.strftime(self.DateStringFormat)
        self.StopDateStr = self.StopDate.strftime(self.DateStringFormat)
        self.StartTimeStr = self.StartTime.strftime(self.TimeStringFormat)
        self.StopTimeStr = self.StopTime.strftime(self.TimeStringFormat)
        return self

    def set_date_times_from_strings(self, StartDateTime, StopDateTime):
        dateTime1 = StartDateTime.strip()
        dateTime2 = StopDateTime.strip()
        date1 = dateTime1[0:10]
        time1 = dateTime1[11:]
        date2 = dateTime2[0:10]
        time2 = dateTime2[11:]
        suffixDate = "09:30:00"
        prefixTime = "01.01.1900"
        self.StartDateTime = self.TimeUtils.get_date_time(dateTime1)
        self.StopDateTime = self.TimeUtils.get_date_time(dateTime2)
        self.StartDate = self.TimeUtils.get_date_time(date1 + " " + suffixDate)
        self.StopDate = self.TimeUtils.get_date_time(date2 + " " + suffixDate)
        self.StartTime = self.TimeUtils.get_date_time(prefixTime + " " + time1)
        self.StopTime = self.TimeUtils.get_date_time(prefixTime + " " + time2)
        self.StartDateTimeStr = self.StartDateTime.strftime(self.DateTimeStringFormat)
        self.StopDateTimeStr = self.StopDateTime.strftime(self.DateTimeStringFormat)
        self.StartDateStr = self.StartDate.strftime(self.DateStringFormat)
        self.StopDateStr = self.StopDate.strftime(self.DateStringFormat)
        self.StartTimeStr = self.StartTime.strftime(self.TimeStringFormat)
        self.StopTimeStr = self.StopTime.strftime(self.TimeStringFormat)
        return self

    def set_date_time(self, StartDate, StartTime):
        StartDateTime = StartDate + " " + StartTime
        return self.set_date_time_from_string(StartDateTime)

    def set_date_time_from_string(self, StartDateTime):
        return self.set_date_times_from_strings(StartDateTime, datetime.datetime.now().strftime(self.DateTimeStringFormat))

    def islem_zaman_filtresi_uygula(self, BarIndex, FilterMode, IsTradeEnabled, IsPozKapatEnabled, CheckResult):
        i = BarIndex
        BarDateTime = self.DateTime[i]
        startDateTime = self.StartDateTimeStr
        stopDateTime = self.StopDateTimeStr
        startDate = self.StartDateStr
        stopDate = self.StopDateStr
        startTime = self.StartTimeStr
        stopTime = self.StopTimeStr
        nowDateTime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        nowDate = datetime.datetime.now().strftime("%d.%m.%Y")
        nowTime = datetime.datetime.now().strftime("%H:%M:%S")
        useTimeFiltering = self.Signals.TimeFilteringEnabled
        if useTimeFiltering:
            if i == self.BarCount - 1:
                s = ""
                s += f'  {startDateTime}\n'
                s += f'  {stopDateTime}\n'
                s += f'  {startDate}\n'
                s += f'  {stopDate}\n'
                s += f'  {startTime}\n'
                s += f'  {stopTime}\n'
                s += f'  {nowDateTime}\n'
                s += f'  {nowDate}\n'
                s += f'  {nowTime}\n'
                s += f'  FilterMode = {FilterMode}\n'
                s += '  CTrader::IslemZamanFiltresiUygula\n'
            if FilterMode == 0:
                IsTradeEnabled.value = True
                CheckResult.value = 0
            elif FilterMode == 1:
                if self.TimeUtils.check_bar_time_with(i, startTime) >= 0 and self.TimeUtils.check_bar_time_with(i, stopTime) < 0:
                    IsTradeEnabled.value = True
                    CheckResult.value = 0
                elif self.TimeUtils.check_bar_time_with(i, startTime) < 0:
                    if not self.is_son_yon_f():
                        IsPozKapatEnabled.value = True
                    CheckResult.value = -1
                elif self.TimeUtils.check_bar_time_with(i, stopTime) >= 0:
                    if not self.is_son_yon_f():
                        IsPozKapatEnabled.value = True
                    CheckResult.value = 1
            elif FilterMode == 2:
                if self.TimeUtils.check_bar_date_with(i, startDate) >= 0 and self.TimeUtils.check_bar_date_with(i, stopDate) < 0:
                    IsTradeEnabled.value = True
                    CheckResult.value = 0
                elif self.TimeUtils.check_bar_date_with(i, startDate) < 0:
                    if not self.is_son_yon_f():
                        IsPozKapatEnabled.value = True
                    CheckResult.value = -1
                elif self.TimeUtils.check_bar_date_with(i, stopDate) >= 0:
                    if not self.is_son_yon_f():
                        IsPozKapatEnabled.value = True
                    CheckResult.value = 1
            elif FilterMode == 3:
                if self.TimeUtils.check_bar_date_time_with(i, startDateTime) >= 0 and self.TimeUtils.check_bar_date_time_with(i, stopDateTime) < 0:
                    IsTradeEnabled.value = True
                    CheckResult.value = 0
                elif self.TimeUtils.check_bar_date_time_with(i, startDateTime) < 0:
                    if not self.is_son_yon_f():
                        IsPozKapatEnabled.value = True
                    CheckResult.value = -1
                elif self.TimeUtils.check_bar_date_time_with(i, stopDateTime) >= 0:
                    if not self.is_son_yon_f():
                        IsPozKapatEnabled.value = True
                    CheckResult.value = 1
            elif FilterMode == 4:
                if self.TimeUtils.check_bar_time_with(i, startTime) >= 0:
                    IsTradeEnabled.value = True
                    CheckResult.value = 0
                elif self.TimeUtils.check_bar_time_with(i, startTime) < 0:
                    if not self.is_son_yon_f():
                        IsPozKapatEnabled.value = True
                    CheckResult.value = -1
            elif FilterMode == 5:
                if self.TimeUtils.check_bar_date_with(i, startDate) >= 0:
                    IsTradeEnabled.value = True
                    CheckResult.value = 0
                elif self.TimeUtils.check_bar_date_with(i, startDate) < 0:
                    if not self.is_son_yon_f():
                        IsPozKapatEnabled.value = True
                    CheckResult.value = -1
            elif FilterMode == 6:
                if self.TimeUtils.check_bar_date_time_with(i, startDateTime) >= 0:
                    IsTradeEnabled.value = True
                    CheckResult.value = 0
                elif self.TimeUtils.check_bar_date_time_with(i, startDateTime) < 0:
                    if not self.is_son_yon_f():
                        IsPozKapatEnabled.value = True
                    CheckResult.value = -1
        return 0

    def emir_oncesi_dongu_foksiyonlarini_calistir(self, bar_index):
        i = bar_index

        self.dongu_basi_degiskenleri_resetle(i)

        self.dongu_basi_degiskenleri_guncelle(i)

        if (i < 1):
            return 0

        self.anlik_kar_zarar_hesapla(i)

        self.emirleri_resetle(i)

        isYeniGun = (self.Date[i] != self.Date[i-1])
        if (isYeniGun):
            pass #.DikeyCizgiEkle(i, Color.DimGray, 2, 2);

        # isYeniSaat = (self.Time[i].Hour != self.Time[i-1].Hour)
        # if (isYeniSaat):
        #     pass #.DikeyCizgiEkle(i, Color.DimGray, 2, 2);

        if (self.Signals.GunSonuPozKapatildi):
            self.Signals.GunSonuPozKapatildi = False

        if (self.Signals.KarAlindi or self.Signals.ZararKesildi or self.Signals.FlatOlundu):
            self.Signals.KarAlindi = False
            self.Signals.ZararKesildi = False
            self.Signals.FlatOlundu = False
            self.Signals.PozAcilabilir = False

        if (self.Signals.PozAcilabilir == False):
            self.Signals.PozAcilabilir = True
            self.Signals.PozAcildi = False

        return 0

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
        # // Kullanim: mySystem.IslemZamanFiltresiUygula(, i, ref
        # Al, ref
        # Sat, ref
        # FlatOl, ref
        # PasGec, ref
        # KarAl, ref
        # ZararKes, 0);
        # // mySystem.EmirleriSetle(, i, Al, Sat, FlatOl, PasGec, KarAl, ZararKes);
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
        #     myTrader.IslemZamanFiltresiUygula(, BarIndex, FilterMode, ref
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
        # // Kullanım: mySystem.EmirleriSetle(, i, Al, Sat, FlatOl, PasGec, KarAl, ZararKes);
        # // mySystem.IslemZamanFiltresiUygula(, i);
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
        #     myTrader.IslemZamanFiltresiUygula(, BarIndex, FilterMode, ref
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
        i = bar_index

        # // KarAl = myTrader.KarAlZararKes.SonFiyataGoreKarAlSeviyeHesapla(, i, 5, 50, 1000) != 0 ? true: false;
        #
        # // ZararKes = myTrader.KarAlZararKes.SonFiyataGoreZararKesSeviyeHesapla(, i, -1, -10,
        #                                                                         1000) != 0 ? true: false;
        #
        # // KarAl = myTrader.Signals.KarAlEnabled ? KarAl: false;
        #
        # // ZararKes = myTrader.Signals.ZararKesEnabled ? ZararKes: false;
        #
        # myTrader.emirleri_setle(, i, Al, Sat, FlatOl, PasGec, KarAl, ZararKes);

        self.Signals.GunSonuPozKapatildi = self.gun_sonu_poz_kapat(i, self.Signals.GunSonuPozKapatEnabled)

        self.emirleri_uygula(i)

        if (self.Signals.KarAlindi == False and self.Signals.KarAl):
            self.Signals.KarAlindi = True

        if (self.Signals.ZararKesildi == False and self.Signals.ZararKes):
            self.Signals.ZararKesildi = True

        if (self.Signals.FlatOlundu == False and self.Signals.FlatOl):
            self.Signals.FlatOlundu = True

        self.sistem_yon_listesini_guncelle(i)

        self.sistem_seviye_listesini_guncelle(i)

        self.sinyal_listesini_guncelle(i)

        self.islem_listesini_guncelle(i)

        self.komisyon_listesini_guncelle(i)

        self.bakiye_listesini_guncelle(i)

        self.dongu_sonu_degiskenleri_setle(i)

        pass

    def update_data_frame(self):
        # Clear DataFrame
        self._df = None

        # Create DataFrame with OHLCV data as columns
        self._df = pd.DataFrame({
            'EpochTime': self.EpochTime,
            'DateTime': self.DateTime,
            'Date': self.Date,
            'Time': self.Time,
            'Open': self.Open,
            'High': self.High,
            'Low': self.Low,
            'Close': self.Close,
            'Volume': self.Volume,
            'Lot': self.Lot
        })
        
        # Add all lists and attributes to DataFrame
        if self.BarCount > 0:
            # Create BarIndex list if it doesn't exist
            if not hasattr(self.Lists, 'BarIndexList') or len(self.Lists.BarIndexList) == 0:
                self.Lists.BarIndexList = list(range(self.BarCount))
            
            # Add BarCount and all trading lists as columns to DataFrame
            self._df['BarIndex'] = self.Lists.BarIndexList if len(self.Lists.BarIndexList) == self.BarCount else list(range(self.BarCount))
            self._df['Yon'] = self.Lists.YonList if len(self.Lists.YonList) == self.BarCount else [''] * self.BarCount
            self._df['Seviye'] = self.Lists.SeviyeList if len(self.Lists.SeviyeList) == self.BarCount else [0.0] * self.BarCount
            self._df['Sinyal'] = self.Lists.SinyalList if len(self.Lists.SinyalList) == self.BarCount else [0.0] * self.BarCount
            self._df['KarZararPuan'] = self.Lists.KarZararPuanList if len(self.Lists.KarZararPuanList) == self.BarCount else [0.0] * self.BarCount
            self._df['KarZararFiyat'] = self.Lists.KarZararFiyatList if len(self.Lists.KarZararFiyatList) == self.BarCount else [0.0] * self.BarCount
            self._df['KarZararFiyatYuzde'] = self.Lists.KarZararFiyatYuzdeList if len(self.Lists.KarZararFiyatYuzdeList) == self.BarCount else [0.0] * self.BarCount
            self._df['KarAl'] = self.Lists.KarAlList if len(self.Lists.KarAlList) == self.BarCount else [0.0] * self.BarCount
            self._df['IzleyenStop'] = self.Lists.IzleyenStopList if len(self.Lists.IzleyenStopList) == self.BarCount else [0.0] * self.BarCount
            self._df['IslemSayisi'] = self.Lists.IslemSayisiList if len(self.Lists.IslemSayisiList) == self.BarCount else [0.0] * self.BarCount
            self._df['AlisSayisi'] = self.Lists.AlisSayisiList if len(self.Lists.AlisSayisiList) == self.BarCount else [0.0] * self.BarCount
            self._df['SatisSayisi'] = self.Lists.SatisSayisiList if len(self.Lists.SatisSayisiList) == self.BarCount else [0.0] * self.BarCount
            self._df['FlatSayisi'] = self.Lists.FlatSayisiList if len(self.Lists.FlatSayisiList) == self.BarCount else [0.0] * self.BarCount
            self._df['PassSayisi'] = self.Lists.PassSayisiList if len(self.Lists.PassSayisiList) == self.BarCount else [0.0] * self.BarCount
            self._df['KontratSayisi'] = self.Lists.KontratSayisiList if len(self.Lists.KontratSayisiList) == self.BarCount else [0.0] * self.BarCount
            self._df['VarlikAdedSayisi'] = self.Lists.VarlikAdedSayisiList if len(self.Lists.VarlikAdedSayisiList) == self.BarCount else [0.0] * self.BarCount
            self._df['KomisyonVarlikAdedSayisi'] = self.Lists.KomisyonVarlikAdedSayisiList if len(self.Lists.KomisyonVarlikAdedSayisiList) == self.BarCount else [0.0] * self.BarCount
            self._df['KomisyonIslemSayisi'] = self.Lists.KomisyonIslemSayisiList if len(self.Lists.KomisyonIslemSayisiList) == self.BarCount else [0.0] * self.BarCount
            self._df['KomisyonFiyat'] = self.Lists.KomisyonFiyatList if len(self.Lists.KomisyonFiyatList) == self.BarCount else [0.0] * self.BarCount
            self._df['KardaBarSayisi'] = self.Lists.KardaBarSayisiList if len(self.Lists.KardaBarSayisiList) == self.BarCount else [0.0] * self.BarCount
            self._df['ZarardaBarSayisi'] = self.Lists.ZarardaBarSayisiList if len(self.Lists.ZarardaBarSayisiList) == self.BarCount else [0.0] * self.BarCount
            self._df['BakiyePuan'] = self.Lists.BakiyePuanList if len(self.Lists.BakiyePuanList) == self.BarCount else [0.0] * self.BarCount
            self._df['BakiyeFiyat'] = self.Lists.BakiyeFiyatList if len(self.Lists.BakiyeFiyatList) == self.BarCount else [0.0] * self.BarCount
            self._df['GetiriPuan'] = self.Lists.GetiriPuanList if len(self.Lists.GetiriPuanList) == self.BarCount else [0.0] * self.BarCount
            self._df['GetiriFiyat'] = self.Lists.GetiriFiyatList if len(self.Lists.GetiriFiyatList) == self.BarCount else [0.0] * self.BarCount
            self._df['GetiriPuanYuzde'] = self.Lists.GetiriPuanYuzdeList if len(self.Lists.GetiriPuanYuzdeList) == self.BarCount else [0.0] * self.BarCount
            self._df['GetiriFiyatYuzde'] = self.Lists.GetiriFiyatYuzdeList if len(self.Lists.GetiriFiyatYuzdeList) == self.BarCount else [0.0] * self.BarCount
            self._df['BakiyePuanNet'] = self.Lists.BakiyePuanNetList if len(self.Lists.BakiyePuanNetList) == self.BarCount else [0.0] * self.BarCount
            self._df['BakiyeFiyatNet'] = self.Lists.BakiyeFiyatNetList if len(self.Lists.BakiyeFiyatNetList) == self.BarCount else [0.0] * self.BarCount
            self._df['GetiriPuanNet'] = self.Lists.GetiriPuanNetList if len(self.Lists.GetiriPuanNetList) == self.BarCount else [0.0] * self.BarCount
            self._df['GetiriFiyatNet'] = self.Lists.GetiriFiyatNetList if len(self.Lists.GetiriFiyatNetList) == self.BarCount else [0.0] * self.BarCount
            self._df['GetiriPuanYuzdeNet'] = self.Lists.GetiriPuanYuzdeNetList if len(self.Lists.GetiriPuanYuzdeNetList) == self.BarCount else [0.0] * self.BarCount
            self._df['GetiriFiyatYuzdeNet'] = self.Lists.GetiriFiyatYuzdeNetList if len(self.Lists.GetiriFiyatYuzdeNetList) == self.BarCount else [0.0] * self.BarCount
            self._df['GetiriKz'] = self.Lists.GetiriKz if len(self.Lists.GetiriKz) == self.BarCount else [0.0] * self.BarCount
            self._df['GetiriKzNet'] = self.Lists.GetiriKzNet if len(self.Lists.GetiriKzNet) == self.BarCount else [0.0] * self.BarCount
            self._df['GetiriKzSistem'] = self.Lists.GetiriKzSistem if len(self.Lists.GetiriKzSistem) == self.BarCount else [0.0] * self.BarCount
            self._df['GetiriKzNetSistem'] = self.Lists.GetiriKzNetSistem if len(self.Lists.GetiriKzNetSistem) == self.BarCount else [0.0] * self.BarCount
            self._df['EmirKomut'] = self.Lists.EmirKomutList if len(self.Lists.EmirKomutList) == self.BarCount else [0.0] * self.BarCount
            self._df['EmirStatus'] = self.Lists.EmirStatusList if len(self.Lists.EmirStatusList) == self.BarCount else [0.0] * self.BarCount
            
            # Add metadata as DataFrame attributes (not columns, to avoid repetition)
            self._df.attrs.update({
                'BakiyeInitialized': self.BakiyeInitialized,
                'ExecutionStepNumber': self.ExecutionStepNumber,
                'LastResetTime': self.LastResetTime,
                'LastExecutionTime': self.LastExecutionTime,
                'LastExecutionTimeStart': self.LastExecutionTimeStart,
                'LastExecutionTimeStop': self.LastExecutionTimeStop,
                'LastStatisticsCalculationTime': self.LastStatisticsCalculationTime,
                'ExecutionTimeInMSec': self.ExecutionTimeInMSec,
                'DateTimeStringFormat': self.DateTimeStringFormat,
                'DateStringFormat': self.DateStringFormat,
                'TimeStringFormat': self.TimeStringFormat,
                'StartDateTime': self.StartDateTime,
                'StopDateTime': self.StopDateTime,
                'StartDate': self.StartDate,
                'StopDate': self.StopDate,
                'StartTime': self.StartTime,
                'StopTime': self.StopTime,
                'StartDateTimeStr': self.StartDateTimeStr,
                'StopDateTimeStr': self.StopDateTimeStr,
                'StartDateStr': self.StartDateStr,
                'StopDateStr': self.StopDateStr,
                'StartTimeStr': self.StartTimeStr,
                'StopTimeStr': self.StopTimeStr,
                'EnableDateTime': self.EnableDateTime,
                'DisableDateTime': self.DisableDateTime,
                'EnableDate': self.EnableDate,
                'DisableDate': self.DisableDate,
                'EnableTime': self.EnableTime,
                'DisableTime': self.DisableTime,
                'EnableDateTimeStr': self.EnableDateTimeStr,
                'DisableDateTimeStr': self.DisableDateTimeStr,
                'EnableDateStr': self.EnableDateStr,
                'DisableDateStr': self.DisableDateStr,
                'EnableTimeStr': self.EnableTimeStr,
                'DisableTimeStr': self.DisableTimeStr
            })
            
            # Add class instance names as metadata attributes (not columns, to avoid repetition)
            self._df.attrs.update({
                'SignalsClass': str(type(self.Signals).__name__),
                'StatusClass': str(type(self.Status).__name__),
                'FlagsClass': str(type(self.Flags).__name__),
                'ListsClass': str(type(self.Lists).__name__),
                'KarZararClass': str(type(self.KarZarar).__name__),
                'KomisyonClass': str(type(self.Komisyon).__name__),
                'BakiyeClass': str(type(self.Bakiye).__name__),
                'VarlikManagerClass': str(type(self.VarlikManager).__name__ if self.VarlikManager else 'None'),
                'StatisticsClass': str(type(self.Statistics).__name__),
                'KarAlZararKesClass': str(type(self.KarAlZararKes).__name__),
                'TimeFilterClass': str(type(self.TimeFilter).__name__),
                'TimeUtilsClass': str(type(self.TimeUtils).__name__)
            })

    def write_data_frame_to_file(self, file_name):
        """
        DataFrame'deki verileri tablo formatında dosyaya yazar
        """
        if self._df is None or self._df.empty:
            print("DataFrame boş veya None. Önce update_data_frame() methodunu çağırın.")
            return
        
        try:
            # Dosya uzantısına göre format belirle
            file_name = file_name.strip()
            file_extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
            
            # CSV formatında kaydet
            if file_extension == 'csv' or file_extension == '':
                if file_extension == '':
                    file_name += '.csv'
                self._df.to_csv(file_name, index=False, encoding='utf-8-sig')
                print(f"DataFrame CSV formatında kaydedildi: {file_name}")
            
            # Excel formatında kaydet
            elif file_extension in ['xlsx', 'xls']:
                try:
                    # Önce openpyxl ile dene
                    self._df.to_excel(file_name, index=False, engine='openpyxl')
                    print(f"DataFrame Excel formatında kaydedildi: {file_name}")
                except ImportError:
                    print("openpyxl kütüphanesi bulunamadı. Excel yerine CSV formatında kaydediliyor...")
                    csv_file_name = file_name.replace('.xlsx', '.csv').replace('.xls', '.csv')
                    self._df.to_csv(csv_file_name, index=False, encoding='utf-8-sig')
                    print(f"DataFrame CSV formatında kaydedildi: {csv_file_name}")
                except Exception as e:
                    print(f"Excel kaydetme hatası: {str(e)}")
                    print("Excel yerine CSV formatında kaydediliyor...")
                    csv_file_name = file_name.replace('.xlsx', '.csv').replace('.xls', '.csv')
                    self._df.to_csv(csv_file_name, index=False, encoding='utf-8-sig')
                    print(f"DataFrame CSV formatında kaydedildi: {csv_file_name}")
            
            # JSON formatında kaydet
            elif file_extension == 'json':
                self._df.to_json(file_name, orient='records', date_format='iso', indent=2)
                print(f"DataFrame JSON formatında kaydedildi: {file_name}")
            
            # HTML tablo formatında kaydet
            elif file_extension == 'html':
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Trading Data</title>
    <style>
        table {{ border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .numeric {{ text-align: right; }}
    </style>
</head>
<body>
    <h2>Trading Data - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h2>
    {self._df.to_html(index=False, classes='table table-striped', escape=False)}
</body>
</html>
"""
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"DataFrame HTML formatında kaydedildi: {file_name}")
            
            # Varsayılan olarak CSV formatında kaydet
            else:
                csv_file_name = file_name + '.csv'
                self._df.to_csv(csv_file_name, index=False, encoding='utf-8-sig')
                print(f"Bilinmeyen format, CSV olarak kaydedildi: {csv_file_name}")
                
        except Exception as e:
            print(f"Dosya yazma hatası: {str(e)}")
            
    def write_data_frame_summary_to_file(self, file_name):
        """
        DataFrame'in özet bilgilerini dosyaya yazar
        """
        if self._df is None or self._df.empty:
            print("DataFrame boş veya None. Önce update_data_frame() methodunu çağırın.")
            return
            
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write("=== DATAFRAME ÖZET BİLGİLERİ ===\n")
                f.write(f"Oluşturulma Tarihi: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Toplam Satır Sayısı: {len(self._df)}\n")
                f.write(f"Toplam Sütun Sayısı: {len(self._df.columns)}\n")
                f.write(f"DataFrame Boyutu: {self._df.shape}\n\n")
                
                f.write("=== SÜTUN BİLGİLERİ ===\n")
                for i, col in enumerate(self._df.columns, 1):
                    f.write(f"{i:3d}. {col}\n")
                
                f.write("\n=== VERİ TİPLERİ ===\n")
                f.write(str(self._df.dtypes))
                f.write("\n\n=== İLK 10 SATIR ===\n")
                f.write(str(self._df.head(10)))
                f.write("\n\n=== SON 10 SATIR ===\n")
                f.write(str(self._df.tail(10)))
                
            print(f"DataFrame özet bilgileri kaydedildi: {file_name}")
            
        except Exception as e:
            print(f"Özet dosya yazma hatası: {str(e)}")


    # def reset_date_times(self):
    #     pass
    #
    # def set_date_times(self, dt1, dt2):
    #     pass
    #
    # def is_son_yon_a(self):
    #     pass
    #
    # def is_son_yon_s(self):
    #     pass
    #
    # def is_son_yon_f(self):
    #     pass
    #
    #
    # def dongu_basi_degiskenleri_guncelle(self, i):
    #     pass
    #
    # def anlik_kar_zarar_hesapla(self, i):
    #     pass
    #
    #
    #
    # def gun_sonu_poz_kapat(self, i, enabled):
    #     pass
    #
    # def emirleri_uygula(self, i):
    #     pass
    #
    # def _yon_listesini_guncelle(self, i):
    #     pass
    #
    # def _seviye_listesini_guncelle(self, i):
    #     pass
    #
    # def sinyal_listesini_guncelle(self, i):
    #     pass
    #
    # def islem_listesini_guncelle(self, i):
    #     pass
    #
    # def komisyon_listesini_guncelle(self, i):
    #     pass
    #
    # def bakiye_listesini_guncelle(self, i):
    #     pass
    #
    # def dongu_sonu_degiskenleri_setle(self, i):
    #     pass
    #
    # def start(self):
    #     pass
    #
    # def stop(self):
    #     pass
    #
    # def ideal_getiri_hesapla(self):
    #     pass
    #
    # def istatistikleri_hesapla(self):
    #     pass
    #
    # def istatistikleri_ekrana_yaz(self, val):
    #     pass
    #
    # def getiri_istatistikleri_ekrana_yaz(self, val):
    #     pass
    #
    # def istatistikleri_dosyaya_yaz(self, filename):
    #     pass
    #
    # def sinyalleri_ekrana_ciz(self, k):
    #     return k
    #
    # def optimizasyon_istatistiklerinin_basliklarini_dosyaya_yaz(self, filename):
    #     pass
    #
    # def optimizasyon_istatistiklerini_dosyaya_yaz(self, filename, run_index, total_runs):
    #     pass