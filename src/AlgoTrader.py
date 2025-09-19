import pandas as pd
import numpy as np
import os
from datetime import datetime
from src.DataManager import DataManager
from src.DataPlotter import DataPlotter
from src.SqliteDataManager import SqliteDataManager
from src.SystemWrapper import SystemWrapper
from src.Utils import CUtils
from src.IndicatorManager import CIndicatorManager

class AlgoTrader:
    def __init__(self):
        self.sqliteDataManager = SqliteDataManager()
        self.dataManager = DataManager()
        self.dataPlotter = DataPlotter()
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
        self.plotData2(self.active_trader)

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
