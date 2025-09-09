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
        self.KarZararPuanList = []
        self.KarZararFiyatList = []
        self.BakiyeFiyatList = []
        self.KomisyonFiyatList = []
        self.YonList = []
        self.SeviyeList = []
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

    def calculate_most(self, period=21, percent=1.0):
        """
        Calculates the MOST (Moving Stop Loss) indicator based on the provided Pine Script logic.

        Args:
            period: The period for the Exponential Moving Average (EMA).
            percent: The percentage for the bands.

        Returns:
            A tuple containing two numpy arrays: (most, exmov)
        """
        close_series = pd.Series(self.Close)
        exmov = close_series.ewm(span=period, adjust=False).mean().to_numpy()

        fark = exmov * (percent / 100.0)
        up = exmov - fark
        down = exmov + fark

        trend_up = np.zeros(self.BarCount)
        trend_down = np.zeros(self.BarCount)
        trend = np.zeros(self.BarCount)
        most = np.zeros(self.BarCount)

        # Initialize first values
        trend_up[0] = up[0]
        trend_down[0] = down[0]
        trend[0] = 1
        most[0] = trend_up[0]


        for i in range(1, self.BarCount):
            # Pine Script: TrendUp = prev(ExMov,1)>prev(TrendUp,1) ? max(Up,prev(TrendUp,1)) : Up
            if exmov[i-1] > trend_up[i-1]:
                trend_up[i] = max(up[i], trend_up[i-1])
            else:
                trend_up[i] = up[i]

            # Pine Script: TrendDown = prev(ExMov,1)<prev(TrendDown,1) ? min(Down,prev(TrendDown,1)) : Down
            if exmov[i-1] < trend_down[i-1]:
                trend_down[i] = min(down[i], trend_down[i-1])
            else:
                trend_down[i] = down[i]

            # Pine Script: Trend = ExMov>prev(TrendDown,1) ? 1 : ExMov<prev(TrendUp,1) ? -1 : prev(Trend,1)
            if exmov[i] > trend_down[i-1]:
                trend[i] = 1
            elif exmov[i] < trend_up[i-1]:
                trend[i] = -1
            else:
                trend[i] = trend[i-1]

            # Pine Script: MOST = Trend==1 ? TrendUp : TrendDown
            if trend[i] == 1:
                most[i] = trend_up[i]
            else:
                most[i] = trend_down[i]

        return most, exmov

    def loadMarketData(self):
        # self.dataManager.create_data(600)
        self.dataManager.set_read_mode_last_n(20000)  # Son 20000 satırı okumaya ayarla
        self.dataManager.load_prices_from_csv(r"data", "01", "BTCUSD.csv")
        self.dataManager.add_time_columns()
        self.V          = self.dataManager
        self.Df         = self.dataManager.get_dataframe()
        self.EpochTime  = self.dataManager.get_epoch_time_array()
        self.DateTime   = self.dataManager.get_date_time_array()
        self.Date       = self.dataManager.get_date_array()
        self.Time       = self.dataManager.get_time_array()
        self.Open       = self.dataManager.get_open_array()
        self.High       = self.dataManager.get_high_array()
        self.Low        = self.dataManager.get_low_array()
        self.Close      = self.dataManager.get_close_array()
        self.Volume     = self.dataManager.get_volume_array()
        self.Lot        = self.dataManager.get_lot_array()
        self.BarCount   = self.dataManager.get_bar_count()
        self.ItemsCount = self.dataManager.get_items_count()

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

        # --------------------------------------------------------------
        self.dataPlotter.plot_series(
            timestamps=self.Time,
            series_data={
                'Close Price': self.KarZararPuanList,
                'Level': self.LevelZero
            },
            title="Trading Analysis - KarZararPuanList"
        )
        self.dataPlotter.show()

        # --------------------------------------------------------------
        self.dataPlotter.plot_series(
            timestamps=self.Time,
            series_data={
                'Close Price': self.KarZararFiyatList,
                'Level': self.LevelZero
            },
            title="Trading Analysis - KarZararFiyatList"
        )
        self.dataPlotter.show()

        # --------------------------------------------------------------
        self.dataPlotter.plot_series(
            timestamps=self.Time,
            series_data={
                'Close Price': self.BakiyeFiyatList
            },
            title="Trading Analysis - BakiyeFiyatList"
        )
        self.dataPlotter.show()

    def plotData2(self, trader, show_moving_average=False, show_levels=False, show_balance=False, show_kar_zarar_puan=False, show_kar_zarar_fiyat=False):
        """
        Dual-panel plotting method with synchronized zoom functionality.
        
        Args:
            show_moving_average: Show moving average on price chart
            show_levels: Show price levels on price chart
            show_balance: Show balance chart in bottom panel
            show_kar_zarar_puan: Show kar/zarar puan chart in bottom panel
            show_kar_zarar_fiyat: Show kar/zarar fiyat chart in bottom panel
        """
        # print("=== DEBUG: plotData2 başlıyor ===")
        # print(f"Time length: {len(self.Time)}")
        # print(f"Close length: {len(self.Close)}")
        # print(f"Close type: {type(self.Close)}")
        # print(f"Time type: {type(self.Time)}")
        # print(f"Close sample: {self.Close[:5] if len(self.Close) > 5 else self.Close}")
        # print(f"Time sample: {self.Time[:5] if len(self.Time) > 5 else self.Time}")

        # Time array boşsa, basit index array oluştur
        if len(self.Time) == 0:
            print("=== WARNING: Time array boş! Index array oluşturuluyor ===")
            time_array = list(range(len(self.Close)))
        else:
            time_array = self.Time

        # print(f"Final time_array length: {len(time_array)}")
        # print(f"Final time_array sample: {time_array[:5] if len(time_array) > 5 else time_array}")
        #
        # # Sadece Close Price verisi - en basit test
        # price_data = {'Close Price': self.Close}
        #
        # # Alt panel için basit dummy data
        # bottom_data = {'Dummy': [1] * len(self.Close)}  # Time yerine Close length kullan
        # bottom_title = "Test"
        #
        # print(f"Upper panel data keys: {list(price_data.keys())}")
        # print(f"Lower panel data keys: {list(bottom_data.keys())}")
        # print("=== DEBUG: plot_dual_panel çağrılıyor ===")
        #
        # # Use multi panel plotting with synchronized zoom
        # print(f"YonList length: {len(self.YonList)}")
        # print(f"YonList sample: {self.YonList[:20] if len(self.YonList) > 20 else self.YonList}")
        # print(f"SeviyeList length: {len(self.SeviyeList)}")
        # print(f"SeviyeList sample: {self.SeviyeList[:20] if len(self.SeviyeList) > 20 else self.SeviyeList}")
        #
        # # Check for direction changes
        # if len(self.YonList) > 1:
        #     direction_changes = []
        #     for i in range(1, len(self.YonList)):
        #         if self.YonList[i] != self.YonList[i-1]:
        #             direction_changes.append((i, self.YonList[i-1], self.YonList[i], self.SeviyeList[i] if i < len(self.SeviyeList) else 'N/A'))
        #     print(f"Direction changes found: {len(direction_changes)}")
        #     print(f"First 10 changes: {direction_changes[:10]}")

        panels = [
            {
                'series_data': {
                    'Close Price': self.Close,
                    # 'Level': self.Level,
                    'MOST': self.Most,
                    'ExMov': self.ExMov},
                'title': 'Trading Analysis - Price Chart',
                'height_ratio': 3,  # Üst panel daha büyük
                'yon_list': self.YonList,  # A/S/F direction data
                'seviye_list': self.SeviyeList  # Price level data
            },
            {
                'series_data': {'Balance': trader.Lists.BakiyeFiyatList},
                'title': 'Trading Analysis - Balance Chart',
                'height_ratio': 1  # Alt panel daha küçük
            },
            {
                'series_data': {'KarZarar': trader.Lists.KarZararPuanList, 'Zero': self.LevelZero},
                'title': 'Trading Analysis - Kar/Zarar Chart (Puan)',
                'height_ratio': 1  # 3. panel
            },
            {
                'series_data': {'KarZarar': trader.Lists.KarZararFiyatList, 'Zero': self.LevelZero},
                'title': 'Trading Analysis - Kar/Zarar Chart (Fiyat)',
                'height_ratio': 1  # 3. panel
            },
            {
                'series_data': {'KomisyonIslemSayisiList': trader.Lists.KomisyonIslemSayisiList, 'Zero': self.LevelZero},
                'title': 'Trading Analysis - KomisyonIslemSayisiList',
                'height_ratio': 1
            },
            # {
            #     'series_data': {'KomisyonFiyatList': trader.Lists.KomisyonFiyatList,
            #                     # 'Zero': self.LevelZero
            #                     },
            #     'title': 'Trading Analysis - KomisyonFiyatList',
            #     'height_ratio': 1
            # }

            # self.BarIndexList = []
            # self.YonList = []
            # self.SeviyeList = []
            # self.SinyalList = []
            # self.KarZararPuanList = []
            # self.KarZararFiyatList = []
            # self.KarZararFiyatYuzdeList = []
            # self.KarAlList = []
            # self.IzleyenStopList = []
            # self.IslemSayisiList = []
            # self.AlisSayisiList = []
            # self.SatisSayisiList = []
            # self.FlatSayisiList = []
            # self.PassSayisiList = []
            # self.KontratSayisiList = []
            # self.VarlikAdedSayisiList = []
            # self.KomisyonVarlikAdedSayisiList = []
            # self.KomisyonIslemSayisiList = []
            # self.KomisyonFiyatList = []
            # self.KardaBarSayisiList = []
            # self.ZarardaBarSayisiList = []
            # self.BakiyePuanList = []
            # self.BakiyeFiyatList = []
            # self.GetiriPuanList = []
            # self.GetiriFiyatList = []
            # self.GetiriPuanYuzdeList = []
            # self.GetiriFiyatYuzdeList = []
            # self.BakiyePuanNetList = []
            # self.BakiyeFiyatNetList = []
            # self.GetiriPuanNetList = []
            # self.GetiriFiyatNetList = []
            # self.GetiriPuanYuzdeNetList = []
            # self.GetiriFiyatYuzdeNetList = []
            # self.GetiriKz = []
            # self.GetiriKzNet = []
            # self.GetiriKzSistem = []
            # self.GetiriKzNetSistem = []
            # self.EmirKomutList = []
            # self.EmirStatusList = []

        ]
        
        self.dataPlotter.plot_multi_panel(
            timestamps=time_array,
            panels=panels,
            synchronized_zoom=True
        )
        print("=== DEBUG: show çağrılıyor ===")
        self.dataPlotter.show()










    def trader_0_run_func(self):
        DateTimes = ["25.05.2025 14:30:00", "02.06.2025 14:00:00"]
        Dates = ["01.01.1900", "01.01.2100"]
        Times = ["09:30:00", "11:59:00"]

        self.mySystem.get_trader().reset_date_times
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
        self.LevelUp4 = self.create_level_series(self.BarCount, 6000)
        self.LevelUp3 = self.create_level_series(self.BarCount, 5750)
        self.LevelUp2 = self.create_level_series(self.BarCount, 5500)
        self.LevelUp1 = self.create_level_series(self.BarCount, 5250)

        self.Level = self.create_level_series(self.BarCount, 5000)

        self.LevelDown1 = self.create_level_series(self.BarCount, 4750)
        self.LevelDown2 = self.create_level_series(self.BarCount, 4500)
        self.LevelDown3 = self.create_level_series(self.BarCount, 4250)
        self.LevelDown4 = self.create_level_series(self.BarCount, 4000)

        self.LevelZero = self.create_level_series(self.BarCount, 0)

        self.Most, self.ExMov = self.calculate_most(period=21, percent=1.0)

        # --------------------------------------------------------------
        self.mySystem.create_modules().initialize(self.EpochTime, self.DateTime, self.Date, self.Time, self.Open, self.High, self.Low, self.Close, self.Volume, self.Lot)

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

                trader.reset_date_times
                trader.set_date_times(DateTimes[0], DateTimes[1])

                trader.Signals.KarAlEnabled = False
                trader.Signals.ZararKesEnabled = False
                trader.Signals.GunSonuPozKapatEnabled = False
                trader.Signals.TimeFilteringEnabled = True

            elif (trader_id == 1):
                DateTimes = ["25.05.2025 14:30:00", "02.06.2025 14:00:00"]
                Dates = ["01.01.1900", "01.01.2100"]
                Times = ["09:30:00", "11:59:00"]

                trader.reset_date_times
                trader.set_date_times(DateTimes[0], DateTimes[1])

                trader.Signals.KarAlEnabled = False
                trader.Signals.ZararKesEnabled = False
                trader.Signals.GunSonuPozKapatEnabled = False
                trader.Signals.TimeFilteringEnabled = True

            elif (trader_id == 2):
                DateTimes = ["25.05.2025 14:30:00", "02.06.2025 14:00:00"]
                Dates = ["01.01.1900", "01.01.2100"]
                Times = ["09:30:00", "11:59:00"]

                trader.reset_date_times
                trader.set_date_times(DateTimes[0], DateTimes[1])

                trader.Signals.KarAlEnabled = False
                trader.Signals.ZararKesEnabled = False
                trader.Signals.GunSonuPozKapatEnabled = False
                trader.Signals.TimeFilteringEnabled = True

            elif (trader_id == 3):
                DateTimes = ["25.05.2025 14:30:00", "02.06.2025 14:00:00"]
                Dates = ["01.01.1900", "01.01.2100"]
                Times = ["09:30:00", "11:59:00"]

                trader.reset_date_times
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

                Al = self.myUtils.yukari_kesti(i, self.ExMov, self.Most)

                Sat = self.myUtils.asagi_kesti(i, self.ExMov, self.Most)

                KarAl = trader.Signals.KarAlEnabled
                KarAl = KarAl and trader.KarAlZararKes.son_fiyata_gore_kar_al_seviye_hesapla(i, 5, 50, 1000) != 0

                ZararKes = trader.Signals.ZararKesEnabled
                ZararKes = ZararKes and trader.KarAlZararKes.son_fiyata_gore_zarar_kes_seviye_hesapla(i, -1, -10, 1000) != 0

                IsSonYonA = trader.is_son_yon_a()

                IsSonYonS = trader.is_son_yon_s()

                IsSonYonF = trader.is_son_yon_f()

                # useTimeFiltering = trader.Signals.TimeFilteringEnabled

                trader.emirleri_setle(i, Al, Sat, FlatOl, PasGec, KarAl, ZararKes)

                # YAPILACAK
                trader.islem_zaman_filtresi_uygula(i)

                trader.emir_sonrasi_dongu_foksiyonlarini_calistir(i)

                if Al:
                    print(f"bar {i} : trader {trader.Id} : Signal : Buy, Close {self.Close[i]}")
                if Sat:
                    print(f"bar {i} : trader {trader.Id} : Signal : Sell, Close {self.Close[i]}")

                self.KarZararPuanList = trader.Lists.KarZararPuanList
                self.KarZararFiyatList = trader.Lists.KarZararFiyatList
                self.BakiyeFiyatList = trader.Lists.BakiyeFiyatList
                self.YonList = trader.Lists.YonList
                self.SeviyeList = trader.Lists.SeviyeList

        self.mySystem.stop()

        for i in range(self.mySystem.get_trader_count()):
            trader = self.mySystem.get_trader(i)
            trader_id = trader.Id

            if (trader_id == 0):
                trader.update_data_frame()
                print(trader._df)
                print(f'BakiyeInitialized = {trader._df.attrs["BakiyeInitialized"]}')


                # # CSV formatında kaydet
                # trader.write_data_frame_to_file("trading_0_data.csv")
                #
                # # Excel formatında kaydet
                # trader.write_data_frame_to_file("trading_0_data.xlsx")
                #
                # # JSON formatında kaydet
                # trader.write_data_frame_to_file("trading_0_data.json")
                #
                # # HTML formatında kaydet
                # trader.write_data_frame_to_file("trading_0_data.html")

                if ( self.mySystem.bIdealGetiriHesapla):
                    trader.ideal_getiri_hesapla()

                if ( self.mySystem.bIstatistikleriHesapla):
                    trader.istatistikleri_hesapla()
                    pass

                if ( self.mySystem.bIstatistikleriEkranaYaz):
                    # trader.istatistikleri_ekrana_yaz(1)
                    pass

                if ( self.mySystem.bGetiriIstatistikleriEkranaYaz):
                    # trader.istatistikleri_ekrana_yaz(2)
                    pass

                if ( self.mySystem.bIstatistikleriDosyayaYaz):
                    trader.istatistikleri_dosyaya_yaz( self.mySystem.IstatistiklerOutputFileName)
                    pass
                pass

            elif (trader_id == 1):
                if ( self.mySystem.bIdealGetiriHesapla):
                    trader.ideal_getiri_hesapla()

                if ( self.mySystem.bIstatistikleriHesapla):
                    trader.istatistikleri_hesapla()
                    pass

                if ( self.mySystem.bIstatistikleriEkranaYaz):
                    # trader.istatistikleri_ekrana_yaz(1)
                    pass

                if ( self.mySystem.bGetiriIstatistikleriEkranaYaz):
                    # trader.istatistikleri_ekrana_yaz(2)
                    pass

                if ( self.mySystem.bIstatistikleriDosyayaYaz):
                    trader.istatistikleri_dosyaya_yaz( self.mySystem.IstatistiklerOutputFileName)
                    pass
                pass

            elif (trader_id == 2):
                if ( self.mySystem.bIdealGetiriHesapla):
                    trader.ideal_getiri_hesapla()

                if ( self.mySystem.bIstatistikleriHesapla):
                    trader.istatistikleri_hesapla()
                    pass

                if ( self.mySystem.bIstatistikleriEkranaYaz):
                    # trader.istatistikleri_ekrana_yaz(1)
                    pass

                if ( self.mySystem.bGetiriIstatistikleriEkranaYaz):
                    # trader.istatistikleri_ekrana_yaz(2)
                    pass

                if ( self.mySystem.bIstatistikleriDosyayaYaz):
                    trader.istatistikleri_dosyaya_yaz( self.mySystem.IstatistiklerOutputFileName)
                    pass
                pass

            elif (trader_id == 3):
                if ( self.mySystem.bIdealGetiriHesapla):
                    trader.ideal_getiri_hesapla()

                if ( self.mySystem.bIstatistikleriHesapla):
                    trader.istatistikleri_hesapla()
                    pass

                if ( self.mySystem.bIstatistikleriEkranaYaz):
                    # trader.istatistikleri_ekrana_yaz(1)
                    pass

                if ( self.mySystem.bGetiriIstatistikleriEkranaYaz):
                    # trader.istatistikleri_ekrana_yaz(2)
                    pass

                if ( self.mySystem.bIstatistikleriDosyayaYaz):
                    trader.istatistikleri_dosyaya_yaz( self.mySystem.IstatistiklerOutputFileName)
                    pass
                pass

            else:
                pass

        # --------------------------------------------------------------
        print("Plotting market data...")
        self.active_trader = self.mySystem.get_trader(0)
        # self.plotData()
        self.plotData2(self.active_trader)

        # --------------------------------------------------------------
        # Show timing reports
        self.dataManager.reportTimes()
        self.mySystem.reportTimes()

        print(self.BakiyeFiyatList[0])
        print(self.BakiyeFiyatList[1])

if __name__ == "__main__":
    print("Hello, Gemini!")

    print("algoTrader, started!")

    algoTrader = AlgoTrader()
    algoTrader.run()

    print("algoTrader, finished!")
