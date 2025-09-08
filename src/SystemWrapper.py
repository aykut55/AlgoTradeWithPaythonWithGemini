import os

from src.Base import CBase
from src.VarlikManager import CVarlikManager
from src.Trader import CTrader
from src.Utils import CUtils
from src.TimeUtils import CTimeUtils
from src.BarUtils import CBarUtils
from src.FileUtils import CFileUtils
from src.ExcelFileHandler import CExcelFileHandler
from src.SharedMemory import CSharedMemory
from src.ConfigManager import CConfigManager
from src.IndicatorManager import CIndicatorManager

class SystemWrapper(CBase):
    def __init__(self):
        # self.GrafikSembol = ""
        # self.GrafikPeriyot = ""
        # self.SistemAdi = ""

        self.myVarlik = None
        self.myTraders = []  # List to hold multiple trader objects, 100 trader objects by default
        self.myUtils = None
        self.myTimeUtils = None
        self.myBarUtils = None
        self.myFileUtils = None
        self.myExcelUtils = None
        self.mySharedMemory = None
        self.myConfig = None
        self.myIndicators = None

        # self.HisseSayisi = 0
        # self.KontratSayisi = 10
        # self.KomisyonCarpan = 0.0
        # self.VarlikAdedCarpani = 1
        #
        # self.InputsDir = ""
        # self.OutputsDir = ""
        # self.ParamsInputFileName = ""
        # self.IstatistiklerOutputFileName = ""
        # self.IstatistiklerOptOutputFileName = ""
        #
        # self.bUseParamsFromInputFile = False
        # self.bOptEnabled = False
        # self.bIdealGetiriHesapla = True
        # self.bIstatistikleriHesapla = True
        # self.bIstatistikleriEkranaYaz = True
        # self.bGetiriIstatistikleriEkranaYaz = True
        # self.bIstatistikleriDosyayaYaz = True
        # self.bOptimizasyonIstatistiklerininBasliklariniDosyayaYaz = True
        # self.bOptimizasyonIstatistikleriniDosyayaYaz = True
        # self.bSinyalleriEkranaCiz = True
        # self.CurrentRunIndex = 0
        # self.TotalRunCount = 1
        #
        # self.Al = False
        # self.Sat = False
        # self.FlatOl = False
        # self.PasGec = False
        # self.KarAl = False
        # self.ZararKes = False
        #
        # self.InputParamsCount = 50
        # self.InputParams = ["" for _ in range(50)]

    def create_modules(self, trader_count=1):
        self.myVarlik = CVarlikManager()
        self.myTraders = [CTrader(i) for i in range(trader_count)]
        self.myUtils = CUtils()
        self.myTimeUtils = CTimeUtils()
        self.myBarUtils = CBarUtils()
        self.myFileUtils = CFileUtils()
        self.myExcelUtils = CExcelFileHandler()
        self.mySharedMemory = CSharedMemory()
        self.myConfig = CConfigManager()
        self.myIndicators = CIndicatorManager()
        return self

    def initialize(self, Open, High, Low, Close, Volume, Lot):
        # self.GrafikSembol = Sistem.Sembol
        # self.GrafikPeriyot = Sistem.Periyot
        # self.SistemAdi = Sistem.Name

        self.set_data(Open, High, Low, Close, Volume, Lot)

        if self.myVarlik:
            self.myVarlik.initialize()

        for trader in self.myTraders:
            if trader:
                trader.GrafikSembol = "GrafikSembol Setlenecek"
                trader.GrafikPeriyot = "GrafikPeriyot Setlenecek"
                trader.SistemAdi = "SistemAdi Setlenecek"
                trader.initialize(Open, High, Low, Close, Volume, Lot, self.myVarlik)
        
        if self.myUtils:
            self.myUtils.initialize()
        
        if self.myTimeUtils:
            self.myTimeUtils.initialize(Open, High, Low, Close, Volume, Lot)
        
        if self.myBarUtils:
            self.myBarUtils.initialize(Open, High, Low, Close, Volume, Lot)
        
        if self.myIndicators:
            self.myIndicators.initialize(Open, High, Low, Close, Volume, Lot)
        
        return self

    def reset(self):
        if self.myVarlik:
            self.myVarlik.reset()
        
        for trader in self.myTraders:
            if trader:
                trader.reset()
        
        if self.myUtils:
            self.myUtils.reset()
        
        if self.myTimeUtils:
            self.myTimeUtils.reset()
        
        if self.myBarUtils:
            self.myBarUtils.reset()
        
        if self.myFileUtils:
            self.myFileUtils.reset()
        
        if self.myExcelUtils:
            self.myExcelUtils.reset()
        
        if self.mySharedMemory:
            self.mySharedMemory.reset()
        
        if self.myConfig:
            self.myConfig.reset()
        
        if self.myIndicators:
            self.myIndicators.reset()

        # for i in range(self.InputParamsCount):
        #     self.InputParams[i] = ""

    def initialize_params_with_defaults(self):
        # self.HisseSayisi = 0
        # self.KontratSayisi = 10
        # self.KomisyonCarpan = 0.0
        # self.VarlikAdedCarpani = 1
        #
        # self.InputsDir = "Aykut/Exports/"
        # self.OutputsDir = "Aykut/Exports/"
        # self.ParamsInputFileName = self.InputsDir + self.SistemAdi + "_params.txt"
        # self.IstatistiklerOutputFileName = self.OutputsDir + "Istatistikler.csv"
        # self.IstatistiklerOptOutputFileName = self.OutputsDir + "IstatistiklerOpt.csv"
        #
        # self.bUseParamsFromInputFile = False
        # self.bOptEnabled = False
        # self.bIdealGetiriHesapla = True
        # self.bIstatistikleriHesapla = True
        # self.bIstatistikleriEkranaYaz = True
        # self.bGetiriIstatistikleriEkranaYaz = True
        # self.bIstatistikleriDosyayaYaz = True
        # self.bOptimizasyonIstatistiklerininBasliklariniDosyayaYaz = False
        # self.bOptimizasyonIstatistikleriniDosyayaYaz = False
        # self.bSinyalleriEkranaCiz = True
        #
        # self.CurrentRunIndex = 0
        # self.TotalRunCount = 1
        #
        # self.myVarlik.set_kontrat_params_fx_ons_altin_micro(Sistem, KontratSayisi=1, VarlikAdedCarpani=1).set_komisyon_params(Sistem, KomisyonCarpan=0.0)
        #
        for trader in self.myTraders:
            if trader:
                trader.Signals.KarAlEnabled = False
                trader.Signals.ZararKesEnabled = False
                trader.Signals.KarAlindi = False
                trader.Signals.ZararKesildi = False
                trader.Signals.FlatOlundu = False
                trader.Signals.PozAcilabilir = False
                trader.Signals.PozAcildi = False
                trader.Signals.PozKapatilabilir = False
                trader.Signals.PozKapatildi = False
                trader.Signals.PozAcilabilirAlis = False
                trader.Signals.PozAcilabilirSatis = False
                trader.Signals.PozAcildiAlis = False
                trader.Signals.PozAcildiSatis = False
                trader.Signals.GunSonuPozKapatEnabled = False
                trader.Signals.GunSonuPozKapatildi = False
                trader.Signals.TimeFilteringEnabled = False
        pass

    def set_params_for_single_run(self, IdealGetiriHesapla=True, IstatistikleriHesapla=True,
                                 IstatistikleriEkranaYaz=True, GetiriIstatistikleriEkranaYaz=True,
                                 IstatistikleriDosyayaYaz=True, SinyalleriEkranaCiz=True):
        self.bIdealGetiriHesapla = IdealGetiriHesapla
        self.bIstatistikleriHesapla = IstatistikleriHesapla
        self.bIstatistikleriEkranaYaz = IstatistikleriEkranaYaz
        self.bGetiriIstatistikleriEkranaYaz = GetiriIstatistikleriEkranaYaz
        self.bIstatistikleriDosyayaYaz = IstatistikleriDosyayaYaz
        self.bSinyalleriEkranaCiz = SinyalleriEkranaCiz

        return self

    def start(self):
        self.myTimeUtils.start_timer()
        for trader in self.myTraders:
            if trader:
                trader.start()
        pass

    def emirleri_resetle(self, bar_index):
        self.Al = False
        self.Sat = False
        self.FlatOl = False
        self.PasGec = False
        self.KarAl = False
        self.ZararKes = False
        pass

    def emir_oncesi_dongu_foksiyonlarini_calistir(self, BarIndex):
        i = BarIndex
        for trader in self.myTraders:
            if trader:
                trader.dongu_basi_degiskenleri_resetle(i)
                trader.dongu_basi_degiskenleri_guncelle(i)
                if i < 1:
                    return
                trader.anlik_kar_zarar_hesapla(i)
                trader.emirleri_resetle(i)

                # is_yeni_gun = self.V[i].Date.day != self.V[i - 1].Date.day
                # if is_yeni_gun:
                #     Sistem.DikeyCizgiEkle(i, "DimGray", 2, 2)

                # is_yeni_saat = self.V[i].Date.hour != self.V[i - 1].Date.hour

                if trader.Signals.GunSonuPozKapatildi:
                    trader.Signals.GunSonuPozKapatildi = False
                if trader.Signals.KarAlindi or trader.Signals.ZararKesildi or trader.Signals.FlatOlundu:
                    trader.Signals.KarAlindi = False
                    trader.Signals.ZararKesildi = False
                    trader.Signals.FlatOlundu = False
                    trader.Signals.PozAcilabilir = False
                if not trader.Signals.PozAcilabilir:
                    trader.Signals.PozAcilabilir = True
                    trader.Signals.PozAcildi = False

    def emirleri_setle(self, BarIndex, Al, Sat, FlatOl=False, PasGec=False, KarAl=False, ZararKes=False):
        i = BarIndex
        self.Al = Al
        self.Sat = Sat
        self.FlatOl = FlatOl
        self.PasGec = PasGec
        self.KarAl = KarAl
        self.ZararKes = ZararKes


    def emir_sonrasi_dongu_foksiyonlarini_calistir(self, BarIndex):
        i = BarIndex
        for trader in self.myTraders:
            if trader:
                trader.emirleri_setle(i, self.Al, self.Sat, self.FlatOl, self.PasGec, self.KarAl, self.ZararKes)
                trader.Signals.GunSonuPozKapatildi = trader.gun_sonu_poz_kapat(i, trader.Signals.GunSonuPozKapatEnabled)
                trader.emirleri_uygula(i)
                if not trader.Signals.KarAlindi and trader.Signals.KarAl:
                    trader.Signals.KarAlindi = True
                if not trader.Signals.ZararKesildi and trader.Signals.ZararKes:
                    trader.Signals.ZararKesildi = True
                if not trader.Signals.FlatOlundu and trader.Signals.FlatOl:
                    trader.Signals.FlatOlundu = True
                trader.sistem_yon_listesini_guncelle(i)
                trader.sistem_seviye_listesini_guncelle(i)
                trader.sinyal_listesini_guncelle(i)
                trader.islem_listesini_guncelle(i)
                trader.komisyon_listesini_guncelle(i)
                trader.bakiye_listesini_guncelle(i)
                trader.dongu_sonu_degiskenleri_setle(i)

    def stop(self):
        for trader in self.myTraders:
            if trader:
                trader.stop()
        self.myTimeUtils.stop_timer();
        pass


    def hesaplamalari_yap(self):
        for trader in self.myTraders:
            if trader:
                if self.bIdealGetiriHesapla:
                    trader.ideal_getiri_hesapla()
                if self.bIstatistikleriHesapla:
                    trader.istatistikleri_hesapla()

    def sonuclari_ekranda_goster(self):
        for trader in self.myTraders:
            if trader:
                if self.bIstatistikleriEkranaYaz:
                    trader.istatistikleri_ekrana_yaz(1)
                if self.bGetiriIstatistikleriEkranaYaz:
                    trader.getiri_istatistikleri_ekrana_yaz(2)

    def sonuclari_dosyaya_yaz(self):
        for trader in self.myTraders:
            if trader:
                if self.bIstatistikleriDosyayaYaz:
                    trader.istatistikleri_dosyaya_yaz(self.IstatistiklerOutputFileName)


    def set_params_for_optimizasyon(self, OptEnabled=True, IdealGetiriHesapla=True, IstatistikleriHesapla=True,
                                    IstatistikleriEkranaYaz=False, GetiriIstatistikleriEkranaYaz=False,
                                    IstatistikleriDosyayaYaz=True, SinyalleriEkranaCiz=False,
                                    OptimizasyonIstatistiklerininBasliklariniDosyayaYaz=True,
                                    OptimizasyonIstatistikleriniDosyayaYaz=True):
        self.bOptEnabled = OptEnabled
        self.bIdealGetiriHesapla = IdealGetiriHesapla
        self.bIstatistikleriHesapla = IstatistikleriHesapla
        self.bIstatistikleriEkranaYaz = IstatistikleriEkranaYaz
        self.bGetiriIstatistikleriEkranaYaz = GetiriIstatistikleriEkranaYaz
        self.bIstatistikleriDosyayaYaz = IstatistikleriDosyayaYaz
        self.bSinyalleriEkranaCiz = SinyalleriEkranaCiz
        self.bOptimizasyonIstatistiklerininBasliklariniDosyayaYaz = OptimizasyonIstatistiklerininBasliklariniDosyayaYaz
        self.bOptimizasyonIstatistikleriniDosyayaYaz = OptimizasyonIstatistikleriniDosyayaYaz
        return self

    def optimizasyon_istatistiklerinin_basliklarini_dosyaya_yaz(self):
        if self.bOptimizasyonIstatistiklerininBasliklariniDosyayaYaz:
            self.myTrader.optimizasyon_istatistiklerinin_basliklarini_dosyaya_yaz(self.IstatistiklerOptOutputFileName)

    def optimizasyon_istatistiklerini_dosyaya_yaz(self, CurrentRunIndex, TotalRunCount):
        if self.bOptimizasyonIstatistikleriniDosyayaYaz:
            self.myTrader.optimizasyon_istatistiklerini_dosyaya_yaz(self.IstatistiklerOptOutputFileName, CurrentRunIndex, TotalRunCount)

    def set_current_index(self, CurrentRunIndex):
        self.CurrentRunIndex = CurrentRunIndex

    def set_total_run_count(self, TotalRunCount):
        self.TotalRunCount = TotalRunCount

    def set_input_params(self, Index, Value):
        self.InputParams[Index] = Value

    def read_params_from_file(self, FileName):
        if os.path.exists(FileName):
            with open(FileName, 'r') as f:
                readLines = f.readlines()
            self.bUseParamsFromInputFile = int(readLines[0]) == 1
            if self.bUseParamsFromInputFile:
                self.CurrentRunIndex = int(readLines[1])
                self.TotalRunCount = int(readLines[2])
                self.bOptEnabled = int(readLines[3]) == 1
                self.bIdealGetiriHesapla = int(readLines[4]) == 1
                self.bIstatistikleriHesapla = int(readLines[5]) == 1
                self.bIstatistikleriEkranaYaz = int(readLines[6]) == 1
                self.bGetiriIstatistikleriEkranaYaz = int(readLines[7]) == 1
                self.bIstatistikleriDosyayaYaz = int(readLines[8]) == 1
                self.bOptimizasyonIstatistiklerininBasliklariniDosyayaYaz = int(readLines[9]) == 1
                self.bOptimizasyonIstatistikleriniDosyayaYaz = int(readLines[10]) == 1
                self.bSinyalleriEkranaCiz = int(readLines[11]) == 1
                self.ParamsInputFileName = readLines[12].strip()
                self.IstatistiklerOutputFileName = readLines[13].strip()
                self.IstatistiklerOptOutputFileName = readLines[14].strip()
            if self.bUseParamsFromInputFile:
                k = 0
                self.InputParams[k] = readLines[15].strip()
                k += 1
                self.InputParams[k] = readLines[16].strip()
                k += 1
                self.InputParams[k] = readLines[17].strip()
                k += 1
                for i in range(k, self.InputParamsCount):
                    self.InputParams[i] = ""
        return self

    def update_sistem_parametreleri(self):
        # for i in range(20):
        #     Sistem.Parametreler[i] = self.InputParams[i]
        return self

    def write_params_to_file(self, FileName, bUseParamsFromInputFile, CurrentRunIndex, TotalRunCount,
                             bOptEnabled, bIdealGetiriHesapla, bIstatistikleriHesapla, bIstatistikleriEkranaYaz,
                             bGetiriIstatistikleriEkranaYaz, bIstatistikleriDosyayaYaz,
                             bOptimizasyonIstatistiklerininBasliklariniDosyayaYaz,
                             bOptimizasyonIstatistikleriniDosyayaYaz, bSinyalleriEkranaCiz, ParamsInputFileName,
                             IstatistiklerOutputFileName, IstatistiklerOptOutputFileName):
        strOne = "1"
        strZero = "0"
        writeLines = []
        writeLines.append(strOne if bUseParamsFromInputFile else strZero)
        writeLines.append(str(CurrentRunIndex))
        writeLines.append(str(TotalRunCount))
        writeLines.append(strOne if bOptEnabled else strZero)
        writeLines.append(strOne if bIdealGetiriHesapla else strZero)
        writeLines.append(strOne if bIstatistikleriHesapla else strZero)
        writeLines.append(strOne if bIstatistikleriEkranaYaz else strZero)
        writeLines.append(strOne if bGetiriIstatistikleriEkranaYaz else strZero)
        writeLines.append(strOne if bIstatistikleriDosyayaYaz else strZero)
        writeLines.append(strOne if bOptimizasyonIstatistiklerininBasliklariniDosyayaYaz else strZero)
        writeLines.append(strOne if bOptimizasyonIstatistikleriniDosyayaYaz else strZero)
        writeLines.append(strOne if bSinyalleriEkranaCiz else strZero)
        writeLines.append(ParamsInputFileName)
        writeLines.append(IstatistiklerOutputFileName)
        writeLines.append(IstatistiklerOptOutputFileName)
        with open(FileName, 'w', encoding='utf-8') as f:
            f.write('\n'.join(writeLines))
        return self

    def create_optimizasyon_log_string(self, Counter, TotalCount, OptParam1=None, OptParam2=None,
                                       OptParam3=None, OptParam4=None, OptParam5=None, OptParam6=None):
        IstatistiklerNew = self.myTrader.Statistics.IstatistiklerNew
        delimiter = ";"
        strList = []
        strList.append(f"{Counter} {delimiter} ")
        strList.append(f"{TotalCount} {delimiter} ")
        if OptParam1 is not None:
            strList.append(f"{OptParam1} {delimiter} ")
        if OptParam2 is not None:
            strList.append(f"{OptParam2} {delimiter} ")
        if OptParam3 is not None:
            strList.append(f"{OptParam3} {delimiter} ")
        if OptParam4 is not None:
            strList.append(f"{OptParam4} {delimiter} ")
        if OptParam5 is not None:
            strList.append(f"{OptParam5} {delimiter} ")
        if OptParam6 is not None:
            strList.append(f"{OptParam6} {delimiter} ")
        strList.append(f"{IstatistiklerNew['GetiriKzSistem']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['GetiriKz']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['GetiriKzNet']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['ProfitFactor']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['ProfitFactorSistem']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['KarliIslemOrani']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['IslemSayisi']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['KomisyonIslemSayisi']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['KomisyonFiyat']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['KomisyonFiyatYuzde']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['IlkBakiyeFiyat']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['BakiyeFiyat']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['GetiriFiyat']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['GetiriFiyatYuzde']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['BakiyeFiyatNet']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['GetiriFiyatNet']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['GetiriFiyatYuzdeNet']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['MinBakiyeFiyat']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['MaxBakiyeFiyat']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['MinBakiyeFiyatYuzde']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['MaxBakiyeFiyatYuzde']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['MaxKarFiyat']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['MaxZararFiyat']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['MaxKarPuan']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['MaxZararPuan']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['KazandiranIslemSayisi']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['KaybettirenIslemSayisi']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['ToplamKarFiyat']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['ToplamZararFiyat']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['NetKarFiyat']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['ToplamKarPuan']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['ToplamZararPuan']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['NetKarPuan']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['GetiriMaxDD']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['GetiriMaxDDTarih']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['GetiriMaxDDSaat']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['GetiriMaxKayip']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['OrtAylikIslemSayisi']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['OrtHaftalikIslemSayisi']} {delimiter} ")
        strList.append(f"{IstatistiklerNew['OrtGunlukIslemSayisi']} {delimiter} ")
        # strList.append(f"{datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')} {delimiter} ")
        return "".join(f"  {s}" for s in strList).strip()

    def islem_zaman_filtresi_uygula(self, BarIndex, Al, Sat, FlatOl, PasGec, KarAl, ZararKes, FilterMode=3):
        # useTimeFiltering = self.myTrader.Signals.TimeFilteringEnabled
        # if useTimeFiltering:
        #     checkResult = 0
        #     isTradeEnabled = False
        #     isPozKapatEnabled = False
        #     self.myTrader.islem_zaman_filtresi_uygula(BarIndex, FilterMode, isTradeEnabled, isPozKapatEnabled, checkResult)
        #     if not isTradeEnabled:
        #         Al = False
        #     if not isTradeEnabled:
        #         Sat = False
        #     if isPozKapatEnabled:
        #         FlatOl = True
        # return Al, Sat, FlatOl, PasGec, KarAl, ZararKes
        pass

    def islem_zaman_filtresi_uygula(self, BarIndex, FilterMode=3):
        # useTimeFiltering = self.myTrader.Signals.TimeFilteringEnabled
        # if useTimeFiltering:
        #     checkResult = 0
        #     isTradeEnabled = False
        #     isPozKapatEnabled = False
        #     self.myTrader.islem_zaman_filtresi_uygula(BarIndex, FilterMode, isTradeEnabled, isPozKapatEnabled, checkResult)
        #     if not isTradeEnabled:
        #         self.Al = False
        #     if not isTradeEnabled:
        #         self.Sat = False
        #     if isPozKapatEnabled:
        #         self.FlatOl = True
        pass

    def islem_zaman_filtresi_uygula_bunu_kullanma(self, BarIndex, mode1=0):
        i = BarIndex
        # mySystem = self
        # checkResult = 0
        # isTradeEnabled = False
        # isPozKapatEnabled = False
        # startDateTime = mySystem.get_trader().StartDateTimeStr
        # stopDateTime = mySystem.get_trader().StopDateTimeStr
        # startDate = mySystem.get_trader().StartDateStr
        # stopDate = mySystem.get_trader().StopDateStr
        # startTime = mySystem.get_trader().StartTimeStr
        # stopTime = mySystem.get_trader().StopTimeStr
        # # nowDateTime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        # # nowDate = datetime.datetime.now().strftime("%d.%m.%Y")
        # # nowTime = datetime.datetime.now().strftime("%H:%M:%S")
        # useTimeFiltering = mySystem.get_trader(Sistem).Signals.TimeFilteringEnabled
        # mode = mode1
        # if useTimeFiltering and 1 == 0:
        #     if i == Sistem.BarSayisi - 1:
        #         s = ""
        #         s += f"  {startDateTime}\n"
        #         s += f"  {stopDateTime}\n"
        #         s += f"  {startDate}\n"
        #         s += f"  {stopDate}\n"
        #         s += f"  {startTime}\n"
        #         s += f"  {stopTime}\n"
        #         s += f"  {nowDateTime}\n"
        #         s += f"  {nowDate}\n"
        #         s += f"  {nowTime}\n"
        #         s += f"  FilterMode = {mode}\n"
        #         s += "  CSystemWrapper::IslemZamanFiltresiUygula\n"
        #         Sistem.Mesaj(s)
        #     if mode == 0:
        #         pass
        #     elif mode == 1:
        #         if mySystem.get_time_utils(Sistem).check_bar_time_with(Sistem, i, startTime) >= 0 and mySystem.get_time_utils(Sistem).check_bar_time_with(Sistem, i, stopTime) < 0:
        #             isTradeEnabled = True
        #         elif mySystem.get_time_utils(Sistem).check_bar_time_with(Sistem, i, startTime) < 0:
        #             if not mySystem.get_trader(Sistem).is_son_yon_f(Sistem):
        #                 isPozKapatEnabled = True
        #         elif mySystem.get_time_utils(Sistem).check_bar_time_with(Sistem, i, stopTime) >= 0:
        #             if not mySystem.get_trader(Sistem).is_son_yon_f(Sistem):
        #                 isPozKapatEnabled = True
        #         if not isTradeEnabled:
        #             self.Al = False
        #         if not isTradeEnabled:
        #             self.Sat = False
        #         if isPozKapatEnabled:
        #             self.FlatOl = True
        #     elif mode == 2:
        #         if mySystem.get_time_utils(Sistem).check_bar_date_with(Sistem, i, startDate) >= 0 and mySystem.get_time_utils(Sistem).check_bar_date_with(Sistem, i, stopDate) < 0:
        #             isTradeEnabled = True
        #         elif mySystem.get_time_utils(Sistem).check_bar_date_with(Sistem, i, startDate) < 0:
        #             if not mySystem.get_trader(Sistem).is_son_yon_f(Sistem):
        #                 isPozKapatEnabled = True
        #         elif mySystem.get_time_utils(Sistem).check_bar_date_with(Sistem, i, stopDate) >= 0:
        #             if not mySystem.get_trader(Sistem).is_son_yon_f(Sistem):
        #                 isPozKapatEnabled = True
        #         if not isTradeEnabled:
        #             self.Al = False
        #         if not isTradeEnabled:
        #             self.Sat = False
        #         if isPozKapatEnabled:
        #             self.FlatOl = True
        #     elif mode == 3:
        #         if mySystem.get_time_utils(Sistem).check_bar_date_time_with(Sistem, i, startDateTime) >= 0 and mySystem.get_time_utils(Sistem).check_bar_date_time_with(Sistem, i, stopDateTime) < 0:
        #             isTradeEnabled = True
        #         elif mySystem.get_time_utils(Sistem).check_bar_date_time_with(Sistem, i, startDateTime) < 0:
        #             if not mySystem.get_trader(Sistem).is_son_yon_f(Sistem):
        #                 isPozKapatEnabled = True
        #         elif mySystem.get_time_utils(Sistem).check_bar_date_time_with(Sistem, i, stopDateTime) >= 0:
        #             if not mySystem.get_trader(Sistem).is_son_yon_f(Sistem):
        #                 isPozKapatEnabled = True
        #         if not isTradeEnabled:
        #             self.Al = False
        #         if not isTradeEnabled:
        #             self.Sat = False
        #         if isPozKapatEnabled:
        #             self.FlatOl = True
        #     elif mode == 4:
        #         if mySystem.get_time_utils(Sistem).check_bar_time_with(Sistem, i, startTime) >= 0:
        #             isTradeEnabled = True
        #         elif mySystem.get_time_utils(Sistem).check_bar_time_with(Sistem, i, startTime) < 0:
        #             if not mySystem.get_trader(Sistem).is_son_yon_f(Sistem):
        #                 isPozKapatEnabled = True
        #         if not isTradeEnabled:
        #             self.Al = False
        #         if not isTradeEnabled:
        #             self.Sat = False
        #         if isPozKapatEnabled:
        #             self.FlatOl = True
        #     elif mode == 5:
        #         if mySystem.get_time_utils(Sistem).check_bar_date_with(Sistem, i, startDate) >= 0:
        #             isTradeEnabled = True
        #         elif mySystem.get_time_utils(Sistem).check_bar_date_with(Sistem, i, startDate) < 0:
        #             if not mySystem.get_trader(Sistem).is_son_yon_f(Sistem):
        #                 isPozKapatEnabled = True
        #         if not isTradeEnabled:
        #             self.Al = False
        #         if not isTradeEnabled:
        #             self.Sat = False
        #         if isPozKapatEnabled:
        #             self.FlatOl = True
        #     elif mode == 6:
        #         if mySystem.get_time_utils(Sistem).check_bar_date_time_with(Sistem, i, startDateTime) >= 0:
        #             isTradeEnabled = True
        #         elif mySystem.get_time_utils(Sistem).check_bar_date_time_with(Sistem, i, startDateTime) < 0:
        #             if not mySystem.get_trader(Sistem).is_son_yon_f(Sistem):
        #                 isPozKapatEnabled = True
        #         if not isTradeEnabled:
        #             self.Al = False
        #         if not isTradeEnabled:
        #             self.Sat = False
        #         if isPozKapatEnabled:
        #             self.FlatOl = True
        pass


    def reportTimes(self):
        pass

    def get_trader_count(self):
        """Get total number of traders"""
        return len(self.myTraders)

    def get_varlik(self):
        return self.myVarlik

    def get_trader(self, index=0):
        """Get trader by index, defaults to trader 0"""
        if 0 <= index < len(self.myTraders):
            return self.myTraders[index]
        return None

    def get_utils(self):
        return self.myUtils

    def get_time_utils(self):
        return self.myTimeUtils

    def get_bar_utils(self):
        return self.myBarUtils

    def get_file_utils(self):
        return self.myFileUtils

    def get_excel_file_handler(self):
        return self.myExcelUtils

    def get_shared_memory(self):
        return self.mySharedMemory

    def get_config(self):
        return self.myConfig

    def get_indicator_manager(self):
        return self.myIndicators







