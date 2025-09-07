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
        self.set_data(Open, High, Low, Close, Volume, Lot)

        if self.myVarlik:
            self.myVarlik.initialize()
        
        for trader in self.myTraders:
            if trader:
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

    def initialize_params_with_defaults(self):
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

    def set_params_for_single_run(self):
        # this.bIdealGetiriHesapla = IdealGetiriHesapla;
        # this.bIstatistikleriHesapla = IstatistikleriHesapla;
        # this.bIstatistikleriEkranaYaz = IstatistikleriEkranaYaz;
        # this.bGetiriIstatistikleriEkranaYaz = GetiriIstatistikleriEkranaYaz;
        # this.bIstatistikleriDosyayaYaz = IstatistikleriDosyayaYaz;
        # this.bSinyalleriEkranaCiz = SinyalleriEkranaCiz;
        pass

    def get_trader(self, index=0):
        """Get trader by index, defaults to trader 0"""
        if 0 <= index < len(self.myTraders):
            return self.myTraders[index]
        return None
    
    def get_trader_count(self):
        """Get total number of traders"""
        return len(self.myTraders)

    def start(self):
        self.myTimeUtils.start_timer();
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

    def emir_oncesi_dongu_foksiyonlarini_calistir(self, bar_index):
        pass

    def emirleri_setle(self, bar_index, al, sat, flat_ol, pas_gec, kar_al, zarar_kes):
        pass

    def islem_zaman_filtresi_uygula(self, bar_index):
        pass

    def emir_sonrasi_dongu_foksiyonlarini_calistir(self, bar_index):
        pass

    def stop(self):
        for trader in self.myTraders:
            if trader:
                trader.stop()
        self.myTimeUtils.stop_timer();
        pass

    def hesaplamalari_yap(self):
        pass

    def sonuclari_ekranda_goster(self):
        pass

    def sonuclari_dosyaya_yaz(self): 
        pass

    def reportTimes(self):
        pass