import pandas as pd
import numpy as np
import os
from datetime import datetime
from src.DataManager import DataManager
from src.DataPlotter import DataPlotter
from src.SystemWrapper import SystemWrapper
from src.Utils import CUtils

class AlgoTrader:
    def __init__(self):
        self.dataManager = DataManager()
        self.dataPlotter = DataPlotter()
        self.mySystem = SystemWrapper()
        self.myUtils = CUtils()
        pass

    def create_level_series(self,bar_count: int, level_value: float) -> np.ndarray:
        """
        Create a constant level series for the given number of bars.

        Args:
            bar_count: Total number of bars
            level_value: Constant value to set for all bars

        Returns:
            numpy array filled with the level value
        """
        return np.full(bar_count, level_value, dtype=float)

    def loadMarketData(self):
        self.dataManager.create_data(600)
        # self.dataManager.set_read_mode_last_n(1000)  # Son 2000 satırı okumaya ayarla
        # self.dataManager.load_prices_from_csv("data", "01", "BTCUSD.csv")

        self.V          = self.dataManager
        self.Df         = self.dataManager.get_dataframe()
        self.Time       = self.dataManager.get_epoch_time_array()
        self.Open       = self.dataManager.get_open_array()
        self.High       = self.dataManager.get_high_array()
        self.Low        = self.dataManager.get_low_array()
        self.Close      = self.dataManager.get_close_array()
        self.Volume     = self.dataManager.get_volume_array()
        self.Lot        = self.dataManager.get_lot_array()
        self.BarCount   = self.dataManager.get_bar_count()
        self.ItemsCount = self.dataManager.get_items_count()
        self.dataManager.add_time_columns()

        print("========================")
        print("BarCount    :", self.BarCount)
        print("ItemsCount  :", self.ItemsCount)

        print("InputTime   :", self.dataManager.get_timestamp_array()[-5:])
        print("EpochTime   :", self.dataManager.get_epoch_time_array()[-5:])

        print("DateTime    :", self.dataManager.get_date_time_array_as_str()[-5:])
        print("Date        :", self.dataManager.get_date_array_as_str()[-5:])
        print("Time        :", self.dataManager.get_time_array_as_str()[-5:])

        print("Open        :", self.dataManager.get_open_array()[-5:])
        print("High        :", self.dataManager.get_high_array()[-5:])
        print("Low         :", self.dataManager.get_low_array()[-5:])
        print("Close       :", self.dataManager.get_close_array()[-5:])
        print("Volume      :", self.dataManager.get_volume_array()[-5:])
        print("Lot         :", self.dataManager.get_lot_array()[-5:])
        print("========================")

    def plotData(self):
        # --------------------------------------------------------------
        self.dataPlotter.plot_series(
            timestamps=self.Time,
            series_data={
                'Close Price': self.Close,
                'Level': self.Level
            },
            title="Trading Analysis - Price with Level"
        )
        self.dataPlotter.show()

    def trader_0_run_func(self):
        DateTimes = ["25.05.2025 14:30:00", "02.06.2025 14:00:00"]
        Dates = ["01.01.1900", "01.01.2100"]
        Times = ["09:30:00", "11:59:00"]

        self.mySystem.get_trader().reset_date_times()
        self.mySystem.get_trader().set_date_times(DateTimes[0], DateTimes[1])

        self.mySystem.get_trader().Signals.KarAlEnabled = False
        self.mySystem.get_trader().Signals.ZararKesEnabled = False
        self.mySystem.get_trader().Signals.GunSonuPozKapatEnabled = False
        self.mySystem.get_trader().Signals.TimeFilteringEnabled = True

        self.mySystem.start()
        for i in range(self.BarCount):
            Al = False
            Sat = False
            FlatOl = False
            PasGec = False
            KarAl = False
            ZararKes = False
            isTradeEnabled = False
            isPozKapatEnabled = False

            self.mySystem.emirleri_resetle(i)

            self.mySystem.emir_oncesi_dongu_foksiyonlarini_calistir(i)

            if i < 1:
                continue

            FlatOl = False

            Al = True
            Al = self.myUtils.yukari_kesti(i, self.Close, self.Level)

            Sat = True
            Sat = self.myUtils.asagi_kesti(i, self.Close, self.Level)

            KarAl = self.mySystem.get_trader().KarAlZararKes.son_fiyata_gore_kar_al_seviye_hesapla(i, 5, 50,
                                                                                                   1000) != 0

            ZararKes = self.mySystem.get_trader().KarAlZararKes.son_fiyata_gore_zarar_kes_seviye_hesapla(i, -1,
                                                                                                         -10,
                                                                                                         1000) != 0

            KarAl = self.mySystem.get_trader().Signals.KarAlEnabled

            ZararKes = self.mySystem.get_trader().Signals.ZararKesEnabled

            IsSonYonA = self.mySystem.get_trader().is_son_yon_a()

            IsSonYonS = self.mySystem.get_trader().is_son_yon_s()

            IsSonYonF = self.mySystem.get_trader().is_son_yon_f()

            useTimeFiltering = self.mySystem.get_trader().Signals.TimeFilteringEnabled

            self.mySystem.emirleri_setle(i, Al, Sat, FlatOl, PasGec, KarAl, ZararKes)

            self.mySystem.islem_zaman_filtresi_uygula(i)

            self.mySystem.emir_sonrasi_dongu_foksiyonlarini_calistir(i)

        self.mySystem.stop()

        self.mySystem.hesaplamalari_yap()

        self.mySystem.sonuclari_ekranda_goster()

        self.mySystem.sonuclari_dosyaya_yaz()

        pass

    def trader_1_run_func(self):
        pass

    def trader_2_run_func(self):
        pass

    def trader_3_run_func(self):
        pass

    def run(self):
        # --------------------------------------------------------------
        # Read market data (equivalent to .GrafikVerileri operations)
        print("Loading market data...")
        self.loadMarketData()

        # --------------------------------------------------------------
        # Create level series
        self.Level = self.create_level_series(self.BarCount, 5000)

        # --------------------------------------------------------------
        self.mySystem.create_modules().initialize(self.Open, self.High, self.Low, self.Close, self.Volume, self.Lot)

        self.mySystem.reset()
        self.mySystem.initialize_params_with_defaults()
        self.mySystem.set_params_for_single_run()

        for i in range(self.mySystem.get_trader_count()):
            trader = self.mySystem.get_trader(i)
            trader_id = trader.Id

            if (trader_id == 0):
                DateTimes = ["25.05.2025 14:30:00", "02.06.2025 14:00:00"]
                Dates = ["01.01.1900", "01.01.2100"]
                Times = ["09:30:00", "11:59:00"]

                trader.reset_date_times()
                trader.set_date_times(DateTimes[0], DateTimes[1])

                trader.Signals.KarAlEnabled = False
                trader.Signals.ZararKesEnabled = False
                trader.Signals.GunSonuPozKapatEnabled = False
                trader.Signals.TimeFilteringEnabled = True

            elif (trader_id == 1):
                DateTimes = ["25.05.2025 14:30:00", "02.06.2025 14:00:00"]
                Dates = ["01.01.1900", "01.01.2100"]
                Times = ["09:30:00", "11:59:00"]

                trader.reset_date_times()
                trader.set_date_times(DateTimes[0], DateTimes[1])

                trader.Signals.KarAlEnabled = False
                trader.Signals.ZararKesEnabled = False
                trader.Signals.GunSonuPozKapatEnabled = False
                trader.Signals.TimeFilteringEnabled = True

            elif (trader_id == 2):
                DateTimes = ["25.05.2025 14:30:00", "02.06.2025 14:00:00"]
                Dates = ["01.01.1900", "01.01.2100"]
                Times = ["09:30:00", "11:59:00"]

                trader.reset_date_times()
                trader.set_date_times(DateTimes[0], DateTimes[1])

                trader.Signals.KarAlEnabled = False
                trader.Signals.ZararKesEnabled = False
                trader.Signals.GunSonuPozKapatEnabled = False
                trader.Signals.TimeFilteringEnabled = True

            elif (trader_id == 3):
                DateTimes = ["25.05.2025 14:30:00", "02.06.2025 14:00:00"]
                Dates = ["01.01.1900", "01.01.2100"]
                Times = ["09:30:00", "11:59:00"]

                trader.reset_date_times()
                trader.set_date_times(DateTimes[0], DateTimes[1])

                trader.Signals.KarAlEnabled = False
                trader.Signals.ZararKesEnabled = False
                trader.Signals.GunSonuPozKapatEnabled = False
                trader.Signals.TimeFilteringEnabled = True

            else:
                pass

        self.mySystem.start()
        for i in range(self.BarCount):
            for j in range(self.mySystem.get_trader_count()):
                trader = self.mySystem.get_trader(j)

                # print(f"bar {i} : trader {trader.Id} is runnig...\n")

                Al = False
                Sat = False
                FlatOl = False
                PasGec = False
                KarAl = False
                ZararKes = False
                isTradeEnabled = False
                isPozKapatEnabled = False

                trader.emirleri_resetle(i)

                trader.emir_oncesi_dongu_foksiyonlarini_calistir(i)

                if i < 1:
                    continue

                FlatOl = False

                Al = True
                Al = Al and self.myUtils.yukari_kesti(i, self.Close, self.Level)

                Sat = True
                Sat = Sat and self.myUtils.asagi_kesti(i, self.Close, self.Level)

                KarAl = trader.Signals.KarAlEnabled
                KarAl = KarAl and trader.KarAlZararKes.son_fiyata_gore_kar_al_seviye_hesapla(i, 5, 50, 1000) != 0

                ZararKes = trader.Signals.ZararKesEnabled
                ZararKes = ZararKes and trader.KarAlZararKes.son_fiyata_gore_zarar_kes_seviye_hesapla(i, -1, -10, 1000) != 0

                IsSonYonA = trader.is_son_yon_a()

                IsSonYonS = trader.is_son_yon_s()

                IsSonYonF = trader.is_son_yon_f()

                # useTimeFiltering = trader.Signals.TimeFilteringEnabled

                trader.emirleri_setle(i, Al, Sat, FlatOl, PasGec, KarAl, ZararKes)

                trader.islem_zaman_filtresi_uygula(i)

                trader.emir_sonrasi_dongu_foksiyonlarini_calistir(i)

                if Al:
                    print(f"bar {i} : trader {trader.Id} : Signal : Buy, Close {self.Close[i]}")
                if Sat:
                    print(f"bar {i} : trader {trader.Id} : Signal : Sell, Close {self.Close[i]}")

        self.mySystem.stop()

        for i in range(self.mySystem.get_trader_count()):
            trader = self.mySystem.get_trader(i)
            trader_id = trader.Id

            if (trader_id == 0):
                # if (bIdealGetiriHesapla)
                #     myTrader.IdealGetiriHesapla(Sistem);
                #
                # if (bIstatistikleriHesapla)
                #     myTrader.IstatistikleriHesapla(Sistem);
                #
                # if (bIstatistikleriEkranaYaz)
                #     myTrader.IstatistikleriEkranaYaz(Sistem, 1);
                #
                # if (bGetiriIstatistikleriEkranaYaz)
                #     myTrader.GetiriIstatistikleriEkranaYaz(Sistem, 2);
                #
                # if (bIstatistikleriDosyayaYaz)
                #     myTrader.IstatistikleriDosyayaYaz(Sistem, IstatistiklerOutputFileName);
                pass

            elif (trader_id == 1):
                # if (bIdealGetiriHesapla)
                #     myTrader.IdealGetiriHesapla(Sistem);
                #
                # if (bIstatistikleriHesapla)
                #     myTrader.IstatistikleriHesapla(Sistem);
                #
                # if (bIstatistikleriEkranaYaz)
                #     myTrader.IstatistikleriEkranaYaz(Sistem, 1);
                #
                # if (bGetiriIstatistikleriEkranaYaz)
                #     myTrader.GetiriIstatistikleriEkranaYaz(Sistem, 2);
                #
                # if (bIstatistikleriDosyayaYaz)
                #     myTrader.IstatistikleriDosyayaYaz(Sistem, IstatistiklerOutputFileName);
                pass

            elif (trader_id == 2):
                # if (bIdealGetiriHesapla)
                #     myTrader.IdealGetiriHesapla(Sistem);
                #
                # if (bIstatistikleriHesapla)
                #     myTrader.IstatistikleriHesapla(Sistem);
                #
                # if (bIstatistikleriEkranaYaz)
                #     myTrader.IstatistikleriEkranaYaz(Sistem, 1);
                #
                # if (bGetiriIstatistikleriEkranaYaz)
                #     myTrader.GetiriIstatistikleriEkranaYaz(Sistem, 2);
                #
                # if (bIstatistikleriDosyayaYaz)
                #     myTrader.IstatistikleriDosyayaYaz(Sistem, IstatistiklerOutputFileName);
                pass

            elif (trader_id == 3):
                # if (bIdealGetiriHesapla)
                #     myTrader.IdealGetiriHesapla(Sistem);
                #
                # if (bIstatistikleriHesapla)
                #     myTrader.IstatistikleriHesapla(Sistem);
                #
                # if (bIstatistikleriEkranaYaz)
                #     myTrader.IstatistikleriEkranaYaz(Sistem, 1);
                #
                # if (bGetiriIstatistikleriEkranaYaz)
                #     myTrader.GetiriIstatistikleriEkranaYaz(Sistem, 2);
                #
                # if (bIstatistikleriDosyayaYaz)
                #     myTrader.IstatistikleriDosyayaYaz(Sistem, IstatistiklerOutputFileName);
                pass

            else:
                pass

        # --------------------------------------------------------------
        print("Plotting market data...")
        self.plotData()

        # --------------------------------------------------------------
        # Show timing reports
        self.dataManager.reportTimes()
        self.mySystem.reportTimes()

if __name__ == "__main__":
    print("Hello, Gemini!")

    print("algoTrader, started!")

    algoTrader = AlgoTrader()
    algoTrader.run()

    print("algoTrader, finished!")
