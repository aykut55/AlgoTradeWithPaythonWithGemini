import pandas as pd
import numpy as np
import os
from datetime import datetime
from src.DataManager import DataManager
from src.DataPlotter import DataPlotter
from src.DataPlotter2 import DataPlotter2
from src.DataPlotterDearPyGui import DataPlotterDearPyGui
from src.DataPlotterDearPyGui2 import DataPlotterDearPyGui2
from src.SqliteDataManager import SqliteDataManager
from src.SystemWrapper import SystemWrapper
from src.Utils import CUtils
from src.IndicatorManager import CIndicatorManager

class AlgoTrader:
    def __init__(self):
        self.sqliteDataManager = SqliteDataManager()
        self.dataManager = DataManager()
        self.dataPlotter = DataPlotter()
        self.dataPlotterDearPyGui = DataPlotterDearPyGui()
        self.dataPlotterDearPyGui2 = DataPlotterDearPyGui2()
        self.dataPlotter2 = DataPlotter2()
        self.mySystem = SystemWrapper()
        self.myUtils = CUtils()
        self.indicatorManager = None
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

    def run_single_optimization_test(self, period, percent):
        """
        Run a single optimization test with given parameters
        
        Args:
            period: Period value for MOST calculation
            percent: Percent value for MOST calculation
            
        Returns:
            dict: Results of the trading test
        """
        # Reset system for this test
        # self.mySystem.reset()
        # self.mySystem.initialize_params_with_defaults()
        # self.mySystem.set_params_for_single_run()

        # Get the first trader
        trader = self.mySystem.get_trader(0)

        trader_id = trader.Id

        DateTimes = ["25.05.2025 14:30:00", "02.06.2025 14:00:00"]
        Dates = ["01.01.1900", "01.01.2100"]
        Times = ["09:30:00", "11:59:00"]

        trader.reset_date_times
        trader.set_date_times(DateTimes[0], DateTimes[1])

        trader.Signals.KarAlEnabled = False
        trader.Signals.ZararKesEnabled = False
        trader.Signals.GunSonuPozKapatEnabled = False
        trader.Signals.TimeFilteringEnabled = True



        self.mySystem.start()
        for i in range(self.BarCount):
            trader = self.mySystem.get_trader(0)
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

            # if Al:
            #     print(f"bar {i} : trader {trader.Id} : Signal : Buy, Close {self.Close[i]}")
            # if Sat:
            #     print(f"bar {i} : trader {trader.Id} : Signal : Sell, Close {self.Close[i]}")

            self.KarZararPuanList = trader.Lists.KarZararPuanList
            self.KarZararFiyatList = trader.Lists.KarZararFiyatList
            self.BakiyeFiyatList = trader.Lists.BakiyeFiyatList
            self.YonList = trader.Lists.YonList
            self.SeviyeList = trader.Lists.SeviyeList
        self.mySystem.stop()

        # Get results from the first trader
        trader = self.mySystem.get_trader(0)
        trader_id = trader.Id

        # Calculate statistics (ideal)
        if (self.mySystem.bIdealGetiriHesapla):
            trader.ideal_getiri_hesapla()

        # Calculate statistics
        if (self.mySystem.bIstatistikleriHesapla):
            trader.istatistikleri_hesapla()
            pass

        if (self.mySystem.bIstatistikleriEkranaYaz):
            # trader.istatistikleri_ekrana_yaz(1)
            pass

        if (self.mySystem.bGetiriIstatistikleriEkranaYaz):
            # trader.istatistikleri_ekrana_yaz(2)
            pass

        if (self.mySystem.bIstatistikleriDosyayaYaz):
            trader.istatistikleri_dosyaya_yaz(self.mySystem.IstatistiklerOutputFileName)
            pass

        # trader.update_data_frame()
        # print(trader._df)
        # print(f'BakiyeInitialized = {trader._df.attrs["BakiyeInitialized"]}')
        # trader.write_data_frame_to_file_as_tabular("trading_data_tabular.txt")
        # trader.write_statistics_to_file_as_tabular("trading_statistics_tabular.txt")
        #
        # # # CSV formatında kaydet
        # # trader.write_data_frame_to_file("trading_0_data.csv")
        # #
        # # # Excel formatında kaydet
        # # trader.write_data_frame_to_file("trading_0_data.xlsx")
        # #
        # # # JSON formatında kaydet
        # # trader.write_data_frame_to_file("trading_0_data.json")
        # #
        # # # HTML formatında kaydet
        # # trader.write_data_frame_to_file("trading_0_data.html")
        # pass
        
        # Extract key metrics
        final_balance = trader.Lists.BakiyeFiyatList[-1] if len(trader.Lists.BakiyeFiyatList) > 0 else 0
        total_trades = len([x for x in trader.Lists.YonList if x != 'F'])
        profit_trades = len([x for x in trader.Lists.KarZararFiyatList if x > 0])
        loss_trades = len([x for x in trader.Lists.KarZararFiyatList if x < 0])
        win_rate = (profit_trades / total_trades) if total_trades > 0 else 0
        
        # Extract additional metrics
        islem_sayisi = trader.Lists.IslemSayisiList[-1] if len(trader.Lists.IslemSayisiList) > 0 else 0
        alis_sayisi = trader.Lists.AlisSayisiList[-1] if len(trader.Lists.AlisSayisiList) > 0 else 0
        satis_sayisi = trader.Lists.SatisSayisiList[-1] if len(trader.Lists.SatisSayisiList) > 0 else 0
        flat_sayisi = trader.Lists.FlatSayisiList[-1] if len(trader.Lists.FlatSayisiList) > 0 else 0
        pass_sayisi = trader.Lists.PassSayisiList[-1] if len(trader.Lists.PassSayisiList) > 0 else 0
        
        komisyon_islem_sayisi = trader.Lists.KomisyonIslemSayisiList[-1] if len(trader.Lists.KomisyonIslemSayisiList) > 0 else 0
        komisyon_fiyat = trader.Lists.KomisyonFiyatList[-1] if len(trader.Lists.KomisyonFiyatList) > 0 else 0
        
        getiri_fiyat = trader.Lists.GetiriFiyatList[-1] if len(trader.Lists.GetiriFiyatList) > 0 else 0
        getiri_fiyat_yuzde = trader.Lists.GetiriFiyatYuzdeList[-1] if len(trader.Lists.GetiriFiyatYuzdeList) > 0 else 0
        
        bakiye_fiyat_net = trader.Lists.BakiyeFiyatNetList[-1] if len(trader.Lists.BakiyeFiyatNetList) > 0 else 0
        getiri_fiyat_net = trader.Lists.GetiriFiyatNetList[-1] if len(trader.Lists.GetiriFiyatNetList) > 0 else 0
        getiri_fiyat_yuzde_net = trader.Lists.GetiriFiyatYuzdeNetList[-1] if len(trader.Lists.GetiriFiyatYuzdeNetList) > 0 else 0
        
        getiri_kz = trader.Lists.GetiriKz[-1] if len(trader.Lists.GetiriKz) > 0 else 0
        getiri_kz_net = trader.Lists.GetiriKzNet[-1] if len(trader.Lists.GetiriKzNet) > 0 else 0

        return {
            'period': period,
            'percent': percent,
            'final_balance': final_balance,
            'total_trades': total_trades,
            'profit_trades': profit_trades,
            'loss_trades': loss_trades,
            'win_rate': win_rate,
            'islem_sayisi': islem_sayisi,
            'alis_sayisi': alis_sayisi,
            'satis_sayisi': satis_sayisi,
            'flat_sayisi': flat_sayisi,
            'pass_sayisi': pass_sayisi,
            'komisyon_islem_sayisi': komisyon_islem_sayisi,
            'komisyon_fiyat': komisyon_fiyat,
            'getiri_fiyat': getiri_fiyat,
            'getiri_fiyat_yuzde': getiri_fiyat_yuzde,
            'bakiye_fiyat_net': bakiye_fiyat_net,
            'getiri_fiyat_net': getiri_fiyat_net,
            'getiri_fiyat_yuzde_net': getiri_fiyat_yuzde_net,
            'getiri_kz': getiri_kz,
            'getiri_kz_net': getiri_kz_net
        }

    def write_optimization_results_to_file(self, output_dir, optimization_results, best_result, best_period, best_percent):
        """
        Write optimization results to multiple file formats
        
        Args:
            output_dir: Directory to save the files
            optimization_results: List of all optimization results
            best_result: Best optimization result
            best_period: Best period parameter
            best_percent: Best percent parameter
        """
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create DataFrame from results
        import pandas as pd
        df = pd.DataFrame(optimization_results)
        
        # Sort by final_balance descending to show best results first
        df = df.sort_values('final_balance', ascending=False)
        
        # Add ranking column
        df['rank'] = range(1, len(df) + 1)
        
        # Reorder columns
        df = df[['rank', 'period', 'percent', 'final_balance', 'total_trades', 'profit_trades', 'loss_trades', 'win_rate']]
        
        # Write to CSV
        csv_filename = os.path.join(output_dir, f"optimization_results_{current_time}.csv")
        df.to_csv(csv_filename, index=False)
        print(f"Optimization results saved to: {csv_filename}")
        
        # Write to Excel with formatting
        try:
            excel_filename = os.path.join(output_dir, f"optimization_results_{current_time}.xlsx")
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Optimization_Results', index=False)
                
                # Add summary sheet
                summary_data = {
                    'Metric': ['Best Period', 'Best Percent', 'Best Final Balance', 'Best Total Trades', 'Best Win Rate', 
                               'Total Tests Run', 'Worst Final Balance', 'Average Final Balance'],
                    'Value': [best_period, best_percent, best_result['final_balance'], best_result['total_trades'], 
                             f"{best_result['win_rate']:.2%}", len(optimization_results), df['final_balance'].min(),
                             df['final_balance'].mean()]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            print(f"Optimization results saved to: {excel_filename}")
        except ImportError:
            print("openpyxl not available, Excel file not created")
        
        # Write detailed text report
        txt_filename = os.path.join(output_dir, f"optimization_report_{current_time}.txt")
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("=== OPTIMIZATION REPORT ===\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("=== BEST RESULT ===\n")
            f.write(f"Period: {best_period}\n")
            f.write(f"Percent: {best_percent}\n")
            f.write(f"Final Balance: {best_result['final_balance']:.2f}\n")
            f.write(f"Total Trades: {best_result['total_trades']}\n")
            f.write(f"Profit Trades: {best_result['profit_trades']}\n")
            f.write(f"Loss Trades: {best_result['loss_trades']}\n")
            f.write(f"Win Rate: {best_result['win_rate']:.2%}\n\n")
            
            f.write("=== TOP 10 RESULTS ===\n")
            f.write(f"{'Rank':<4} {'Period':<6} {'Percent':<7} {'Balance':<12} {'Trades':<6} {'Win Rate':<8}\n")
            f.write("-" * 50 + "\n")
            
            for i, row in df.head(10).iterrows():
                f.write(f"{row['rank']:<4} {row['period']:<6} {row['percent']:<7} "
                       f"{row['final_balance']:<12.2f} {row['total_trades']:<6} {row['win_rate']:<8.2%}\n")
            
            f.write(f"\n=== STATISTICS ===\n")
            f.write(f"Total tests run: {len(optimization_results)}\n")
            f.write(f"Best balance: {df['final_balance'].max():.2f}\n")
            f.write(f"Worst balance: {df['final_balance'].min():.2f}\n")
            f.write(f"Average balance: {df['final_balance'].mean():.2f}\n")
            f.write(f"Standard deviation: {df['final_balance'].std():.2f}\n")
            
            f.write(f"\n=== ALL RESULTS ===\n")
            f.write(f"{'Rank':<4} {'Period':<6} {'Percent':<7} {'Balance':<12} {'Trades':<6} {'P.Trades':<8} {'L.Trades':<8} {'Win Rate':<8}\n")
            f.write("-" * 70 + "\n")
            
            for i, row in df.iterrows():
                f.write(f"{row['rank']:<4} {row['period']:<6} {row['percent']:<7} "
                       f"{row['final_balance']:<12.2f} {row['total_trades']:<6} {row['profit_trades']:<8} "
                       f"{row['loss_trades']:<8} {row['win_rate']:<8.2%}\n")
        
        print(f"Detailed report saved to: {txt_filename}")

    def write_optimization_results_to_file_2(self, output_dir, optimization_results, best_result, best_period, best_percent):
        """
        Write optimization results with all 23 metrics to multiple file formats
        
        Args:
            output_dir: Directory to save the files
            optimization_results: List of all optimization results with 23 metrics
            best_result: Best optimization result
            best_period: Best period parameter
            best_percent: Best percent parameter
        """
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create DataFrame from results
        import pandas as pd
        df = pd.DataFrame(optimization_results)
        
        # Sort by final_balance descending to show best results first
        df = df.sort_values('final_balance', ascending=False)
        
        # Add ranking column
        df['rank'] = range(1, len(df) + 1)
        
        # Reorder columns - put key metrics first
        key_columns = ['rank', 'period', 'percent', 'final_balance', 'total_trades', 'profit_trades', 'loss_trades', 'win_rate']
        other_columns = [col for col in df.columns if col not in key_columns]
        df = df[key_columns + other_columns]
        
        # Write to CSV
        csv_filename = os.path.join(output_dir, f"optimization_results_detailed_{current_time}.csv")
        df.to_csv(csv_filename, index=False)
        print(f"Detailed optimization results saved to: {csv_filename}")
        
        # Write to Excel with formatting
        try:
            excel_filename = os.path.join(output_dir, f"optimization_results_detailed_{current_time}.xlsx")
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Detailed_Results', index=False)
                
                # Add summary sheet with more metrics
                summary_data = {
                    'Metric': ['Best Period', 'Best Percent', 'Best Final Balance', 'Best Total Trades', 'Best Win Rate', 
                               'Best Profit Trades', 'Best Loss Trades', 'Best İslem Sayisi', 'Best Alis Sayisi',
                               'Total Tests Run', 'Worst Final Balance', 'Average Final Balance'],
                    'Value': [best_period, best_percent, best_result['final_balance'], best_result['total_trades'], 
                             f"{best_result['win_rate']:.2%}", best_result.get('profit_trades', 'N/A'), 
                             best_result.get('loss_trades', 'N/A'), best_result.get('islem_sayisi', 'N/A'),
                             best_result.get('alis_sayisi', 'N/A'), len(optimization_results), 
                             df['final_balance'].min(), df['final_balance'].mean()]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            print(f"Detailed optimization results saved to: {excel_filename}")
        except ImportError:
            print("openpyxl not available, Excel file not created")
        
        # Write comprehensive text report
        txt_filename = os.path.join(output_dir, f"optimization_report_detailed_{current_time}.txt")
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("=== DETAILED OPTIMIZATION REPORT (23 Metrics) ===\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("=== BEST RESULT (All Metrics) ===\n")
            for key, value in best_result.items():
                if isinstance(value, float):
                    if 'rate' in key.lower() or 'ratio' in key.lower():
                        f.write(f"{key}: {value:.2%}\n")
                    else:
                        f.write(f"{key}: {value:.2f}\n")
                else:
                    f.write(f"{key}: {value}\n")
            f.write("\n")
            
            f.write("=== TOP 10 RESULTS (Key Metrics) ===\n")
            f.write(f"{'Rank':<4} {'Period':<6} {'Percent':<7} {'Balance':<12} {'Trades':<6} {'Win Rate':<8} {'İslem':<6} {'Alış':<6}\n")
            f.write("-" * 65 + "\n")
            
            for i, row in df.head(10).iterrows():
                islem = row.get('islem_sayisi', 'N/A')
                alis = row.get('alis_sayisi', 'N/A')
                f.write(f"{row['rank']:<4} {row['period']:<6} {row['percent']:<7} "
                       f"{row['final_balance']:<12.2f} {row['total_trades']:<6} {row['win_rate']:<8.2%} "
                       f"{islem:<6} {alis:<6}\n")
            
            f.write(f"\n=== STATISTICS ===\n")
            f.write(f"Total tests run: {len(optimization_results)}\n")
            f.write(f"Best balance: {df['final_balance'].max():.2f}\n")
            f.write(f"Worst balance: {df['final_balance'].min():.2f}\n")
            f.write(f"Average balance: {df['final_balance'].mean():.2f}\n")
            f.write(f"Standard deviation: {df['final_balance'].std():.2f}\n")
            
            # Write all results with all columns
            f.write(f"\n=== ALL RESULTS (All Metrics) ===\n")
            f.write("Note: Due to large number of columns (23 metrics), see CSV/Excel files for complete tabular view\n")
            f.write("-" * 80 + "\n")
            
            for i, row in df.head(20).iterrows():  # Limit to top 20 for readability
                f.write(f"\nRank {row['rank']}: Period={row['period']}, Percent={row['percent']}\n")
                f.write(f"  Final Balance: {row['final_balance']:.2f}\n")
                f.write(f"  Total Trades: {row['total_trades']}, Win Rate: {row['win_rate']:.2%}\n")
                if 'islem_sayisi' in row:
                    f.write(f"  İslem Sayisi: {row.get('islem_sayisi', 'N/A')}, Alış Sayisi: {row.get('alis_sayisi', 'N/A')}\n")
        
        print(f"Detailed optimization report saved to: {txt_filename}")
        
        print(f"\n=== DETAILED OPTIMIZATION SUMMARY ===")
        print(f"Best Period: {best_period}")
        print(f"Best Percent: {best_percent}")
        print(f"Best Final Balance: {best_result['final_balance']:.2f}")
        print(f"Total Tests: {len(optimization_results)}")
        print(f"Average Balance: {df['final_balance'].mean():.2f}")
        print(f"Results saved to: {output_dir}")

    def print_current_result(self, result):
        """Print current optimization result with basic metrics"""
        print(f"  Result: Balance={result['final_balance']:.2f}, Trades={result['total_trades']}, Win Rate={result['win_rate']:.2%}")

    def print_current_result_2(self, result):
        """Print current optimization result with all 23 metrics"""
        print(f"  Detailed Result:")
        print(f"    Period={result['period']}, Percent={result['percent']}")
        print(f"    Final Balance: {result['final_balance']:.2f}")
        print(f"    Total Trades: {result['total_trades']}, Profit: {result['profit_trades']}, Loss: {result['loss_trades']}")
        print(f"    Win Rate: {result['win_rate']:.2%}")
        
        # Print additional metrics if available
        if 'islem_sayisi' in result:
            print(f"    İslem Sayisi: {result.get('islem_sayisi', 'N/A')}, Alış Sayisi: {result.get('alis_sayisi', 'N/A')}")
        if 'satis_sayisi' in result:
            print(f"    Satış Sayisi: {result.get('satis_sayisi', 'N/A')}, Net Kar: {result.get('net_kar', 'N/A')}")
        if 'toplam_komisyon' in result:
            print(f"    Toplam Komisyon: {result.get('toplam_komisyon', 'N/A'):.2f}")
        if 'max_dd' in result:
            print(f"    Max DD: {result.get('max_dd', 'N/A'):.2f}, Max DD %: {result.get('max_dd_percent', 'N/A'):.2%}")
        if 'sharpe_ratio' in result:
            print(f"    Sharpe Ratio: {result.get('sharpe_ratio', 'N/A'):.3f}, Sortino Ratio: {result.get('sortino_ratio', 'N/A'):.3f}")
        
        # Print remaining metrics if they exist
        metrics_to_skip = {'period', 'percent', 'final_balance', 'total_trades', 'profit_trades', 'loss_trades', 
                          'win_rate', 'islem_sayisi', 'alis_sayisi', 'satis_sayisi', 'net_kar', 'toplam_komisyon',
                          'max_dd', 'max_dd_percent', 'sharpe_ratio', 'sortino_ratio'}
        
        other_metrics = {k: v for k, v in result.items() if k not in metrics_to_skip}
        if other_metrics:
            print(f"    Other metrics: {other_metrics}")

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

    def loadMarketDataFromSqliteDB(self):
        # SQLite veritabanından veri yükle
        db_path = "D:\\Aykut\\Projects\\AlgoTradeWithPaythonWithGemini\\data\\sqlLite\\IMKBH_complete.db"
        table_name = "period_05"

        # Mevcut tablolari kontrol et
        available_tables = self.sqliteDataManager.get_available_tables(db_path)
        print(f"Available tables: {available_tables}")

        # Mevcut sembolleri kontrol et
        available_symbols = self.sqliteDataManager.get_available_symbols(db_path, table_name)
        print(f"Available symbols in {table_name}: {available_symbols}")
        print(f"Total symbols found: {len(available_symbols)}")

        # Her sembol için veri aralığını göster
        if available_symbols:
            print("\nSymbol data ranges:")
            for sym in available_symbols[:5]:  # İlk 5 sembolü göster
                data_range = self.sqliteDataManager.get_symbol_data_range(db_path, table_name, sym)
                if data_range:
                    min_date, max_date, count = data_range
                    print(f"  {sym}: {count} records, {min_date} to {max_date}")

        # İlk mevcut sembolü kullan
        if available_symbols:
            symbol = available_symbols[0]
            print(f"\nUsing symbol: {symbol}")
        else:
            print("No symbols found in database!")
            return

        self.sqliteDataManager.set_read_mode_last_n(20000)  # Son 20000 satırı okumaya ayarla
        self.sqliteDataManager.load_prices_from_sqlite(db_path, table_name, symbol)
        self.sqliteDataManager.add_time_columns()

        self.V          = self.sqliteDataManager
        self.Df         = self.sqliteDataManager.get_dataframe()
        self.EpochTime  = self.sqliteDataManager.get_epoch_time_array()
        self.DateTime   = self.sqliteDataManager.get_date_time_array()
        self.Date       = self.sqliteDataManager.get_date_array()
        self.Time       = self.sqliteDataManager.get_time_array()
        self.Open       = self.sqliteDataManager.get_open_array()
        self.High       = self.sqliteDataManager.get_high_array()
        self.Low        = self.sqliteDataManager.get_low_array()
        self.Close      = self.sqliteDataManager.get_close_array()
        self.Volume     = self.sqliteDataManager.get_volume_array()
        self.Lot        = self.sqliteDataManager.get_lot_array()
        self.BarCount   = self.sqliteDataManager.get_bar_count()
        self.ItemsCount = self.sqliteDataManager.get_items_count()

        print("========================")
        print("SQLite Data Manager")
        print("BarCount    :", self.BarCount)
        print("ItemsCount  :", self.ItemsCount)

        print("InputTime   :", self.sqliteDataManager.get_timestamp_array()[-5:])
        print("EpochTime   :", self.sqliteDataManager.get_epoch_time_array()[-5:])

        print("DateTime    :", self.sqliteDataManager.get_date_time_array_as_str()[-5:])
        print("Date        :", self.sqliteDataManager.get_date_array_as_str()[-5:])
        print("Time        :", self.sqliteDataManager.get_time_array_as_str()[-5:])

        print("Open        :", self.sqliteDataManager.get_open_array()[-5:])
        print("High        :", self.sqliteDataManager.get_high_array()[-5:])
        print("Low         :", self.sqliteDataManager.get_low_array()[-5:])
        print("Close       :", self.sqliteDataManager.get_close_array()[-5:])
        print("Volume      :", self.sqliteDataManager.get_volume_array()[-5:])
        print("Lot         :", self.sqliteDataManager.get_lot_array()[-5:])
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

        farkList = [0.0] * len(trader.Lists.BakiyeFiyatList)
        for i in range(len(trader.Lists.BakiyeFiyatList)):
            farkList[i] = trader.Lists.BakiyeFiyatList[i] - trader.Lists.GetiriFiyatList[i]

        farkList2 = [0.0] * len(trader.Lists.GetiriKz)
        for i in range(len(trader.Lists.GetiriKz)):
            farkList2[i] = trader.Lists.GetiriKz[i] - trader.Lists.GetiriKzNet[i]

        print(f"farkList: {farkList[-1]}")
        print(f"farkList2: {farkList2[-1]}")

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
            # {
            #     'series_data': {'Balance': trader.Lists.BakiyeFiyatList},
            #     'title': 'Trading Analysis - Balance Chart',
            #     'height_ratio': 1  # Alt panel daha küçük
            # },
            # {
            #     'series_data': {'KarZarar': trader.Lists.KarZararPuanList, 'Zero': self.LevelZero},
            #     'title': 'Trading Analysis - Kar/Zarar Chart (Puan)',
            #     'height_ratio': 1  # 3. panel
            # },
            # {
            #     'series_data': {'KarZarar': trader.Lists.KarZararFiyatList, 'Zero': self.LevelZero},
            #     'title': 'Trading Analysis - Kar/Zarar Chart (Fiyat)',
            #     'height_ratio': 1  # 3. panel
            # },
            # {
            #     'series_data': {'KarZarar': trader.Lists.KarZararFiyatYuzdeList, 'Zero': self.LevelZero},
            #     'title': 'Trading Analysis - Kar/Zarar Chart (Fiyat %)',
            #     'height_ratio': 1  # 3. panel
            # },
            # {
            #     'series_data': {'KomisyonIslemSayisiList': trader.Lists.KomisyonIslemSayisiList, 'Zero': self.LevelZero},
            #     'title': 'Trading Analysis - KomisyonIslemSayisiList',
            #     'height_ratio': 1
            # },
            # {
            #     'series_data': {
            #         'YonList': trader.Lists.YonList,
            #         'SinyalList': trader.Lists.SinyalList,
            #         'Zero': self.LevelZero
            #     },
            #     'title': 'Trading Analysis - YonList',
            #     'height_ratio': 1
            # },
            # # {
            # #     'series_data': {'KomisyonFiyatList': trader.Lists.KomisyonFiyatList,
            # #                     # 'Zero': self.LevelZero
            # #                     },
            # #     'title': 'Trading Analysis - KomisyonFiyatList',
            # #     'height_ratio': 1
            # # }
            {
                'series_data': {
                    'Balance': trader.Lists.BakiyeFiyatList,
                    'GetiriFiyatList': trader.Lists.GetiriFiyatList,
                    # 'GetiriFiyatYuzdeList': trader.Lists.GetiriFiyatYuzdeList,
                    # 'BakiyeFiyatNetList': trader.Lists.BakiyeFiyatNetList,
                    # 'GetiriFiyatNetList': trader.Lists.GetiriFiyatNetList,
                    # 'GetiriFiyatYuzdeNetList': trader.Lists.GetiriFiyatYuzdeNetList
                    'farkList': farkList,
                },
                'title': 'Trading Analysis - Balance Chart',
                'height_ratio': 2  # Alt panel daha küçük
            },
            {
                'series_data': {
                    # 'Balance': trader.Lists.BakiyeFiyatList,
                    'GetiriKz': trader.Lists.GetiriKz,
                    'GetiriKzNet': trader.Lists.GetiriKzNet,
                    'farkList2': farkList2,
                },
                'title': 'Trading Analysis - Balance Chart',
                'height_ratio': 2  # Alt panel daha küçük
            },

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

    def plotData3(self, trader, show_moving_average=False, show_levels=False, show_balance=False, show_kar_zarar_puan=False, show_kar_zarar_fiyat=False):
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

        farkList = [0.0] * len(trader.Lists.BakiyeFiyatList)
        for i in range(len(trader.Lists.BakiyeFiyatList)):
            farkList[i] = trader.Lists.BakiyeFiyatList[i] - trader.Lists.GetiriFiyatList[i]

        farkList2 = [0.0] * len(trader.Lists.GetiriKz)
        for i in range(len(trader.Lists.GetiriKz)):
            farkList2[i] = trader.Lists.GetiriKz[i] - trader.Lists.GetiriKzNet[i]

        print(f"farkList: {farkList[-1]}")
        print(f"farkList2: {farkList2[-1]}")

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
            # {
            #     'series_data': {'Balance': trader.Lists.BakiyeFiyatList},
            #     'title': 'Trading Analysis - Balance Chart',
            #     'height_ratio': 1  # Alt panel daha küçük
            # },
            # {
            #     'series_data': {'KarZarar': trader.Lists.KarZararPuanList, 'Zero': self.LevelZero},
            #     'title': 'Trading Analysis - Kar/Zarar Chart (Puan)',
            #     'height_ratio': 1  # 3. panel
            # },
            # {
            #     'series_data': {'KarZarar': trader.Lists.KarZararFiyatList, 'Zero': self.LevelZero},
            #     'title': 'Trading Analysis - Kar/Zarar Chart (Fiyat)',
            #     'height_ratio': 1  # 3. panel
            # },
            # {
            #     'series_data': {'KarZarar': trader.Lists.KarZararFiyatYuzdeList, 'Zero': self.LevelZero},
            #     'title': 'Trading Analysis - Kar/Zarar Chart (Fiyat %)',
            #     'height_ratio': 1  # 3. panel
            # },
            # {
            #     'series_data': {'KomisyonIslemSayisiList': trader.Lists.KomisyonIslemSayisiList, 'Zero': self.LevelZero},
            #     'title': 'Trading Analysis - KomisyonIslemSayisiList',
            #     'height_ratio': 1
            # },
            # {
            #     'series_data': {
            #         'YonList': trader.Lists.YonList,
            #         'SinyalList': trader.Lists.SinyalList,
            #         'Zero': self.LevelZero
            #     },
            #     'title': 'Trading Analysis - YonList',
            #     'height_ratio': 1
            # },
            # # {
            # #     'series_data': {'KomisyonFiyatList': trader.Lists.KomisyonFiyatList,
            # #                     # 'Zero': self.LevelZero
            # #                     },
            # #     'title': 'Trading Analysis - KomisyonFiyatList',
            # #     'height_ratio': 1
            # # }
            {
                'series_data': {
                    'Balance': trader.Lists.BakiyeFiyatList,
                    'GetiriFiyatList': trader.Lists.GetiriFiyatList,
                    # 'GetiriFiyatYuzdeList': trader.Lists.GetiriFiyatYuzdeList,
                    # 'BakiyeFiyatNetList': trader.Lists.BakiyeFiyatNetList,
                    # 'GetiriFiyatNetList': trader.Lists.GetiriFiyatNetList,
                    # 'GetiriFiyatYuzdeNetList': trader.Lists.GetiriFiyatYuzdeNetList
                    'farkList': farkList,
                },
                'title': 'Trading Analysis - Balance Chart',
                'height_ratio': 2  # Alt panel daha küçük
            },
            {
                'series_data': {
                    # 'Balance': trader.Lists.BakiyeFiyatList,
                    'GetiriKz': trader.Lists.GetiriKz,
                    'GetiriKzNet': trader.Lists.GetiriKzNet,
                    'farkList2': farkList2,
                },
                'title': 'Trading Analysis - Balance Chart',
                'height_ratio': 2  # Alt panel daha küçük
            },

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

        self.dataPlotterDearPyGui.plot_multi_panel(
            timestamps=time_array,
            panels=panels,
            synchronized_zoom=True
        )
        print("=== DEBUG: show çağrılıyor ===")
        self.dataPlotterDearPyGui.show()

    def plotData3_DearPyGui(self, trader, show_moving_average=False, show_levels=False, show_balance=False, show_kar_zarar_puan=False, show_kar_zarar_fiyat=False):
        """
        Dear PyGui version of plotData3 - plots directly in Trading Analysis window.
        
        Args:
            trader: Trader object with trading data
            show_moving_average: Show moving average on price chart
            show_levels: Show price levels on price chart
            show_balance: Show balance chart in bottom panel
            show_kar_zarar_puan: Show kar/zarar puan chart in bottom panel
            show_kar_zarar_fiyat: Show kar/zarar fiyat chart in bottom panel
        """
        print("=== plotData3_DearPyGui başlıyor ===")
        
        # Time array boşsa, basit index array oluştur
        if len(self.Time) == 0:
            print("=== WARNING: Time array boş! Index array oluşturuluyor ===")
            time_array = list(range(len(self.Close)))
        else:
            time_array = self.Time

        # Calculate additional data
        farkList = [0.0] * len(trader.Lists.BakiyeFiyatList)
        for i in range(len(trader.Lists.BakiyeFiyatList)):
            farkList[i] = trader.Lists.BakiyeFiyatList[i] - trader.Lists.GetiriFiyatList[i]

        farkList2 = [0.0] * len(trader.Lists.GetiriKz)
        for i in range(len(trader.Lists.GetiriKz)):
            farkList2[i] = trader.Lists.GetiriKz[i] - trader.Lists.GetiriKzNet[i]

        print(f"farkList: {farkList[-1] if farkList else 'Empty'}")
        print(f"farkList2: {farkList2[-1] if farkList2 else 'Empty'}")

        # Configure UI layout BEFORE any data operations
        try:
            self.dataPlotterDearPyGui.show_header = True
            self.dataPlotterDearPyGui.show_footer = True
        except Exception as e:
            print(f"Warning: Could not configure UI layout: {e}")
            # Fallback to safe defaults
            self.dataPlotterDearPyGui.show_header = True
            self.dataPlotterDearPyGui.show_footer = False

        # Create panels data
        panels = [
            {
                'series_data': {
                    'Close Price': self.Close,
                    'MOST': self.Most,
                    'ExMov': self.ExMov
                },
                'title': 'Trading Analysis - Price Chart',
                'height_ratio': 3,
                'yon_list': self.YonList,
                'seviye_list': self.SeviyeList
            },
            {
                'series_data': {
                    'Balance': trader.Lists.BakiyeFiyatList,
                    'GetiriFiyatList': trader.Lists.GetiriFiyatList,
                    'farkList': farkList,
                },
                'title': 'Trading Analysis - Balance Chart',
                'height_ratio': 2
            },
            {
                'series_data': {
                    'GetiriKz': trader.Lists.GetiriKz,
                    'GetiriKzNet': trader.Lists.GetiriKzNet,
                    'farkList2': farkList2,
                },
                'title': 'Trading Analysis - GetiriKz Chart',
                'height_ratio': 2
            }
        ]

        print("=== Calling dataPlotterDearPyGui.plot_multi_panel ===")
        self.dataPlotterDearPyGui.plot_multi_panel(
            timestamps=time_array,
            panels=panels,
            synchronized_zoom=True
        )

        print("=== Calling dataPlotterDearPyGui.show ===")
        self.dataPlotterDearPyGui.show()
        print("=== plotData3_DearPyGui tamamlandı ===")

    def plotData4_DearPyGui(self, trader, show_moving_average=False, show_levels=False, show_balance=False,
                                show_kar_zarar_puan=False, show_kar_zarar_fiyat=False):
        """
        Modern financial data visualization using DataPlotterDearPyGui2 framework.

        Args:
            trader: Trader object containing trading data
            show_moving_average: Show moving average indicators
            show_levels: Show support/resistance levels
            show_balance: Show balance chart
            show_kar_zarar_puan: Show profit/loss points
            show_kar_zarar_fiyat: Show profit/loss prices
        """

        # Time array boşsa, basit index array oluştur
        if len(self.Time) == 0:
            print("=== WARNING: Time array boş! Index array oluşturuluyor ===")
            time_array = list(range(len(self.Close)))
        else:
            time_array = self.Time

        balance = trader.Lists.BakiyeFiyatList
        getiriFiyatList = trader.Lists.GetiriFiyatList
        getiriKz = trader.Lists.GetiriKz
        getiriKzNet = trader.Lists.GetiriKzNet
        karZararPuanList = trader.Lists.KarZararPuanList
        karZararFiyatList = trader.Lists.KarZararFiyatList

        # Calculate additional data
        farkList = [0.0] * len(trader.Lists.BakiyeFiyatList)
        for i in range(len(trader.Lists.BakiyeFiyatList)):
            farkList[i] = trader.Lists.BakiyeFiyatList[i] - trader.Lists.GetiriFiyatList[i]

        farkList2 = [0.0] * len(trader.Lists.GetiriKz)
        for i in range(len(trader.Lists.GetiriKz)):
            farkList2[i] = trader.Lists.GetiriKz[i] - trader.Lists.GetiriKzNet[i]

        print(f"farkList: {farkList[-1] if farkList else 'Empty'}")
        print(f"farkList2: {farkList2[-1] if farkList2 else 'Empty'}")


        print("=== plotData4_DearPyGui başlıyor ===")

        try:
            from src.DataPlotterDearPyGui2 import DataPlotterDearPyGui2

            # Initialize the framework
            self.dataPlotterDearPyGui2 = DataPlotterDearPyGui2(
                figsize=(1600, 1000),
                title="AlgoTrader - Financial Data Analysis"
            )

            # Panel visibility will use default values from DataPlotterDearPyGui2

            # Store parameters for content restoration
            self.current_trader = trader
            self.current_show_moving_average = show_moving_average
            
            # Chart type selection
            self.chart_type = "Candlestick"  # Default chart type (Mum Grafikler)
            
            # Data cache to prevent recalculation
            self.data_cache = {
                "ohlc_data": None,
                "line_data": None,
                "heiken_ashi_data": None,
                "volume_data": None,
                "ma_data": None
            }

            # Initialize the UI
            self.dataPlotterDearPyGui2.Initialize()

            # Setup menu bar
            # Setup menu items
            self._setup_menu_items()
            
            # Set the menu setup callback for RefreshLayout
            self.dataPlotterDearPyGui2.SetMenuSetupCallback(self._setup_menu_items)
            
            # Set the content setup callback for RefreshLayout
            self.dataPlotterDearPyGui2.SetContentSetupCallback(self._setup_panel_content)

            main_panel = self.dataPlotterDearPyGui2.GetMainPanel()


            volume_data_dict = self._prepare_volume_data(self.current_trader)
            volume_data = volume_data_dict['Volume']

            # ----------------------------------------------------------------------------------------------------------
            chart_type_name = getattr(self, 'chart_type', 'OHLC')
            panel0 = main_panel.AddPanel(0, title=f"Price Chart ({chart_type_name})", height_ratio=1)
            if panel0:
                # --- panele hangi türde price verisi kullanaılacak onu veriyoruz
                panel0.SetLegend("OHLC")
                panel0.SetPriceData(trader)
                panel0._setup_price_chart_content2(chart_type_name)

                panel0.AddXData(timestamps=time_array)
                
                # Volume'u fiyat aralığına normalize et
                if len(volume_data) > 0 and len(self.Close) > 0:
                    price_min = min(self.Close)
                    price_max = max(self.Close)
                    volume_min = min(volume_data)
                    volume_max = max(volume_data)

                    k = 0.90 # skale etmek icin
                    
                    # Volume'u fiyat aralığına ölçekle
                    normalized_volume = []
                    for vol in volume_data:
                        normalized_vol = price_min + (vol - volume_min) * (price_max - price_min) / (volume_max - volume_min)
                        normalized_vol = k * normalized_vol
                        normalized_volume.append(normalized_vol)
                    # panel0.AddYData(normalized_volume, 'volume (normalized)')


                # Dinamik yatay çizgiler için seviye listesi oluştur
                # Önce trader'dan güncel verileri al
                self.YonList = trader.Lists.YonList
                self.SeviyeList = trader.Lists.SeviyeList

                import numpy as np
                segments = self.get_signal_segments()

                # Tüm segmentleri tek bir combined data olarak birleştir
                combined_data = [np.nan] * len(time_array)
                
                for seg in segments:
                    for j in range(seg["start"], seg["end"] + 1):
                        if j < len(combined_data):
                            combined_data[j] = seg["level"]
                    
                    print(f"DEBUG: Added {seg['direction']} segment {seg['start']}→{seg['end']} at level {seg['level']:.2f}")

                # Tek bir legend entry ile tüm segmentleri çiz
                if segments:  # En az bir segment varsa
                    panel0.AddYData(combined_data, "Signal Levels")

                panel0.AddYData(self.ExMov, 'ExMov')
                panel0.AddYData(self.Most, 'Most')
                panel0.AddYData(self.Ma5, 'MA5')
                panel0.AddYData(self.Ma8, 'MA8')
                panel0.AddYData(self.Ma13, 'Ma13')
                panel0.AddYData(self.Ma100, 'Ma100')
                panel0.AddYData(self.Ma200, 'Ma200')

                panel0.SetTitle('Trading Analysis - Price Chart')
                # panel0.SetHeightRatio(1)

                panel0.PlotSignals()

            # ----------------------------------------------------------------------------------------------------------
            panel1 = main_panel.AddPanel(1, title="ma", height_ratio=1)
            if panel1:
                panel1.AddXData(timestamps=time_array)
                panel1.AddYData(self.Ma5, 'MA5')
                panel1.AddYData(self.Ma8, 'MA8')
                panel1.AddYData(self.Ma13, 'Ma13')
                panel1.AddYData(self.Ma100, 'Ma100')
                panel1.AddYData(self.Ma200, 'Ma200')

                panel1.SetTitle('Trading Analysis - Price Chart')

                panel1.PlotSignals()

            # ----------------------------------------------------------------------------------------------------------
            panel2 = main_panel.AddPanel(2, title="Volume", height_ratio=1)
            if panel2:
                print(f"DEBUG: Panel2 created successfully: {panel2}")
                print(f"DEBUG: Trader attributes: {[attr for attr in dir(self.current_trader) if 'volume' in attr.lower() or 'close' in attr.lower()]}")


                # print(f"DEBUG: Volume data dict: {volume_data_dict}")

                if volume_data_dict and 'Volume' in volume_data_dict:
                    volume_data = volume_data_dict['Volume']
                    # print(f"DEBUG: Volume data type: {type(volume_data)}, length: {len(volume_data) if hasattr(volume_data, '__len__') else 'N/A'}")

                    panel2.AddXData(timestamps=time_array)
                    panel2.AddYData(volume_data, 'Volume')
                    panel2.SetTitle('Trading Analysis - Volume Chart')
                    panel2.PlotSignals()
                else:
                    print("DEBUG: No volume data available!")
            else:
                print("DEBUG: Panel2 creation failed!")

            # ----------------------------------------------------------------------------------------------------------
            panel3 = main_panel.AddPanel(3, title="balance", height_ratio=1)
            if panel3:
                panel3.AddXData(timestamps=time_array)
                panel3.AddYData(balance, 'balance')
                panel3.AddYData(getiriFiyatList, 'getiriFiyatList')
                panel3.AddYData(farkList, 'farkList')
                panel3.SetTitle('Trading Analysis - balance')
                panel3.PlotSignals()

            # ----------------------------------------------------------------------------------------------------------

            panel4 = main_panel.AddPanel(4, title="GetiriKz", height_ratio=1)
            if panel4:
                panel4.AddXData(timestamps=time_array)
                panel4.AddYData(getiriKz, 'getiriKz')
                panel4.AddYData(getiriKzNet, 'getiriKzNet')
                panel4.AddYData(farkList2, 'farkList2')
                panel4.SetTitle('Trading Analysis - GetiriKz')
                panel4.PlotSignals()

            # ----------------------------------------------------------------------------------------------------------

            panel5 = main_panel.AddPanel(5, title="karZarar", height_ratio=1)
            if panel5:
                panel5.AddXData(timestamps=time_array)
                panel5.AddYData(karZararFiyatList, 'karZararFiyatList')
                panel5.SetTitle('Trading Analysis - karZararFiyatList')
                panel5.PlotSignals()

            # ----------------------------------------------------------------------------------------------------------
            # Setup status bar
            status_bar = self.dataPlotterDearPyGui2.GetStatusBar()
            if status_bar:
                status_bar.SetText("Chart loaded successfully - Ready for analysis")
                status_bar.AddIndicator("progress", 1.0)  # Loading complete


            print("=== Framework initialized, showing chart ===")

            # Display the application
            self.dataPlotterDearPyGui2.Show()

        except Exception as e:
            print(f"Error in plotData4_DearPyGui: {e}")
            import traceback
            traceback.print_exc()

        print("=== plotData4_DearPyGui tamamlandı ===")

    def _get_trading_params_text(self, trader):
        """Get trading parameters as formatted text."""
        try:
            params = []
            params.append(f"Symbol: {getattr(trader, 'symbol', 'N/A')}")
            params.append(f"Timeframe: {getattr(trader, 'timeframe', 'N/A')}")
            params.append(f"Balance: {getattr(trader, 'balance', 'N/A')}")
            params.append(f"Position Size: {getattr(trader, 'position_size', 'N/A')}")
            params.append(f"Risk %: {getattr(trader, 'risk_percent', 'N/A')}")
            return "\n".join(params)
        except:
            return "Parameters not available"

    def _get_trading_statistics(self, trader):
        """Get trading statistics as table data."""
        try:
            stats = []
            stats.append(["Total Trades", str(getattr(trader, 'total_trades', 0))])
            stats.append(["Win Rate", f"{getattr(trader, 'win_rate', 0):.2f}%"])
            stats.append(["Profit Factor", f"{getattr(trader, 'profit_factor', 0):.2f}"])
            stats.append(["Max Drawdown", f"{getattr(trader, 'max_drawdown', 0):.2f}%"])
            stats.append(["Sharpe Ratio", f"{getattr(trader, 'sharpe_ratio', 0):.2f}"])
            return stats
        except:
            return [["No Data", "Available"]]

    def _prepare_ohlc_data(self, trader):
        """Prepare OHLC data for candlestick chart with caching."""
        try:
            # Check cache first
            if self.data_cache["ohlc_data"] is not None:
                print("DEBUG: Using cached OHLC data")
                return self.data_cache["ohlc_data"]
            
            print(f"DEBUG: _prepare_ohlc_data called with trader: {trader}")
            
            # Try different attribute names for OHLC data
            close_data = None
            open_data = None
            high_data = None
            low_data = None
            
            # Check for standard attribute names on self (AlgoTrader instance)
            if hasattr(self, 'Close') and self.Close is not None:
                close_data = self.Close
                open_data = getattr(self, 'Open', close_data)
                high_data = getattr(self, 'High', close_data)
                low_data = getattr(self, 'Low', close_data)
                print(f"DEBUG: Using self.Close/Open/High/Low attributes")
            
            # Check for standard attribute names on trader (fallback)
            elif hasattr(trader, 'Close') and trader.Close is not None:
                close_data = trader.Close
                open_data = getattr(trader, 'Open', close_data)
                high_data = getattr(trader, 'High', close_data)
                low_data = getattr(trader, 'Low', close_data)
                print(f"DEBUG: Using trader.Close/Open/High/Low attributes")
            
            # Check for alternative names (close_prices, etc.)
            elif hasattr(trader, 'close_prices') and trader.close_prices is not None:
                close_data = trader.close_prices
                open_data = getattr(trader, 'open_prices', close_data)
                high_data = getattr(trader, 'high_prices', close_data)
                low_data = getattr(trader, 'low_prices', close_data)
                print(f"DEBUG: Using close_prices/open_prices/etc. attributes")
            
            if close_data is not None and len(close_data) > 0:
                length = len(close_data)
                result = {
                    "timestamps": list(range(length)),
                    "open": list(open_data) if hasattr(open_data, '__iter__') else [open_data] * length,
                    "high": list(high_data) if hasattr(high_data, '__iter__') else [high_data] * length,
                    "low": list(low_data) if hasattr(low_data, '__iter__') else [low_data] * length,
                    "close": list(close_data)
                }
                
                # Cache the result
                self.data_cache["ohlc_data"] = result
                print(f"DEBUG: OHLC data created and cached with {length} points")
                print(f"DEBUG: Sample data - Close[0]: {result['close'][0] if result['close'] else 'None'}")
                return result
            else:
                print("DEBUG: No suitable OHLC data found")
                print(f"DEBUG: Available trader attributes: {[attr for attr in dir(trader) if not attr.startswith('_') and hasattr(getattr(trader, attr, None), '__len__')]}")
                
        except Exception as e:
            print(f"Error preparing OHLC data: {e}")
            import traceback
            traceback.print_exc()
        return None

    def _prepare_line_data(self, trader):
        """Prepare line chart data using only Close prices with caching."""
        try:
            # Check cache first
            if self.data_cache["line_data"] is not None:
                print("DEBUG: Using cached line data")
                return self.data_cache["line_data"]
            
            print(f"DEBUG: _prepare_line_data called with trader: {trader}")
            
            # Get close data
            close_data = None
            
            # Check for standard attribute names (Close)
            if hasattr(trader, 'Close') and trader.Close is not None:
                close_data = trader.Close
                print(f"DEBUG: Using Close attribute for line chart")
            
            # Check for alternative names (close_prices)
            elif hasattr(trader, 'close_prices') and trader.close_prices is not None:
                close_data = trader.close_prices
                print(f"DEBUG: Using close_prices attribute for line chart")
            
            if close_data is not None and len(close_data) > 0:
                length = len(close_data)
                result = {
                    "Close": list(close_data)  # Line chart expects named series
                }
                
                # Cache the result
                self.data_cache["line_data"] = result
                print(f"DEBUG: Line data created and cached with {length} points")
                print(f"DEBUG: Sample data - Close[0]: {result['Close'][0] if result['Close'] else 'None'}")
                return result
            else:
                print("DEBUG: No suitable Close data found for line chart")
                
        except Exception as e:
            print(f"Error preparing line data: {e}")
            import traceback
            traceback.print_exc()
        return None

    def _prepare_moving_average_data(self, trader):
        """Prepare moving average data."""
        try:
            ma_data = {}
            if hasattr(trader, 'ma_values') and trader.ma_values:
                ma_data["MA"] = trader.ma_values
            if hasattr(trader, 'ma_fast') and trader.ma_fast:
                ma_data["MA Fast"] = trader.ma_fast
            if hasattr(trader, 'ma_slow') and trader.ma_slow:
                ma_data["MA Slow"] = trader.ma_slow
            return ma_data if ma_data else None
        except Exception as e:
            print(f"Error preparing MA data: {e}")
        return None

    def _prepare_heiken_ashi_data(self, trader):
        """Prepare Heiken Ashi candlestick data with caching."""
        try:
            # Check cache first
            if self.data_cache["heiken_ashi_data"] is not None:
                print("DEBUG: Using cached Heiken Ashi data")
                return self.data_cache["heiken_ashi_data"]
            
            print(f"DEBUG: _prepare_heiken_ashi_data called with trader: {trader}")
            
            # First get OHLC data
            ohlc_data = self._prepare_ohlc_data(trader)
            if not ohlc_data:
                print("DEBUG: No OHLC data available for Heiken Ashi calculation")
                return None
            
            open_prices = ohlc_data["open"]
            high_prices = ohlc_data["high"]
            low_prices = ohlc_data["low"]
            close_prices = ohlc_data["close"]
            
            length = len(close_prices)
            if length == 0:
                return None
            
            # Initialize Heiken Ashi arrays
            ha_open = [0] * length
            ha_high = [0] * length
            ha_low = [0] * length
            ha_close = [0] * length
            
            # Calculate Heiken Ashi values
            for i in range(length):
                if i == 0:
                    # First candle
                    ha_open[i] = (open_prices[i] + close_prices[i]) / 2
                    ha_close[i] = (open_prices[i] + high_prices[i] + low_prices[i] + close_prices[i]) / 4
                    ha_high[i] = high_prices[i]
                    ha_low[i] = low_prices[i]
                else:
                    # Subsequent candles
                    ha_open[i] = (ha_open[i-1] + ha_close[i-1]) / 2
                    ha_close[i] = (open_prices[i] + high_prices[i] + low_prices[i] + close_prices[i]) / 4
                    ha_high[i] = max(high_prices[i], ha_open[i], ha_close[i])
                    ha_low[i] = min(low_prices[i], ha_open[i], ha_close[i])
            
            result = {
                "timestamps": list(range(length)),
                "open": ha_open,
                "high": ha_high,
                "low": ha_low,
                "close": ha_close
            }
            
            # Cache the result
            self.data_cache["heiken_ashi_data"] = result
            print(f"DEBUG: Heiken Ashi data created and cached with {length} points")
            print(f"DEBUG: Sample HA data - Open[0]: {ha_open[0]:.4f}, Close[0]: {ha_close[0]:.4f}")
            return result
            
        except Exception as e:
            print(f"Error preparing Heiken Ashi data: {e}")
            import traceback
            traceback.print_exc()
        return None

    def _prepare_volume_data(self, trader):
        """Prepare volume data."""
        try:
            print(f"DEBUG: _prepare_volume_data called with trader: {trader}")
            
            # Check for volume_values on trader
            if hasattr(trader, 'volume_values') and trader.volume_values:
                print("DEBUG: Found trader.volume_values")
                return {"Volume": trader.volume_values}
            
            # Check for close_prices on trader
            elif hasattr(trader, 'close_prices') and len(trader.close_prices) > 0:
                print("DEBUG: Found trader.close_prices, generating dummy volume")
                import random
                volume = [random.randint(1000, 10000) for _ in range(len(trader.close_prices))]
                return {"Volume": volume}
            
            # Check if we can use self.Volume (from market data)
            elif hasattr(self, 'Volume') and self.Volume is not None and len(self.Volume) > 0:
                print("DEBUG: Found self.Volume, using market volume data")
                return {"Volume": list(self.Volume)}
            
            # Check if we can use self.Close to generate dummy volume
            elif hasattr(self, 'Close') and self.Close is not None and len(self.Close) > 0:
                print("DEBUG: Found self.Close, generating dummy volume based on Close data length")
                import random
                volume = [random.randint(1000, 10000) for _ in range(len(self.Close))]
                return {"Volume": volume}
            
            else:
                print("DEBUG: No suitable data found for volume generation")
                
        except Exception as e:
            print(f"Error preparing volume data: {e}")
            import traceback
            traceback.print_exc()
        return None

    def _prepare_balance_data(self, trader):
        """Prepare balance data."""
        try:
            if hasattr(trader, 'balance_history') and trader.balance_history:
                return {"Balance": trader.balance_history}
            elif hasattr(trader, 'equity_curve') and trader.equity_curve:
                return {"Equity": trader.equity_curve}
        except Exception as e:
            print(f"Error preparing balance data: {e}")
        return None

    def _prepare_pnl_points_data(self, trader):
        """Prepare P&L points data."""
        try:
            if hasattr(trader, 'pnl_points') and trader.pnl_points:
                return {"P&L Points": trader.pnl_points}
        except Exception as e:
            print(f"Error preparing P&L points data: {e}")
        return None

    # Callback methods for menu items
    def _on_save_chart(self, sender, app_data, user_data):
        print("Save chart requested")

    def _on_export_data(self, sender, app_data, user_data):
        print("Export data requested")

    def _on_exit_app(self, sender, app_data, user_data):
        print("Exit application requested")

    def _on_reset_zoom(self, sender, app_data, user_data):
        """Reset zoom on all charts."""
        print("Reset zoom requested")
        try:
            if hasattr(self, 'dataPlotterDearPyGui2') and self.dataPlotterDearPyGui2:
                self.dataPlotterDearPyGui2.ResetZoomWithCollection()
                print("Zoom reset completed on all charts")
        except Exception as e:
            print(f"Error resetting zoom: {e}")

    def _on_toggle_grid(self, sender, app_data, user_data):
        print("Toggle grid requested")

    def _on_analysis_tools(self, sender, app_data, user_data):
        print("Analysis tools requested")

    def _on_settings(self, sender, app_data, user_data):
        print("Settings requested")

    def _on_refresh_data(self, sender, app_data, user_data):
        print("Refresh data requested")

    def _on_auto_scale(self, sender, app_data, user_data):
        print("Auto scale requested")

    def _on_start_trading(self, sender, app_data, user_data):
        print("Start trading requested")

    def _on_stop_trading(self, sender, app_data, user_data):
        print("Stop trading requested")

    def _on_reset_system(self, sender, app_data, user_data):
        print("Reset system requested")

    def _on_manual_mode(self, sender, app_data, user_data):
        print("Manual mode activated")

    def _on_auto_mode(self, sender, app_data, user_data):
        print("Auto mode activated")

    def _get_quick_statistics(self, trader):
        """Get quick trading statistics as table data."""
        try:
            quick_stats = []
            quick_stats.append(["Current Balance", f"{getattr(trader, 'current_balance', 10000):.2f}"])
            quick_stats.append(["Position", getattr(trader, 'current_position', 'Flat')])
            quick_stats.append(["Last Trade", getattr(trader, 'last_trade_type', 'None')])
            quick_stats.append(["P&L Today", f"{getattr(trader, 'pnl_today', 0):.2f}"])
            return quick_stats
        except:
            return [["Quick Data", "Not Available"]]

    def _setup_menu_items(self, menu=None):
        """Setup all menu items. Can be called with a menu parameter or use the main menu."""
        if menu is None:
            menu = self.dataPlotterDearPyGui2.GetMainMenu()
        
        if menu:
            # File menu
            menu.AddItem("File")
            menu.AddSubItem("File", "Save Chart", self._on_save_chart)
            menu.AddSubItem("File", "Export Data", self._on_export_data)
            menu.AddSubItem("File", "Exit", self._on_exit_app)

            # View menu
            menu.AddItem("View")
            menu.AddSubItem("View", "Reset Zoom", self._on_reset_zoom)
            menu.AddSubItem("View", "Toggle Grid", self._on_toggle_grid)
            menu.AddSubItem("View", "--- Panels ---", None)  # Separator
            
            # Panel toggle items with checkmarks
            upper_check = "[X] " if self.dataPlotterDearPyGui2.show_upper_panel else "[ ] "
            left_check = "[X] " if self.dataPlotterDearPyGui2.show_left_panel else "[ ] "
            main_check = "[X] " if self.dataPlotterDearPyGui2.show_main_panel else "[ ] "
            right_check = "[X] " if self.dataPlotterDearPyGui2.show_right_panel else "[ ] "
            bottom_check = "[X] " if self.dataPlotterDearPyGui2.show_bottom_panel else "[ ] "
            status_check = "[X] " if self.dataPlotterDearPyGui2.show_status_bar else "[ ] "
            
            menu.AddSubItem("View", f"{upper_check}Upper Panel", self._on_toggle_upper_panel)
            menu.AddSubItem("View", f"{left_check}Left Panel", self._on_toggle_left_panel)
            menu.AddSubItem("View", f"{main_check}Main Panel", self._on_toggle_main_panel)
            menu.AddSubItem("View", f"{right_check}Right Panel", self._on_toggle_right_panel)
            menu.AddSubItem("View", f"{bottom_check}Bottom Panel", self._on_toggle_bottom_panel)
            menu.AddSubItem("View", f"{status_check}Status Bar", self._on_toggle_status_bar)
            
            # Panel control shortcuts
            menu.AddSubItem("View", "---", None)  # Separator
            menu.AddSubItem("View", "Show All Panels", self._on_show_all_panels)
            menu.AddSubItem("View", "Hide All Panels", self._on_hide_all_panels)

            # Bars menu (organized like TradingView)
            menu.AddItem("Bars")
            
            # Bar/Candle Charts section
            bar_chart_check = "[X] " if self.chart_type == "BarChart" else "[ ] "
            candlestick_check = "[X] " if self.chart_type == "Candlestick" else "[ ] "
            hollow_candles_check = "[X] " if self.chart_type == "HollowCandles" else "[ ] "
            volume_candles_check = "[X] " if self.chart_type == "VolumeCandles" else "[ ] "
            
            menu.AddSubItem("Bars", f"{bar_chart_check}Çubuk Grafikler", self._on_chart_type_bar_chart)
            menu.AddSubItem("Bars", f"{candlestick_check}Mum Grafikler", self._on_chart_type_candlestick)
            menu.AddSubItem("Bars", f"{hollow_candles_check}İçi Boş Mumlar", self._on_chart_type_hollow_candles)
            menu.AddSubItem("Bars", f"{volume_candles_check}Hacimli Mumlar", self._on_chart_type_volume_candles)
            
            # Separator
            menu.AddSubItem("Bars", "---", None)
            
            # Line Charts section
            line_check = "[X] " if self.chart_type == "Line" else "[ ] "
            marked_line_check = "[X] " if self.chart_type == "MarkedLine" else "[ ] "
            
            menu.AddSubItem("Bars", f"{line_check}Çizgi", self._on_chart_type_line)
            menu.AddSubItem("Bars", f"{marked_line_check}İşaretli Çizgi", self._on_chart_type_marked_line)
            
            # Separator
            menu.AddSubItem("Bars", "---", None)
            
            # Alternative Charts section
            heikin_ashi_check = "[X] " if self.chart_type == "HeikinAshi" else "[ ] "
            renko_check = "[X] " if self.chart_type == "Renko" else "[ ] "
            
            menu.AddSubItem("Bars", f"{heikin_ashi_check}Heiken Ashi", self._on_chart_type_heikin_ashi)
            menu.AddSubItem("Bars", f"{renko_check}Renko", self._on_chart_type_renko)

            # Tools menu
            menu.AddItem("Tools")
            menu.AddSubItem("Tools", "Analysis", self._on_analysis_tools)
            menu.AddSubItem("Tools", "Settings", self._on_settings)

    def _setup_panel_content(self):
        """Setup content for all panels. Called initially and after RefreshLayout."""
        # Setup panel labels to see which panel is where
        upper_panel = self.dataPlotterDearPyGui2.GetUpperPanel()
        if upper_panel:
            upper_panel.AddText("=== UPPER PANEL ===", color=[255, 255, 0, 255])
            upper_panel.AddText("Window resize: Height adjusts with ratio")

        left_panel = self.dataPlotterDearPyGui2.GetLeftPanel()
        if left_panel:
            left_panel.AddText("=== LEFT PANEL ===", color=[255, 255, 0, 255])
            left_panel.AddText("Fixed width - no resize")

        right_panel = self.dataPlotterDearPyGui2.GetRightPanel()
        if right_panel:
            right_panel.AddText("=== RIGHT PANEL ===", color=[255, 255, 0, 255])
            right_panel.AddText("Fixed width - right aligned")

        bottom_panel = self.dataPlotterDearPyGui2.GetBottomPanel()
        if bottom_panel:
            bottom_panel.AddText("=== BOTTOM PANEL ===", color=[255, 255, 0, 255])
            bottom_panel.AddText("Height ratio: 20% - Trading controls will be here")

        main_panel = self.dataPlotterDearPyGui2.GetMainPanel()
        if main_panel and self.dataPlotterDearPyGui2.show_main_panel:
            main_panel.AddText("=== MAIN PANEL ===", color=[255, 255, 0, 255])

                # # Add moving averages if requested
                # if hasattr(self, 'current_show_moving_average') and self.current_show_moving_average:
                #     ma_data = self._prepare_moving_average_data(self.current_trader)
                #     if ma_data:
                #         panel0.AddPlot(
                #             plot_type="line",
                #             series_data=ma_data,
                #             options={"title": "Moving Averages", "height": 400}
                #         )
                #
                # # Panel 1: Volume chart
                # panel1 = main_panel.AddPanel(1, title="Volume", height_ratio=1)
                # volume_data = self._prepare_volume_data(self.current_trader)
                # if volume_data:
                #     panel1.AddPlot(
                #         plot_type="bar",
                #         series_data=volume_data,
                #         options={"title": "Volume Chart", "height": 150}
                #     )

        # Setup status bar
        status_bar = self.dataPlotterDearPyGui2.GetStatusBar()
        if status_bar:
            status_bar.SetText("Chart loaded successfully - Ready for analysis")
            status_bar.AddIndicator("progress", 1.0)  # Loading complete


    def _setup_price_chart_content(self, panel, chart_type_name):
        # Prepare and add chart data based on selected type
        if hasattr(self, 'current_trader'):
            print(f"DEBUG: current_trader exists: {self.current_trader}")
            print(f"DEBUG: Chart type selected: {chart_type_name}")

            if chart_type_name in ["BarChart", "Candlestick", "HollowCandles", "VolumeCandles"]:
                # OHLC-based charts
                ohlc_data = self._prepare_ohlc_data(self.current_trader)
                print(f"DEBUG: OHLC data prepared: {ohlc_data is not None}")
                if ohlc_data:
                    print(f"DEBUG: Adding {chart_type_name} plot to panel")
                    panel.AddPlot(
                        plot_type="candlestick",  # All OHLC types use candlestick for now
                        series_data=ohlc_data,
                        options={"title": f"{chart_type_name} Chart", "height": 400}
                    )
                    print(f"DEBUG: {chart_type_name} plot added successfully")
                else:
                    print("DEBUG: OHLC data is None or empty")

            elif chart_type_name in ["Line", "MarkedLine"]:
                # Line charts using only Close prices
                line_data = self._prepare_line_data(self.current_trader)
                print(f"DEBUG: Line data prepared: {line_data is not None}")
                if line_data:
                    print(f"DEBUG: Adding {chart_type_name} plot to panel0")
                    panel.AddPlot(
                        plot_type="line",
                        series_data=line_data,
                        options={"title": f"{chart_type_name} Chart", "height": 400}
                    )
                    print(f"DEBUG: {chart_type_name} plot added successfully")
                else:
                    print("DEBUG: Line data is None or empty")

            elif chart_type_name == "HeikinAshi":
                # Heiken Ashi chart
                ha_data = self._prepare_heiken_ashi_data(self.current_trader)
                print(f"DEBUG: Heiken Ashi data prepared: {ha_data is not None}")
                if ha_data:
                    print("DEBUG: Adding Heiken Ashi candlestick plot to panel0")
                    panel.AddPlot(
                        plot_type="candlestick",
                        series_data=ha_data,
                        options={"title": "Heiken Ashi Chart", "height": 400}
                    )
                    print("DEBUG: Heiken Ashi plot added successfully")
                else:
                    print("DEBUG: Heiken Ashi data is None or empty")

            elif chart_type_name == "Renko":
                # Renko chart (placeholder for future implementation)
                print("DEBUG: Renko not yet implemented, falling back to OHLC")
                ohlc_data = self._prepare_ohlc_data(self.current_trader)
                if ohlc_data:
                    panel.AddPlot(
                        plot_type="candlestick",
                        series_data=ohlc_data,
                        options={"title": "Renko Chart (OHLC fallback)", "height": 400}
                    )

        else:
            print("DEBUG: current_trader does not exist")



    # Panel visibility toggle callbacks
    def _on_toggle_upper_panel(self, sender, app_data, user_data):
        """Toggle upper panel visibility."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            # Update the framework's visibility setting
            self.dataPlotterDearPyGui2.show_upper_panel = not self.dataPlotterDearPyGui2.show_upper_panel
            # Refresh the layout to reflect changes
            self.dataPlotterDearPyGui2.RefreshLayout()
            print(f"Upper panel visibility toggled to: {self.dataPlotterDearPyGui2.show_upper_panel}")

    def _on_toggle_left_panel(self, sender, app_data, user_data):
        """Toggle left panel visibility."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            # Update the framework's visibility setting
            self.dataPlotterDearPyGui2.show_left_panel = not self.dataPlotterDearPyGui2.show_left_panel
            # Refresh the layout to reflect changes
            self.dataPlotterDearPyGui2.RefreshLayout()
            print(f"Left panel visibility toggled to: {self.dataPlotterDearPyGui2.show_left_panel}")

    def _on_toggle_right_panel(self, sender, app_data, user_data):
        """Toggle right panel visibility."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            # Update the framework's visibility setting
            self.dataPlotterDearPyGui2.show_right_panel = not self.dataPlotterDearPyGui2.show_right_panel
            # Refresh the layout to reflect changes
            self.dataPlotterDearPyGui2.RefreshLayout()
            print(f"Right panel visibility toggled to: {self.dataPlotterDearPyGui2.show_right_panel}")

    def _on_toggle_bottom_panel(self, sender, app_data, user_data):
        """Toggle bottom panel visibility."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            # Update the framework's visibility setting
            self.dataPlotterDearPyGui2.show_bottom_panel = not self.dataPlotterDearPyGui2.show_bottom_panel
            # Refresh the layout to reflect changes
            self.dataPlotterDearPyGui2.RefreshLayout()
            print(f"Bottom panel visibility toggled to: {self.dataPlotterDearPyGui2.show_bottom_panel}")

    def _on_toggle_main_panel(self, sender, app_data, user_data):
        """Toggle main panel visibility."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            # Update the framework's visibility setting
            self.dataPlotterDearPyGui2.show_main_panel = not self.dataPlotterDearPyGui2.show_main_panel
            # Refresh the layout to reflect changes
            self.dataPlotterDearPyGui2.RefreshLayout()
            print(f"Main panel visibility toggled to: {self.dataPlotterDearPyGui2.show_main_panel}")

    def _on_toggle_status_bar(self, sender, app_data, user_data):
        """Toggle status bar visibility."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            status_bar = self.dataPlotterDearPyGui2.GetStatusBar()
            if status_bar:
                current_visibility = getattr(status_bar, 'visible', True)
                status_bar.SetVisibility(not current_visibility)
                print(f"Status bar visibility toggled to: {not current_visibility}")

    def _on_show_all_panels(self, sender, app_data, user_data):
        """Show all panels."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            # Set all panel visibility flags to True
            self.dataPlotterDearPyGui2.show_upper_panel = True
            self.dataPlotterDearPyGui2.show_left_panel = True
            self.dataPlotterDearPyGui2.show_main_panel = True
            self.dataPlotterDearPyGui2.show_right_panel = True
            self.dataPlotterDearPyGui2.show_bottom_panel = True
            self.dataPlotterDearPyGui2.show_status_bar = True
            # Refresh layout to apply changes
            self.dataPlotterDearPyGui2.RefreshLayout()
            print("All panels shown")

    def _on_hide_all_panels(self, sender, app_data, user_data):
        """Hide all panels except menu."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            # Set all panel visibility flags to False (except menu)
            self.dataPlotterDearPyGui2.show_upper_panel = False
            self.dataPlotterDearPyGui2.show_left_panel = False
            self.dataPlotterDearPyGui2.show_main_panel = False
            self.dataPlotterDearPyGui2.show_right_panel = False
            self.dataPlotterDearPyGui2.show_bottom_panel = False
            self.dataPlotterDearPyGui2.show_status_bar = False
            # Refresh layout to apply changes
            self.dataPlotterDearPyGui2.RefreshLayout()
            print("All panels hidden")

    # Bar/Candle Chart callbacks
    def _on_chart_type_bar_chart(self, sender, app_data, user_data):
        """Switch to Bar Chart type."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            self.chart_type = "BarChart"
            self._refresh_chart()
            print("Chart type changed to Çubuk Grafikler")

    def _on_chart_type_candlestick(self, sender, app_data, user_data):
        """Switch to Candlestick chart type."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            self.chart_type = "Candlestick"
            self._refresh_chart()
            print("Chart type changed to Mum Grafikler")

    def _on_chart_type_hollow_candles(self, sender, app_data, user_data):
        """Switch to Hollow Candles chart type."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            self.chart_type = "HollowCandles"
            self._refresh_chart()
            print("Chart type changed to İçi Boş Mumlar")

    def _on_chart_type_volume_candles(self, sender, app_data, user_data):
        """Switch to Volume Candles chart type."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            self.chart_type = "VolumeCandles"
            self._refresh_chart()
            print("Chart type changed to Hacimli Mumlar")

    # Line Chart callbacks
    def _on_chart_type_line(self, sender, app_data, user_data):
        """Switch to Line chart type."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            self.chart_type = "Line"
            self._refresh_chart()
            print("Chart type changed to Çizgi")

    def _on_chart_type_marked_line(self, sender, app_data, user_data):
        """Switch to Marked Line chart type."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            self.chart_type = "MarkedLine"
            self._refresh_chart()
            print("Chart type changed to İşaretli Çizgi")

    # Alternative Chart callbacks
    def _on_chart_type_heikin_ashi(self, sender, app_data, user_data):
        """Switch to Heiken Ashi chart type."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            self.chart_type = "HeikinAshi"
            self._refresh_chart()
            print("Chart type changed to Heiken Ashi")

    def _on_chart_type_renko(self, sender, app_data, user_data):
        """Switch to Renko chart type."""
        if hasattr(self, 'dataPlotterDearPyGui2'):
            self.chart_type = "Renko"
            self._refresh_chart()
            print("Chart type changed to Renko")

    def _refresh_chart(self):
        """Refresh chart with new type by recreating content."""
        # Refresh layout to update menu checkmarks and chart content
        self.dataPlotterDearPyGui2.RefreshLayout()

    def create_config_file(self, configFilePath):
        self.mySystem.write_params_to_file(configFilePath,
                                           self.mySystem.bUseParamsFromInputFile,
                                           self.mySystem.CurrentRunIndex,
                                           self.mySystem.TotalRunCount,

                                           self.mySystem.bOptEnabled,
                                           self.mySystem.bIdealGetiriHesapla,
                                           self.mySystem.bIstatistikleriHesapla,
                                           self.mySystem.bIstatistikleriEkranaYaz,
                                           self.mySystem.bGetiriIstatistikleriEkranaYaz,
                                           self.mySystem.bIstatistikleriDosyayaYaz,
                                           self.mySystem.bOptimizasyonIstatistiklerininBasliklariniDosyayaYaz,
                                           self.mySystem.bOptimizasyonIstatistikleriniDosyayaYaz,

                                           self.mySystem.bSinyalleriEkranaCiz,
                                           self.mySystem.ParamsInputFileName,
                                           self.mySystem.IstatistiklerOutputFileName,
                                           self.mySystem.IstatistiklerOptOutputFileName)

    def run_with_single_trader(self):
        # --------------------------------------------------------------
        # Read market data (equivalent to .GrafikVerileri operations)
        print("Loading market data...")
        self.loadMarketData()
        # self.loadMarketDataFromSqliteDB()

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

        # --------------------------------------------------------------
        self.mySystem.create_modules().initialize(self.EpochTime, self.DateTime, self.Date, self.Time, self.Open, self.High, self.Low, self.Close, self.Volume, self.Lot)

        self.mySystem.reset()
        self.mySystem.initialize_params_with_defaults()
        self.mySystem.set_params_for_single_run()

        # --------------------------------------------------------------
        self.indicatorManager = self.mySystem.myIndicators

        # self.Most, self.ExMov = self.calculate_most(period=21, percent=1.0)
        self.Most, self.ExMov = self.indicatorManager.calculate_most(period=21, percent=1.0)

        self.Ma5 = self.indicatorManager.calculate_ema(self.Close, 5)
        self.Ma8 = self.indicatorManager.calculate_ema(self.Close, 8)
        self.Ma13= self.indicatorManager.calculate_ema(self.Close, 13)
        self.Ma21 = self.indicatorManager.calculate_ema(self.Close, 21)
        self.Ma50 = self.indicatorManager.calculate_ema(self.Close, 50)
        self.Ma100 = self.indicatorManager.calculate_ema(self.Close, 100)
        self.Ma200 = self.indicatorManager.calculate_ema(self.Close, 200)

        # --------------------------------------------------------------
        for i in range(self.mySystem.get_trader_count()):
            trader = self.mySystem.get_trader(i)
            trader_id = trader.Id

            DateTimes = ["25.05.2025 14:30:00", "02.06.2025 14:00:00"]
            Dates = ["01.01.1900", "01.01.2100"]
            Times = ["09:30:00", "11:59:00"]

            trader.reset_date_times
            trader.set_date_times(DateTimes[0], DateTimes[1])

            trader.Signals.KarAlEnabled = False
            trader.Signals.ZararKesEnabled = False
            trader.Signals.GunSonuPozKapatEnabled = False
            trader.Signals.TimeFilteringEnabled = True

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

            if (self.mySystem.bIdealGetiriHesapla):
                trader.ideal_getiri_hesapla()

            if (self.mySystem.bIstatistikleriHesapla):
                trader.istatistikleri_hesapla()
                pass

            if (self.mySystem.bIstatistikleriEkranaYaz):
                # trader.istatistikleri_ekrana_yaz(1)
                pass

            if (self.mySystem.bGetiriIstatistikleriEkranaYaz):
                # trader.istatistikleri_ekrana_yaz(2)
                pass

            if (self.mySystem.bIstatistikleriDosyayaYaz):
                trader.istatistikleri_dosyaya_yaz(self.mySystem.IstatistiklerOutputFileName)
                pass

            trader.update_data_frame()
            print(trader._df)
            print(f'BakiyeInitialized = {trader._df.attrs["BakiyeInitialized"]}')
            trader.write_data_frame_to_file_as_tabular("trading_data_tabular.txt")
            trader.write_statistics_to_file_as_tabular("trading_statistics_tabular.txt")

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
            pass

        # --------------------------------------------------------------
        print("Plotting market data...")
        self.active_trader = self.mySystem.get_trader(0)
        # self.plotData()
        # self.plotData2(self.active_trader)
        # self.plotData3(self.active_trader)  # matplotlib version - DISABLED
        
        # Use Dear PyGui version instead
        # self.plotData3_DearPyGui(self.active_trader)
        # self.plotData4_DearPyGui(self.active_trader)
        self.plotDataFinal(self.active_trader)

        # --------------------------------------------------------------
        # Show timing reports
        self.dataManager.reportTimes()
        self.mySystem.reportTimes()

        print(self.BakiyeFiyatList[0])
        print(self.BakiyeFiyatList[1])

    def run_with_multiple_trader(self):
        # --------------------------------------------------------------
        # Read market data (equivalent to .GrafikVerileri operations)
        print("Loading market data...")
        self.loadMarketData()
        # self.loadMarketDataFromSqliteDB()

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

        # --------------------------------------------------------------
        self.mySystem.create_modules().initialize(self.EpochTime, self.DateTime, self.Date, self.Time, self.Open, self.High, self.Low, self.Close, self.Volume, self.Lot)

        self.mySystem.reset()
        self.mySystem.initialize_params_with_defaults()
        self.mySystem.set_params_for_single_run()

        # --------------------------------------------------------------
        self.indicatorManager = self.mySystem.myIndicators

        # self.Most, self.ExMov = self.calculate_most(period=21, percent=1.0)
        self.Most, self.ExMov = self.indicatorManager.calculate_most(period=21, percent=1.0)

        self.Ma5 = self.indicatorManager.calculate_ema(self.Close, 5)
        self.Ma8 = self.indicatorManager.calculate_ema(self.Close, 8)
        self.Ma13 = self.indicatorManager.calculate_ema(self.Close, 13)
        self.Ma21 = self.indicatorManager.calculate_ema(self.Close, 21)

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


                trader.update_data_frame()
                print(trader._df)
                print(f'BakiyeInitialized = {trader._df.attrs["BakiyeInitialized"]}')
                trader.write_data_frame_to_file_as_tabular("trading_data_tabular.txt")
                trader.write_statistics_to_file_as_tabular("trading_statistics_tabular.txt")

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
        # self.plotData3(self.active_trader)  # matplotlib version - DISABLED
        
        # Use Dear PyGui version instead
        # self.plotData3_DearPyGui(self.active_trader)
        # self.plotData4_DearPyGui(self.active_trader)

        # --------------------------------------------------------------
        # Show timing reports
        self.dataManager.reportTimes()
        self.mySystem.reportTimes()

        print(self.BakiyeFiyatList[0])
        print(self.BakiyeFiyatList[1])

    def run_optimization_with_single_trader(self):
        # --------------------------------------------------------------
        # Read market data (equivalent to .GrafikVerileri operations)
        print("Loading market data...")
        self.loadMarketData()
        # self.loadMarketDataFromSqliteDB()

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

        # --------------------------------------------------------------
        self.mySystem.create_modules().initialize(self.EpochTime, self.DateTime, self.Date, self.Time, self.Open, self.High, self.Low, self.Close, self.Volume, self.Lot)

        self.mySystem.GrafikSembol = "BTCUSD"
        self.mySystem.GrafikPeriyot = "01"
        self.mySystem.SistemAdi = "my_sistem_01"

        self.mySystem.reset()
        self.mySystem.initialize_params_with_defaults()

        # --------------------------------------------------------------
        self.indicatorManager = self.mySystem.myIndicators

        # --------------------------------------------------------------
        # enable for single run
        self.mySystem.set_params_for_single_run()
        self.mySystem.clear_input_params()
        self.mySystem.set_input_params(0, "Simple")
        self.mySystem.set_input_params(1, "8")
        self.mySystem.set_input_params(2, "13")
        self.mySystem.set_input_params(3, "21")
        self.mySystem.set_input_params(4, "50")
        self.mySystem.set_input_params(5, "100")
        self.mySystem.set_input_params(5, "200")

        # enable for optimization
        self.mySystem.set_params_for_optimizasyon()
        self.mySystem.clear_input_params()
        self.mySystem.set_input_params(0, "Simple")
        self.mySystem.set_input_params(1, "8")
        self.mySystem.set_input_params(2, "13")
        self.mySystem.set_input_params(3, "21")
        self.mySystem.set_input_params(4, "50")
        self.mySystem.set_input_params(5, "100")
        self.mySystem.set_input_params(5, "200")

        persistentIndicatorManager = CIndicatorManager()
        persistentIndicatorManager.reset()
        persistentIndicatorManager.initialize(self.EpochTime, self.DateTime, self.Date, self.Time, self.Open, self.High, self.Low, self.Close, self.Volume, self.Lot)
        self.Most, self.ExMov = persistentIndicatorManager.calculate_most(period=21, percent=2)

        # # enable to create configFile (only once), then disable
        # configFileName = "config.txt"
        # configFilePath = os.path.join(self.mySystem.InputsDir, configFileName)
        # self.create_config_file(configFilePath)
        #
        # # configFile must be prepared, already
        # self.mySystem.read_params_from_file(configFilePath).update_sistem_parametreleri()

        # Parameter scanning for period and percent
        # period_values = [8, 13, 21, 34, 50]  # Different period values to test
        # percent_values = [0.5, 1.0, 1.5, 2.0, 2.5]  # Different percent values to test
        #         veya asagidaki gibi kullanim
        # Parameter scanning for period and percent
        period_start = 8
        period_end = 50
        period_increment = 1
        
        percent_start = 0.5
        percent_end = 2.5
        percent_increment = 0.5
        
        best_result = None
        best_period = None
        best_percent = None
        optimization_results = []
        
        # Generate period values using range
        period_values = list(range(period_start, period_end + 1, period_increment))
        
        # Generate percent values using increment
        percent_values = []
        current_percent = percent_start
        while current_percent <= percent_end:
            percent_values.append(round(current_percent, 1))  # Round to avoid floating point issues
            current_percent += percent_increment
        
        print(f"Period values to test: {period_values}")
        print(f"Percent values to test: {percent_values}")
        total_combinations = len(period_values) * len(percent_values)
        print(f"Total combinations: {total_combinations}")
        print("=" * 50)

        current_iteration = 0
        for period in period_values:
            for percent in percent_values:
                current_iteration += 1
                progress_percent = (current_iteration / total_combinations) * 100
                print(f"[{current_iteration}/{total_combinations}] ({progress_percent:.1f}%) Testing period={period}, percent={percent}")
                
                # Run trading simulation for this parameter combination
                result = self.run_single_optimization_test(period, percent)
                optimization_results.append(result)
                
                # Print current result
                # self.print_current_result(result)
                self.print_current_result_2(result)
                
                # Track best result (example: highest final balance)
                if best_result is None or result['final_balance'] > best_result['final_balance']:
                    best_result = result
                    best_period = period
                    best_percent = percent
        
        print(f"\nOptimization completed!")
        print(f"Best parameters: period={best_period}, percent={best_percent}")
        print(f"Best result: {best_result}")
        
        # Write optimization results to file
        # self.write_optimization_results_to_file(self.mySystem.OutputsDir, optimization_results, best_result, best_period, best_percent)
        self.write_optimization_results_to_file_2(self.mySystem.OutputsDir, optimization_results, best_result, best_period, best_percent)

        # Use best parameters for final run and plotting
        # self.Most, self.ExMov = self.calculate_most(period=best_period, percent=best_percent)
        self.Most, self.ExMov = self.indicatorManager.calculate_most(period=best_period, percent=best_percent)

    def get_horizontal_levels(self):
        """
        YonList ve SeviyeList verilerine göre yatay çizgi seviyelerini döndürür.
        KOD2'nin mantığına göre sinyal değişimlerini yakalar,
        F geldiğinde resetler. Plot etmez, sadece tek liste döndürür.

        Returns:
            list: Yatay çizgi seviyeleri listesi
        """
        if not self.YonList or not self.SeviyeList or len(self.YonList) != len(self.SeviyeList):
            print("Debug: Geçersiz giriş verisi")
            return []

        print(f"Debug: YonList length: {len(self.YonList)}, SeviyeList length: {len(self.SeviyeList)}")

        horizontal_levels = []
        current_signal = None

        # Sinyal değişimlerini yakala
        for i, direction in enumerate(self.YonList):
            level = self.SeviyeList[i]

            # Geçerli seviye olmalı
            if not direction or level == 0.0:
                continue

            # Yeni sinyal başlıyorsa
            if direction != current_signal and direction in ['A', 'S']:
                horizontal_levels.append(level)
                print(f"Debug: Yeni sinyal {direction} @ {i}, level {level:.2f}")
                current_signal = direction

            # 'F' geldiğinde sinyal sıfırlanır
            elif direction == 'F':
                print(f"Debug: Reset sinyali 'F' @ {i}")
                current_signal = None

        # Duplicate temizle
        unique_levels = list(set(horizontal_levels))
        # unique_levels.sort()  # İstersen açabilirsin

        print(f"Debug: Toplam {len(unique_levels)} seviye bulundu")
        if unique_levels:
            print(f"Debug: Seviyeler: {[f'{lvl:.2f}' for lvl in unique_levels[:10]]}")

        return unique_levels

    def get_signal_segments(self):
        """
        YonList ve SeviyeList'e göre her aktif sinyal segmentini döndürür.
        'A' veya 'S' başladığında segment başlar, 'F' veya yön değişimi ile biter.

        Returns:
            list of dict: [{ "level": float, "start": int, "end": int, "direction": str }]
        """
        segments = []
        current_signal = None
        start_index = None
        level = None

        for i, (yon, seviye) in enumerate(zip(self.YonList, self.SeviyeList)):
            if yon in ['A', 'S']:
                if current_signal is None:
                    # yeni sinyal başlat
                    current_signal = yon
                    start_index = i
                    level = seviye
                elif current_signal != yon:
                    # yön değişti → önceki segmenti kapat
                    segments.append({
                        "level": level,
                        "start": start_index,
                        "end": i - 1,
                        "direction": current_signal
                    })
                    # yeni segment aç
                    current_signal = yon
                    start_index = i
                    level = seviye
            elif yon == 'F' and current_signal is not None:
                # sinyal kapanıyor
                segments.append({
                    "level": level,
                    "start": start_index,
                    "end": i - 1,
                    "direction": current_signal
                })
                current_signal = None
                start_index = None
                level = None

        # eğer sona kadar açık kaldıysa kapat
        if current_signal is not None:
            segments.append({
                "level": level,
                "start": start_index,
                "end": len(self.YonList) - 1,
                "direction": current_signal
            })

        print(f"DEBUG: {len(segments)} segments found")
        return segments

    def plotDataFinal(self, trader):

        # Time array boşsa, basit index array oluştur
        if len(self.Time) == 0:
            print("=== WARNING: Time array boş! Index array oluşturuluyor ===")
            time_array = list(range(len(self.Close)))
        else:
            time_array = self.Time

        balance = trader.Lists.BakiyeFiyatList
        getiriFiyatList = trader.Lists.GetiriFiyatList
        getiriKz = trader.Lists.GetiriKz
        getiriKzNet = trader.Lists.GetiriKzNet
        karZararPuanList = trader.Lists.KarZararPuanList
        karZararFiyatList = trader.Lists.KarZararFiyatList

        # Calculate additional data
        farkList = [0.0] * len(trader.Lists.BakiyeFiyatList)
        for i in range(len(trader.Lists.BakiyeFiyatList)):
            farkList[i] = trader.Lists.BakiyeFiyatList[i] - trader.Lists.GetiriFiyatList[i]

        farkList2 = [0.0] * len(trader.Lists.GetiriKz)
        for i in range(len(trader.Lists.GetiriKz)):
            farkList2[i] = trader.Lists.GetiriKz[i] - trader.Lists.GetiriKzNet[i]

        print(f"farkList: {farkList[-1] if farkList else 'Empty'}")
        print(f"farkList2: {farkList2[-1] if farkList2 else 'Empty'}")

        print("=== plotData başlıyor ===")
        self.dataPlotter2.ClearData()

        self.dataPlotter2.SetData(trader)

        self.dataPlotter2.AddData(0, balance, "balance")
        self.dataPlotter2.AddData(1, getiriFiyatList, "getiriFiyatList")
        self.dataPlotter2.AddData(2, getiriKz, "getiriKz")
        self.dataPlotter2.AddData(3, getiriKzNet, "getiriKzNet")
        self.dataPlotter2.AddData(4, karZararPuanList, "karZararPuanList")
        self.dataPlotter2.AddData(5, karZararFiyatList, "karZararFiyatList")

        self.dataPlotter2.Show()
        print("=== plotData bitti ===")




if __name__ == "__main__":
    print("Hello, Gemini!")

    print("algoTrader, started!")

    algoTrader = AlgoTrader()

    choice = 2
    if choice == 0:
        algoTrader.run_with_single_trader()
    elif choice == 1:
        algoTrader.run_with_multiple_trader()
    elif choice == 2:
        algoTrader.run_optimization_with_single_trader()
    else:
        pass

    print("algoTrader, finished!")
