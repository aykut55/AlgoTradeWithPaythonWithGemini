import pandas as pd
import numpy as np
import os
import sys
import time
import json
from datetime import datetime
from typing import List, Dict, Any, TypeAlias
from numpy.typing import NDArray
from src.DataManager import DataManager
from src.DataPlotter import DataPlotter
from src.DataPlotter2 import DataPlotter2
from src.DataPlotterDearPyGui import DataPlotterDearPyGui
from src.DataPlotterDearPyGui2 import DataPlotterDearPyGui2
from src.SqliteDataManager import SqliteDataManager
from src.SystemWrapper import SystemWrapper
from src.Utils import CUtils
from src.IndicatorManager import CIndicatorManager
import matplotlib.pyplot as plt
import lightningchart as lc
from lightningchart_trader import TAChart
import random
from src.DataPlotterImgBundle import DataPlotterImgBundle

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.float_format", lambda x: f"{x:.0f}")   # bilimsel gösterim kapalı

# imgui_bundle imports for plotting
try:
    from imgui_bundle import imgui, immapp, implot, imgui_ctx, ImVec4, ImVec2, IM_COL32
    IMGUI_AVAILABLE = True
except ImportError:
    IMGUI_AVAILABLE = False
    print("Warning: imgui_bundle not installed. Install with: pip install imgui-bundle")

# Import DataPlotter (new multi-panel system)
try:
    from src.DataPlotterImgBundle import DataPlotterImgBundle, DataType, Panel
    DATAPLOTTER_AVAILABLE = True
except ImportError:
    DATAPLOTTER_AVAILABLE = False
    print("Warning: DataPlotter not available")

FloatArray1D: TypeAlias = NDArray[np.floating[Any]]

class AlgoTrader:
    def __init__(self):
        self.sqliteDataManager = SqliteDataManager()
        self.dataManager = DataManager()
        self.dataPlotter = DataPlotter()
        self.dataPlotterDearPyGui = DataPlotterDearPyGui()
        self.dataPlotterDearPyGui2 = DataPlotterDearPyGui2()
        self.dataPlotter2 = DataPlotter2()
        self.dataPlotterImgBundle = DataPlotterImgBundle()
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

        trader.reset_date_times()
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

    def write_optimization_results_to_file_3(self, output_dir, df : 'DataFrame'):
        """
        Write single optimization result to file in tabular format.
        First call creates file with header, subsequent calls append data rows.
        Each iteration appends one row to the same file with fixed column widths.

        Args:
            output_dir: Directory to save the file
            df: DataFrame containing optimization results
        """
        if df.empty:
            return

        import os
        import json

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Define filename (same file for entire optimization run)
        filename = os.path.join(output_dir, "optimization_results_tabular.txt")
        widths_filename = os.path.join(output_dir, ".column_widths.json")

        # Check if file exists - if not, write header first
        file_exists = os.path.exists(filename)

        # Helper function to format values based on column name and type
        def format_value(col, val):
            """Format a value based on column name and type"""
            if isinstance(val, float):
                if 'percent' in col.lower() or 'rate' in col.lower() or 'yuzde' in col.lower():
                    # Values are already in percent format (e.g., 2.5 = 2.5%), no need to multiply by 100
                    return f"{val:.2f}"
                elif 'ratio' in col.lower():
                    return f"{val:.3f}"
                else:
                    return f"{val:.2f}"
            elif isinstance(val, int):
                return f"{val}"
            else:
                return f"{val}"

        # Get headers from DataFrame columns (convert snake_case to PascalCase)
        headers = []
        for col in df.columns:
            # Convert snake_case to PascalCase
            header = ''.join(word.capitalize() for word in col.split('_'))
            # Special cases for display
            if header == 'WinRate':
                header = 'WinRate%'
            elif header == 'MaxDdPercent':
                header = 'MaxDD%'
            elif header == 'GetiriFiyatYuzde':
                header = 'GetiriFiyatYuzde%'
            elif header == 'GetiriFiyatYuzdeNet':
                header = 'GetiriFiyatYuzdeNet%'
            headers.append(header)

        # Load or calculate column widths
        if not file_exists:
            # First iteration - calculate column widths based on header + estimated max value length
            column_widths = []
            for i, col in enumerate(df.columns):
                # Start with header length
                max_width = len(headers[i])

                # Estimate max data width based on column type
                # For safety, use generous estimates
                if 'iteration' in col.lower():
                    estimated_width = 8  # e.g., "10000"
                elif 'period' in col.lower():
                    estimated_width = 6  # e.g., "100"
                elif 'percent' in col.lower() or 'rate' in col.lower() or 'yuzde' in col.lower():
                    estimated_width = 8  # e.g., "100.00"
                elif 'ratio' in col.lower():
                    estimated_width = 8  # e.g., "10.000"
                elif isinstance(df.iloc[-1][col], float):
                    estimated_width = 12  # e.g., "100000.00"
                elif isinstance(df.iloc[-1][col], int):
                    estimated_width = 10  # e.g., "100000"
                else:
                    estimated_width = 15  # text columns

                max_width = max(max_width, estimated_width)

                # Add padding (3 spaces minimum)
                column_widths.append(max_width + 10)

            # Save column widths to file for consistency
            with open(widths_filename, 'w') as f:
                json.dump(column_widths, f)

            # Write header
            with open(filename, 'w', encoding='utf-8') as f:
                # Write headers with calculated widths (left-aligned)
                header_line = ""
                for i, header in enumerate(headers):
                    header_line += header.ljust(column_widths[i])
                f.write(header_line.rstrip() + "\n")

                # Write separator line
                separator = ""
                for width in column_widths:
                    separator += "-" * width
                f.write(separator.rstrip() + "\n")
        else:
            # Load column widths from file for consistency
            try:
                with open(widths_filename, 'r') as f:
                    column_widths = json.load(f)
            except:
                # Fallback: recalculate if widths file is missing
                column_widths = [max(len(headers[i]), 15) + 3 for i in range(len(headers))]

        # Append last row of DataFrame (every iteration)
        last_row = df.iloc[-1]
        with open(filename, 'a', encoding='utf-8') as f:
            data_line = ""
            for i, col in enumerate(df.columns):
                val = last_row[col]
                formatted_val = format_value(col, val)
                # Right-align numbers, left-align text for better readability
                if isinstance(val, (int, float)):
                    data_line += formatted_val.ljust(column_widths[i])
                else:
                    data_line += formatted_val.rjust(column_widths[i])

            f.write(data_line.rstrip() + "\n")
            f.flush()  # Force write to disk immediately

    def write_optimization_results_to_file_4(self, output_dir, df : 'DataFrame', best_result, best_period, best_percent):
        """
        Write complete optimization results to files using DataFrame.
        Creates CSV and detailed text report with all metrics in tabular format.

        Args:
            output_dir: Directory to save the files
            df: DataFrame containing all optimization results
            best_result: Dictionary with best result metrics
            best_period: Best period parameter
            best_percent: Best percent parameter
        """
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Sort by final_balance descending to show best results first
        df = df.sort_values('final_balance', ascending=False)

        # Add ranking column
        df['rank'] = range(1, len(df) + 1)

        # Write to CSV
        csv_filename = os.path.join(output_dir, f"optimization_results_detailed_{current_time}.csv")
        df.to_csv(csv_filename, index=False)
        print(f"Detailed optimization results saved to: {csv_filename}")

        # TODO 1: DONE - Write comprehensive text report with statistics
        # TODO 2: DONE - Write DETAILED OPTIMIZATION REPORT from df
        txt_filename = os.path.join(output_dir, f"optimization_report_detailed_{current_time}.txt")
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("=== DETAILED OPTIMIZATION REPORT (All Metrics) ===\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("=== BEST RESULT (All Metrics) ===\n")
            for key, value in best_result.items():
                if isinstance(value, float):
                    if 'percent' in key.lower() or 'rate' in key.lower() or 'yuzde' in key.lower():
                        # Values are already in percent format, no need to multiply by 100
                        f.write(f"{key}: {value:.2f}%\n")
                    elif 'ratio' in key.lower():
                        f.write(f"{key}: {value:.3f}\n")
                    else:
                        f.write(f"{key}: {value:.2f}\n")
                else:
                    f.write(f"{key}: {value}\n")
            f.write("\n")

            # TODO 1: DONE - Write statistics from df
            f.write(f"=== STATISTICS ===\n")
            f.write(f"Total tests run: {len(df)}\n")
            f.write(f"Best balance: {df['final_balance'].max():.2f}\n")
            f.write(f"Worst balance: {df['final_balance'].min():.2f}\n")
            f.write(f"Average balance: {df['final_balance'].mean():.2f}\n")
            f.write(f"Standard deviation: {df['final_balance'].std():.2f}\n")
            f.write("\n")

            # TODO 3: DONE - Write all data rows in tabular format
            # Using similar approach from write_optimization_results_to_file_3()
            f.write(f"=== ALL RESULTS (Tabular Format) ===\n")

            # Helper function to format values based on column name and type
            def format_value(col, val):
                """Format a value based on column name and type"""
                if isinstance(val, float):
                    if 'percent' in col.lower() or 'rate' in col.lower() or 'yuzde' in col.lower():
                        # Values are already in percent format (e.g., 2.5 = 2.5%)
                        return f"{val:.2f}"
                    elif 'ratio' in col.lower():
                        return f"{val:.3f}"
                    else:
                        return f"{val:.2f}"
                elif isinstance(val, int):
                    return f"{val}"
                else:
                    return f"{val}"

            # Get headers from DataFrame columns (convert snake_case to PascalCase)
            headers = []
            for col in df.columns:
                # Convert snake_case to PascalCase
                header = ''.join(word.capitalize() for word in col.split('_'))
                # Special cases for display
                if header == 'WinRate':
                    header = 'WinRate%'
                elif header == 'MaxDdPercent':
                    header = 'MaxDD%'
                elif header == 'GetiriFiyatYuzde':
                    header = 'GetiriFiyatYuzde%'
                elif header == 'GetiriFiyatYuzdeNet':
                    header = 'GetiriFiyatYuzdeNet%'
                headers.append(header)

            # Calculate column widths based on header + estimated max value length
            column_widths = []
            for i, col in enumerate(df.columns):
                # Start with header length
                max_width = len(headers[i])

                # Estimate max data width based on column type
                if 'iteration' in col.lower():
                    estimated_width = 8  # e.g., "10000"
                elif 'period' in col.lower():
                    estimated_width = 6  # e.g., "100"
                elif 'percent' in col.lower() or 'rate' in col.lower() or 'yuzde' in col.lower():
                    estimated_width = 8  # e.g., "100.00"
                elif 'ratio' in col.lower():
                    estimated_width = 8  # e.g., "10.000"
                elif 'rank' in col.lower():
                    estimated_width = 6  # e.g., "1000"
                elif col in df.columns and df[col].dtype in ['float64', 'float32']:
                    estimated_width = 12  # e.g., "100000.00"
                elif col in df.columns and df[col].dtype in ['int64', 'int32']:
                    estimated_width = 10  # e.g., "100000"
                else:
                    estimated_width = 15  # text columns

                max_width = max(max_width, estimated_width)

                # Add padding (3 spaces minimum)
                column_widths.append(max_width + 3)

            # Write headers with calculated widths (left-aligned)
            header_line = ""
            for i, header in enumerate(headers):
                header_line += header.ljust(column_widths[i])
            f.write(header_line.rstrip() + "\n")

            # Write separator line
            separator = ""
            for width in column_widths:
                separator += "-" * width
            f.write(separator.rstrip() + "\n")

            # Write all data rows
            for idx, row in df.iterrows():
                data_line = ""
                for i, col in enumerate(df.columns):
                    val = row[col]
                    formatted_val = format_value(col, val)
                    # Right-align numbers, left-align text for better readability
                    if isinstance(val, (int, float)):
                        data_line += formatted_val.ljust(column_widths[i])
                    else:
                        data_line += formatted_val.rjust(column_widths[i])

                f.write(data_line.rstrip() + "\n")

        print(f"Detailed optimization report saved to: {txt_filename}")

        # TODO 4: DONE - Print summary to console using df
        print(f"\n=== DETAILED OPTIMIZATION SUMMARY ===")
        print(f"Best Period: {best_period}")
        print(f"Best Percent: {best_percent}")
        print(f"Best Final Balance: {best_result['final_balance']:.2f}")
        print(f"Total Tests: {len(df)}")
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
        print(f"    İslem Sayisi: {result.get('islem_sayisi', 'N/A')}, Alış Sayisi: {result.get('alis_sayisi', 'N/A')}")
        print(f"    Satış Sayisi: {result.get('satis_sayisi', 'N/A')}, Net Kar: {result.get('net_kar', 'N/A')}")
        print(f"    Toplam Komisyon: {result.get('komisyon_fiyat', 'N/A'):.2f}")
        print(f"    Max Kar: {result.get('max_kar', 'N/A'):.2f}")
        print(f"    Max Zarar: {result.get('max_zarar', 'N/A'):.2f}")
        print(f"    Max DD: {result.get('max_dd', 'N/A'):.2f}, Max DD %: {result.get('max_dd_percent', 'N/A'):.2%}")
        print(f"    Sharpe Ratio: {result.get('sharpe_ratio', 'N/A'):.3f}, Sortino Ratio: {result.get('sortino_ratio', 'N/A'):.3f}")
                    
        # Print remaining metrics if they exist
        metrics_to_skip = {'period', 'percent', 'final_balance', 'total_trades', 'profit_trades', 'loss_trades', 
                          'win_rate', 'islem_sayisi', 'alis_sayisi', 'satis_sayisi', 'net_kar', 'toplam_komisyon',
                          'max_kar', 'max_zarar', 'max_dd', 'max_dd_percent', 'sharpe_ratio', 'sortino_ratio'}
        
        other_metrics = {k: v for k, v in result.items() if k not in metrics_to_skip}
        if other_metrics:
            # print(f"    Other metrics: {other_metrics}")
            pass

    def print_current_result_3(self, result):
        """Print current optimization result in tabular format (DataFrame-like)"""

        # Header'ı sadece bir kere yazdır (ilk koşumda)
        if not hasattr(self, '_header_printed') or not self._header_printed:
            # Header satırı
            headers = [
                "Period",
                "Percent",
                "FinalBalance",
                "TotalTrades",
                "ProfitTrades",
                "LossTrades",
                "WinRate%",
                "IslemSayisi",
                "AlisSayisi",
                "SatisSayisi",
                "NetKar",
                "Komisyon",
                "MaxKar",
                "MaxZarar",
                "MaxDD",
                "MaxDD%",
                "Sharpe",
                "Sortino"
            ]
            print("\t".join(headers))
            print("-" * 150)  # Ayırıcı çizgi
            self._header_printed = True

        # Data satırı (tek satırda, tab-separated)
        values = [
            f"{result['period']}",
            f"{result['percent']:.1f}",
            f"{result['final_balance']:.2f}",
            f"{result['total_trades']}",
            f"{result['profit_trades']}",
            f"{result['loss_trades']}",
            f"{result['win_rate'] * 100:.2f}",
            f"{result.get('islem_sayisi', 0)}",
            f"{result.get('alis_sayisi', 0)}",
            f"{result.get('satis_sayisi', 0)}",
            f"{result.get('net_kar', 0):.2f}",
            f"{result.get('komisyon_fiyat', 0):.2f}",
            f"{result.get('max_kar', 0):.2f}",
            f"{result.get('max_zarar', 0):.2f}",
            f"{result.get('max_dd', 0):.2f}",
            f"{result.get('max_dd_percent', 0) * 100:.2f}",
            f"{result.get('sharpe_ratio', 0):.3f}",
            f"{result.get('sortino_ratio', 0):.3f}"
        ]
        print("\t".join(values))

    def loadMarketData(self):

        filePath             = "C:\\data\\csvFiles\\VIP\\01\\VIP-X030-T.csv"
        filePath             = "C:\\data\\VIP-X030-T\\VIP'VIP-X030-T_1.csv"
        dirName              = os.path.dirname(filePath)
        fileName             = os.path.basename(filePath)
        name_no_ext, ext     = os.path.splitext(fileName)
        drive, path_no_drive = os.path.splitdrive(filePath)
        norm                 = os.path.normpath(filePath)

        dataCount = 100_000
        # self.dataManager.set_read_mode_all_data()
        self.dataManager.set_read_mode_last_n(dataCount)
        # self.dataManager.set_read_mode_first_n(dataCount)
        # self.dataManager.set_read_mode_range(10000, 20000)
        # self.dataManager.set_read_mode_after_date("2024.01.01")
        # self.dataManager.set_read_mode_after_date("2024.11.01 09:30:00")
        # self.dataManager.set_read_mode_before_date("2024.12.01")
        # self.dataManager.set_read_mode_between_dates("2024.11.01", "2024.11.30")

        start_time = time.time()
        self.dataManager.load_prices_from_csv_with_bar_data_reader(filePath)
        self.dataManager.print_sample_bars(5)
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000  # Saniyeyi 1000 ile çarpıp ms'ye çeviriyoruz
        # print(f"Geçen süre: {elapsed_ms:.2f} ms")

        start_time = time.time()
        self.dataManager.build_data_frame()
        # print(self.dataManager.get_dataframe().tail())
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000  # Saniyeyi 1000 ile çarpıp ms'ye çeviriyoruz
        # print(f"Geçen süre: {elapsed_ms:.2f} ms")

        start_time = time.time()
        # self.dataManager.add_time_columns()
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000  # Saniyeyi 1000 ile çarpıp ms'ye çeviriyoruz
        # print(f"Geçen süre: {elapsed_ms:.2f} ms")

        self.V           = self.dataManager
        self.Df          = self.dataManager.get_dataframe()
        self.EpochTime   = self.dataManager.get_epoch_time_array()
        self.DateTime    = self.dataManager.get_date_time_string_array_new()
        self.Date        = self.dataManager.get_date_string_array_new()
        self.Time        = self.dataManager.get_time_string_array_new()
        self.DateTimeObj = self.dataManager.get_date_time_array_new()
        self.DateObj     = self.dataManager.get_date_array_new()
        self.TimeObj     = self.dataManager.get_time_array_new()
        self.Open        = self.dataManager.get_open_array()
        self.High        = self.dataManager.get_high_array()
        self.Low         = self.dataManager.get_low_array()
        self.Close       = self.dataManager.get_close_array()
        self.Volume      = self.dataManager.get_volume_array()
        self.Lot         = self.dataManager.get_lot_array()
        self.BarCount    = self.dataManager.get_bar_count()
        self.ItemsCount  = self.dataManager.get_items_count()

        print("\n=====================================================================")
        print("FilePath    :", os.path.join(filePath))
        print("FileName    :", os.path.join(fileName))

        print("BarCount    :", self.BarCount)
        print("ItemsCount  :", self.ItemsCount)
        print("=====================================================================\n")

        print_last_elements_enabled = False
        print_first_elements_enabled = False

        if print_last_elements_enabled:
            print("\n=====================================================================")
            print("Last Elements:")
            print("\n=====================================================================")
            print("InputTime   :", self.dataManager.get_timestamp_array()[-5:])
            print("EpochTime   :", self.dataManager.get_epoch_time_array()[-5:])

            print("DateTime    :", self.dataManager.get_date_time_array_as_str()[-5:])
            print("Date        :", self.dataManager.get_date_array_as_str()[-5:])
            print("Time        :", self.dataManager.get_time_array_as_str()[-5:])

            print("DateTimeObj :", self.dataManager.get_date_time_array_new()[-5:])
            print("DateObj     :", self.dataManager.get_date_array_new()[-5:])
            print("TimeObj     :", self.dataManager.get_time_array_new()[-5:])

            print("Open        :", self.dataManager.get_open_array()[-5:])
            print("High        :", self.dataManager.get_high_array()[-5:])
            print("Low         :", self.dataManager.get_low_array()[-5:])
            print("Close       :", self.dataManager.get_close_array()[-5:])
            print("Volume      :", self.dataManager.get_volume_array()[-5:])
            print("Lot         :", self.dataManager.get_lot_array()[-5:])
            print("Delta       :", self.dataManager.get_delta_array()[-5:])
            print("Delta (%)   :", self.dataManager.get_delta_pct_array()[-5:])

        if print_first_elements_enabled:
            print("\n=====================================================================")
            print("First Elements:")
            print("\n=====================================================================")
            print("InputTime   :", self.dataManager.get_timestamp_array()[5:])
            print("EpochTime   :", self.dataManager.get_epoch_time_array()[5:])
    
            print("DateTime    :", self.dataManager.get_date_time_array_as_str()[5:])
            print("Date        :", self.dataManager.get_date_array_as_str()[5:])
            print("Time        :", self.dataManager.get_time_array_as_str()[5:])
    
            print("DateTimeObj :", self.dataManager.get_date_time_array_new()[5:])
            print("DateObj     :", self.dataManager.get_date_array_new()[5:])
            print("TimeObj     :", self.dataManager.get_time_array_new()[5:])
    
            print("Open        :", self.dataManager.get_open_array()[5:])
            print("High        :", self.dataManager.get_high_array()[5:])
            print("Low         :", self.dataManager.get_low_array()[5:])
            print("Close       :", self.dataManager.get_close_array()[5:])
            print("Volume      :", self.dataManager.get_volume_array()[5:])
            print("Lot         :", self.dataManager.get_lot_array()[5:])
            print("Delta       :", self.dataManager.get_delta_array()[5:])
            print("Delta (%)   :", self.dataManager.get_delta_pct_array()[5:])
            print("\n=====================================================================")

        # name = input("Devam etmek icin tusa basiniz 3 ")
        # print("")

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

                # Create signal segments and plot
                segments, combined_data, combined_data_normalized = self.create_signal_segments(trader)
                # if combined_data:
                #     self.plot_combined_signals(combined_data)

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

    def reset_trader_for_new_iteration_during_optimization(self, trader: 'AlgoTrader'):

        trader.reset()
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

    def initialize_strategy(self,  i: int, trader: 'AlgoTrader'):

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
      
        return 0     
    
    def run_strategy(self,  i: int, trader: 'AlgoTrader'):

        trader_id = trader.Id
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
            return 0
        
        if (trader_id == 0): 
        
            FlatOl = False

            Al = self.myUtils.yukari_kesti(i, self.ExMov, self.Most)

            Sat = self.myUtils.asagi_kesti(i, self.ExMov, self.Most)

            KarAl = trader.Signals.KarAlEnabled
            KarAl = KarAl and trader.KarAlZararKes.son_fiyata_gore_kar_al_seviye_hesapla(i, 5, 50, 1000) != 0

            ZararKes = trader.Signals.ZararKesEnabled
            ZararKes = ZararKes and trader.KarAlZararKes.son_fiyata_gore_zarar_kes_seviye_hesapla(i, -1, -10, 1000) != 0
        
        elif (trader_id == 1): 
        
            FlatOl = False

            Al = self.myUtils.yukari_kesti(i, self.ExMov, self.Most)

            Sat = self.myUtils.asagi_kesti(i, self.ExMov, self.Most)

            KarAl = trader.Signals.KarAlEnabled
            KarAl = KarAl and trader.KarAlZararKes.son_fiyata_gore_kar_al_seviye_hesapla(i, 5, 50, 1000) != 0

            ZararKes = trader.Signals.ZararKesEnabled
            ZararKes = ZararKes and trader.KarAlZararKes.son_fiyata_gore_zarar_kes_seviye_hesapla(i, -1, -10, 1000) != 0
        
        elif (trader_id == 2): 
        
            FlatOl = False

            Al = self.myUtils.yukari_kesti(i, self.ExMov, self.Most)

            Sat = self.myUtils.asagi_kesti(i, self.ExMov, self.Most)

            KarAl = trader.Signals.KarAlEnabled
            KarAl = KarAl and trader.KarAlZararKes.son_fiyata_gore_kar_al_seviye_hesapla(i, 5, 50, 1000) != 0

            ZararKes = trader.Signals.ZararKesEnabled
            ZararKes = ZararKes and trader.KarAlZararKes.son_fiyata_gore_zarar_kes_seviye_hesapla(i, -1, -10, 1000) != 0
        
        elif (trader_id == 3): 
        
            FlatOl = False

            Al = self.myUtils.yukari_kesti(i, self.ExMov, self.Most)

            Sat = self.myUtils.asagi_kesti(i, self.ExMov, self.Most)

            KarAl = trader.Signals.KarAlEnabled
            KarAl = KarAl and trader.KarAlZararKes.son_fiyata_gore_kar_al_seviye_hesapla(i, 5, 50, 1000) != 0

            ZararKes = trader.Signals.ZararKesEnabled
            ZararKes = ZararKes and trader.KarAlZararKes.son_fiyata_gore_zarar_kes_seviye_hesapla(i, -1, -10, 1000) != 0

        else:
            pass

        IsSonYonA = trader.is_son_yon_a()

        IsSonYonS = trader.is_son_yon_s()

        IsSonYonF = trader.is_son_yon_f()

        # useTimeFiltering = trader.Signals.TimeFilteringEnabled

        trader.emirleri_setle(i, Al, Sat, FlatOl, PasGec, KarAl, ZararKes)

        # TODO : YAPILACAK
        trader.islem_zaman_filtresi_uygula(i)

        trader.emir_sonrasi_dongu_foksiyonlarini_calistir(i)

        # if Al:
        #     print(f"bar {i} : trader {trader.Id} : Signal : Buy, Close {self.Close[i]}")
        # if Sat:
        #     print(f"bar {i} : trader {trader.Id} : Signal : Sell, Close {self.Close[i]}")

        # self.KarZararPuanList = trader.Lists.KarZararPuanList
        # self.KarZararFiyatList = trader.Lists.KarZararFiyatList
        # self.BakiyeFiyatList = trader.Lists.BakiyeFiyatList
        # self.YonList = trader.Lists.YonList
        # self.SeviyeList = trader.Lists.SeviyeList

        return 0       
    
    def finalize_strategy(self,  i: int, trader: 'AlgoTrader'):    

        trader_id = trader.Id

        if (trader_id == 0):
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

        elif (trader_id == 1):
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

        elif (trader_id == 2):
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

        elif (trader_id == 3):
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

        else:
            pass

        return 0         

    def create_trade_signals(self, trader: 'AlgoTrader'):
        trader_id = trader.Id

        if (trader_id == 0):
            pass
        elif (trader_id == 1):
            pass
        elif (trader_id == 2):
            pass
        elif (trader_id == 3):
            pass
        else:
            pass

        combined_data = []
        combined_data_normalized = []
        segments, combined_data, combined_data_normalized  = self.create_signal_segments(trader)
        if segments:  # En az bir segment varsa
            trader.segments = segments
            trader.combined_data = combined_data
            trader.combined_data_normalized = combined_data_normalized

        return 0

    def update_data_frame(self, trader: 'AlgoTrader', save_to_file: bool = False):

        trader_id = trader.Id

        if (trader_id == 0):
            trader.update_data_frame()
            # print(trader._df.head())

            # print(f'BakiyeInitialized = {trader._df.attrs["BakiyeInitialized"]}')

            if save_to_file:

                # Tablo formatında kaydet
                trader.write_data_frame_to_file_as_tabular("trading_data_0_tabular.txt")
                trader.write_statistics_to_file_as_tabular("trading_statistics_0_tabular.txt")

                # CSV formatında kaydet
                trader.write_data_frame_to_file("trading_0_data.csv")

                # # Excel formatında kaydet
                # trader.write_data_frame_to_file("trading_0_data.xlsx")
                #
                # # JSON formatında kaydet
                # trader.write_data_frame_to_file("trading_0_data.json")
                #
                # # HTML formatında kaydet
                # trader.write_data_frame_to_file("trading_0_data.html")
                #
                # # DataFrame kaydet
                # trader._df.to_csv('trading_0_data1.csv', index=False)
                #
                # trader._df.to_parquet('trading_0_data1.parquet', index=False)
                #
                # trader._df.to_pickle('trading_0_data1.pkl')
                #
                # trader._df.to_excel('trading_0_data1.xlsx', index=False)
                #
                # trader._df.to_feather('trading_0_data1.feather')

            pass

        elif (trader_id == 1):
            trader.update_data_frame()
            # print(trader._df.head())
            
            # print(f'BakiyeInitialized = {trader._df.attrs["BakiyeInitialized"]}')

            if save_to_file:
            
                # Tablo formatında kaydet
                trader.write_data_frame_to_file_as_tabular("trading_data_1_tabular.txt")
                trader.write_statistics_to_file_as_tabular("trading_statistics_1_tabular.txt")

                # CSV formatında kaydet
                trader.write_data_frame_to_file("trading_1_data.csv")

                # # Excel formatında kaydet
                # trader.write_data_frame_to_file("trading_1_data.xlsx")
                #
                # # JSON formatında kaydet
                # trader.write_data_frame_to_file("trading_1_data.json")
                #
                # # HTML formatında kaydet
                # trader.write_data_frame_to_file("trading_1_data.html")
                #
                # # DataFrame kaydet
                # trader._df.to_csv('trading_1_data1.csv', index=False)
                #
                # trader._df.to_parquet('trading_1_data1.parquet', index=False)
                #
                # trader._df.to_pickle('trading_1_data1.pkl')
                #
                # trader._df.to_excel('trading_1_data1.xlsx', index=False)
                #
                # trader._df.to_feather('trading_1_data1.feather')

            pass

        elif (trader_id == 2):
            trader.update_data_frame()
            # print(trader._df.head())
            
            # print(f'BakiyeInitialized = {trader._df.attrs["BakiyeInitialized"]}')

            if save_to_file:
            
                # Tablo formatında kaydet
                trader.write_data_frame_to_file_as_tabular("trading_data_2_tabular.txt")
                trader.write_statistics_to_file_as_tabular("trading_statistics_2_tabular.txt")

                # CSV formatında kaydet
                trader.write_data_frame_to_file("trading_2_data.csv")

                # # Excel formatında kaydet
                # trader.write_data_frame_to_file("trading_2_data.xlsx")
                #
                # # JSON formatında kaydet
                # trader.write_data_frame_to_file("trading_2_data.json")
                #
                # # HTML formatında kaydet
                # trader.write_data_frame_to_file("trading_2_data.html")
                #
                # # DataFrame kaydet
                # trader._df.to_csv('trading_2_data1.csv', index=False)
                #
                # trader._df.to_parquet('trading_2_data1.parquet', index=False)
                #
                # trader._df.to_pickle('trading_2_data1.pkl')
                #
                # trader._df.to_excel('trading_2_data1.xlsx', index=False)
                #
                # trader._df.to_feather('trading_2_data1.feather')

            pass

        elif (trader_id == 3):
            trader.update_data_frame()
            # print(trader._df.head())
            
            # print(f'BakiyeInitialized = {trader._df.attrs["BakiyeInitialized"]}')

            if save_to_file:
            
                # Tablo formatında kaydet
                trader.write_data_frame_to_file_as_tabular("trading_data_3_tabular.txt")
                trader.write_statistics_to_file_as_tabular("trading_statistics_3_tabular.txt")

                # CSV formatında kaydet
                trader.write_data_frame_to_file("trading_3_data.csv")

                # # Excel formatında kaydet
                # trader.write_data_frame_to_file("trading_3_data.xlsx")
                #
                # # JSON formatında kaydet
                # trader.write_data_frame_to_file("trading_3_data.json")
                #
                # # HTML formatında kaydet
                # trader.write_data_frame_to_file("trading_3_data.html")
                #
                # # DataFrame kaydet
                # trader._df.to_csv('trading_3_data1.csv', index=False)
                #
                # trader._df.to_parquet('trading_3_data1.parquet', index=False)
                #
                # trader._df.to_pickle('trading_3_data1.pkl')
                #
                # trader._df.to_excel('trading_3_data1.xlsx', index=False)
                #
                # trader._df.to_feather('trading_3_data1.feather')

            pass

        else:
            pass

        return 0 

    def run_with_single_trader(self):
        # --------------------------------------------------------------  
        print("\nLoading market data...")
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

        # --------------------------------------------------------------
        self.mySystem.create_modules().initialize(self.EpochTime, self.DateTime, self.Date, self.Time, self.Open, self.High, self.Low, self.Close, self.Volume, self.Lot)

        self.mySystem.reset()
        self.mySystem.initialize_params_with_defaults()
        self.mySystem.set_params_for_single_run()

        # --------------------------------------------------------------
        self.indicatorManager = self.mySystem.myIndicators

        self.Most, self.ExMov = self.indicatorManager.calculate_most(period=21, percent=0.5)

        self.Ma5 = self.indicatorManager.calculate_ema(self.Close, 5)
        self.Ma8 = self.indicatorManager.calculate_ema(self.Close, 8)
        self.Ma13= self.indicatorManager.calculate_ema(self.Close, 13)
        self.Ma21 = self.indicatorManager.calculate_ema(self.Close, 21)
        self.Ma50 = self.indicatorManager.calculate_ema(self.Close, 50)
        self.Ma100 = self.indicatorManager.calculate_ema(self.Close, 100)
        self.Ma200 = self.indicatorManager.calculate_ema(self.Close, 200)

        # --------------------------------------------------------------
        print("\nInitializing strategy params...")        
        for i in range(self.mySystem.get_trader_count()):
            trader = self.mySystem.get_trader(i)
            self.initialize_strategy(i, trader)

        # --------------------------------------------------------------
        print("\nRunning strategy...")                
        self.mySystem.start()
        for i in range(self.BarCount):
            for j in range(self.mySystem.get_trader_count()):
                trader = self.mySystem.get_trader(j)
                self.run_strategy(i, trader)
        self.mySystem.stop()

        # --------------------------------------------------------------
        print("\nGetting strategy results...")             
        for i in range(self.mySystem.get_trader_count()):
            trader = self.mySystem.get_trader(i)
            self.finalize_strategy(i, trader)

        # --------------------------------------------------------------
        for i in range(self.mySystem.get_trader_count()):
            # --------------------------------------------------------------
            self.active_trader = self.mySystem.get_trader(i)
            # --------------------------------------------------------------
            print(f"\nTrader {self.active_trader.Id}...")
            # --------------------------------------------------------------
            print("\tGetting trade signals...")
            self.create_trade_signals(self.active_trader)
            # --------------------------------------------------------------
            print("\tUpdating dataFrame...")
            self.update_data_frame(self.active_trader)
            # --------------------------------------------------------------
            print("\tSaving data to files...")
            dstDir = "."
            # self.SavePlotData(self.active_trader, dstDir)
            # --------------------------------------------------------------
            print("\tPlotting market data...")
            self.plotDataImgBundle(self.active_trader)

        # --------------------------------------------------------------
        # Show timing reports
        self.dataManager.reportTimes()
        self.mySystem.reportTimes()

        return 0 

    def run_with_multiple_trader(self, trader_count=4):
        # --------------------------------------------------------------
        print("\nLoading market data...")
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

        # --------------------------------------------------------------
        self.mySystem.create_modules(trader_count).initialize(self.EpochTime, self.DateTime, self.Date, self.Time, self.Open, self.High, self.Low, self.Close, self.Volume, self.Lot)

        self.mySystem.reset()
        self.mySystem.initialize_params_with_defaults()
        self.mySystem.set_params_for_single_run()

        # --------------------------------------------------------------
        self.indicatorManager = self.mySystem.myIndicators

        self.Most, self.ExMov = self.indicatorManager.calculate_most(period=21, percent=0.5)

        self.Ma5 = self.indicatorManager.calculate_ema(self.Close, 5)
        self.Ma8 = self.indicatorManager.calculate_ema(self.Close, 8)
        self.Ma13= self.indicatorManager.calculate_ema(self.Close, 13)
        self.Ma21 = self.indicatorManager.calculate_ema(self.Close, 21)
        self.Ma50 = self.indicatorManager.calculate_ema(self.Close, 50)
        self.Ma100 = self.indicatorManager.calculate_ema(self.Close, 100)
        self.Ma200 = self.indicatorManager.calculate_ema(self.Close, 200)

        # --------------------------------------------------------------
        print("\nInitializing strategy params...")        
        for i in range(self.mySystem.get_trader_count()):
            trader = self.mySystem.get_trader(i)
            self.initialize_strategy(i, trader)

        # --------------------------------------------------------------
        print("\nRunning strategy...")                
        self.mySystem.start()
        for i in range(self.BarCount):
            for j in range(self.mySystem.get_trader_count()):
                trader = self.mySystem.get_trader(j)
                self.run_strategy(i, trader)
        self.mySystem.stop()

        # --------------------------------------------------------------
        print("\nGetting strategy results...")             
        for i in range(self.mySystem.get_trader_count()):
            trader = self.mySystem.get_trader(i)
            self.finalize_strategy(i, trader)

        for i in range(self.mySystem.get_trader_count()):
            # --------------------------------------------------------------
            self.active_trader = self.mySystem.get_trader(i)
            # --------------------------------------------------------------
            print(f"\nTrader {self.active_trader.Id}...")
            # --------------------------------------------------------------
            print("\tGetting trade signals...")
            self.create_trade_signals(self.active_trader)
            # --------------------------------------------------------------
            print("\tUpdating dataFrame...")
            self.update_data_frame(self.active_trader)
            # --------------------------------------------------------------
            print("\tSaving data to files...")
            dstDir = "."
            # self.SavePlotData(self.active_trader, dstDir)
            # --------------------------------------------------------------
            print("\tPlotting market data...")
            # self.plotDataImgBundle(self.active_trader)

        # --------------------------------------------------------------
        # Show timing reports
        self.dataManager.reportTimes()
        self.mySystem.reportTimes()

        return 0 

    def run_optimization_with_single_trader(self):
        # --------------------------------------------------------------  
        print("\nLoading market data...")
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

        # --------------------------------------------------------------
        self.mySystem.create_modules().initialize(self.EpochTime, self.DateTime, self.Date, self.Time, self.Open, self.High, self.Low, self.Close, self.Volume, self.Lot)

        # --------------------------------------------------------------      
        self.mySystem.GrafikSembol = self.dataManager.reader.get_metadata('GrafikSembol')
        self.mySystem.GrafikPeriyot = self.dataManager.reader.get_metadata('GrafikPeriyot')
        self.mySystem.SistemAdi = "my_sistem_01"
    
        # --------------------------------------------------------------    
        self.mySystem.reset()
        self.mySystem.initialize_params_with_defaults()

        # --------------------------------------------------------------
        self.indicatorManager = self.mySystem.myIndicators
        self.indicatorManager.reset()        
        self.indicatorManager.initialize(self.EpochTime, self.DateTime, self.Date, self.Time, self.Open, self.High, self.Low, self.Close, self.Volume, self.Lot)

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

        # --------------------------------------------------------------
        self.Most, self.ExMov = self.indicatorManager.calculate_most(period=21, percent=0.5)

        # --------------------------------------------------------------
        parameter_scanning_method = 0
        if parameter_scanning_method == 0:
            period_start = 8
            period_end = 50
            period_increment = 1
            
            percent_start = 0.5
            percent_end = 2.5
            percent_increment = 0.5

            # Generate period values using range
            period_values = list(range(period_start, period_end + 1, period_increment))
            
            # Generate percent values using increment
            percent_values = []
            current_percent = percent_start
            while current_percent <= percent_end:
                percent_values.append(round(current_percent, 1))  # Round to avoid floating point issues
                current_percent += percent_increment

        elif parameter_scanning_method == 1:
            period_values = [8, 13, 21, 34, 50]         # Different period values to test
            percent_values = [0.5, 1.0, 1.5, 2.0, 2.5]  # Different percent values to test
        else :          
            pass

        print(f"Period values to test: {period_values}")
        print(f"Percent values to test: {percent_values}")
        total_combinations = len(period_values) * len(percent_values)
        print(f"Total combinations: {total_combinations}")
        print("=" * 50)        

        # --------------------------------------------------------------
        best_result = None
        best_period = None
        best_percent = None
        optimization_results = []

        skip_iteration_enabled = True   # if resume, this flag must be set
        skip_iteration = 200            # up to this iteration, the execution will be skipped

        # --------------------------------------------------------------
        df = pd.DataFrame() # Create DataFrame

        # --------------------------------------------------------------
        current_iteration = 0
        for period in period_values:
            for percent in percent_values:
                current_iteration += 1
                progress_percent = (current_iteration / total_combinations) * 100
                if skip_iteration_enabled:
                    if current_iteration < skip_iteration:
                        continue

                print(f"[{current_iteration}/{total_combinations}] "
                    f"({progress_percent:6.2f}%) "
                    f"Testing  period={period:<3} percent={percent:<10}")
                
                # Run trading simulation for this parameter combination
                result = self.run_single_optimization_internal(current_iteration, period, percent)
                optimization_results.append(result)

                # Add result to DataFrame
                df = pd.concat([df, pd.DataFrame([result])], ignore_index=True)

                # Print current result
                # self.print_current_result(result)
                self.print_current_result_3(result)
                
                # df'nin son elemanını write_optimization_results_to_file_3 ile dosyaya yaz
                # write_optimization_results_to_file_3() içinde First iteration ise headeri da dosyaya yaz...
                self.write_optimization_results_to_file_3(self.mySystem.OutputsDir, df)
                
                # Track best result (example: highest final balance)
                if best_result is None or result['final_balance'] > best_result['final_balance']:
                    best_result = result
                    best_period = period
                    best_percent = percent


        # --------------------------------------------------------------
        print(f"\nOptimization completed!")
        print(f"Best parameters: period={best_period}, percent={best_percent}")
        print(f"Best result: {best_result}")

        # Write optimization results to file
        # self.write_optimization_results_to_file(self.mySystem.OutputsDir, optimization_results, best_result, best_period, best_percent)
        self.write_optimization_results_to_file_4(self.mySystem.OutputsDir, df, best_result, best_period, best_percent)

        # # Use best parameters for final run and plotting
        # # self.Most, self.ExMov = self.calculate_most(period=best_period, percent=best_percent)
        # self.Most, self.ExMov = self.indicatorManager.calculate_most(period=best_period, percent=best_percent)        



        """         
        # --------------------------------------------------------------
        print("\nInitializing strategy params...")        
        for i in range(self.mySystem.get_trader_count()):
            trader = self.mySystem.get_trader(i)
            self.initialize_strategy(i, trader)

        # --------------------------------------------------------------
        print("\nRunning strategy...")                
        self.mySystem.start()
        for i in range(self.BarCount):
            for j in range(self.mySystem.get_trader_count()):
                trader = self.mySystem.get_trader(j)
                self.run_strategy(i, trader)
        self.mySystem.stop()

        # --------------------------------------------------------------
        print("\nGetting strategy results...")             
        for i in range(self.mySystem.get_trader_count()):
            trader = self.mySystem.get_trader(i)
            self.finalize_strategy(i, trader)

        # --------------------------------------------------------------
        for i in range(self.mySystem.get_trader_count()):
            # --------------------------------------------------------------
            self.active_trader = self.mySystem.get_trader(i)
            # --------------------------------------------------------------
            print(f"\nTrader {self.active_trader.Id}...")
            # --------------------------------------------------------------
            print("\tGetting trade signals...")
            self.create_trade_signals(self.active_trader)
            # --------------------------------------------------------------
            print("\tUpdating dataFrame...")
            self.update_data_frame(self.active_trader)
            # --------------------------------------------------------------
            print("\tSaving data to files...")
            dstDir = "."
            # self.SavePlotData(self.active_trader, dstDir)
            # --------------------------------------------------------------
            print("\tPlotting market data...")
            self.plotDataImgBundle(self.active_trader)

        # --------------------------------------------------------------
        # Show timing reports
        self.dataManager.reportTimes()
        self.mySystem.reportTimes() 
        """
        return 0 

    def run_single_optimization_internal(self, current_iteration, period, percent):
        # --------------------------------------------------------------
        self.Most, self.ExMov = self.indicatorManager.calculate_most(period, percent)

        # --------------------------------------------------------------
        print("\nInitializing strategy params...")        
        for i in range(self.mySystem.get_trader_count()):
            trader = self.mySystem.get_trader(i)
            self.reset_trader_for_new_iteration_during_optimization(trader)
            self.initialize_strategy(i, trader)

        # --------------------------------------------------------------
        print("\nRunning strategy...")                
        self.mySystem.start()
        for i in range(self.BarCount):
            for j in range(self.mySystem.get_trader_count()):
                trader = self.mySystem.get_trader(j)
                self.run_strategy(i, trader)
        self.mySystem.stop()

        # --------------------------------------------------------------
        print("\nGetting strategy results...")             
        for i in range(self.mySystem.get_trader_count()):
            trader = self.mySystem.get_trader(i)
            self.finalize_strategy(i, trader)

        # --------------------------------------------------------------
        for i in range(self.mySystem.get_trader_count()):
            # --------------------------------------------------------------
            self.active_trader = self.mySystem.get_trader(i)
            # --------------------------------------------------------------
            print(f"\nTrader {self.active_trader.Id}...")
            # --------------------------------------------------------------
            print("\tGetting trade signals...")
            self.create_trade_signals(self.active_trader)
            # --------------------------------------------------------------
            print("\tUpdating dataFrame...")
            # self.update_data_frame(self.active_trader)
            # --------------------------------------------------------------
            print("\tSaving data to files...")
            dstDir = "."
            # self.SavePlotData(self.active_trader, dstDir)
            # --------------------------------------------------------------
            print("\tPlotting market data...")
            # self.plotDataImgBundle(self.active_trader)

        # --------------------------------------------------------------
        trader = self.mySystem.get_trader(0)

        # --------------------------------------------------------------
        # Extract key metrics
        initial_balance = trader.Lists.BakiyeFiyatList[0] if len(trader.Lists.BakiyeFiyatList) > 0 else 0
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

        if len(trader.Lists.KarZararFiyatList) > 0:
            max_kar = max(trader.Lists.KarZararFiyatList)  # En yüksek kar (pozitif değer)
            max_zarar = min(trader.Lists.KarZararFiyatList)  # En büyük zarar (negatif değer)
        else:
            max_kar = 0.0
            max_zarar = 0.0

        metrics = self.calculate_performance_metrics(trader)
        max_dd = metrics['max_dd']
        max_dd_percent = metrics['max_dd_percent']
        sharpe_ratio = metrics['sharpe_ratio']
        sortino_ratio = metrics['sortino_ratio']

        final_balance = bakiye_fiyat_net

        max_kar_fiyat = trader.Statistics.MaxKarFiyat
        max_zarar_fiyat = trader.Statistics.MaxZararFiyat
        min_bakiye_fiyat = trader.Statistics.MinBakiyeFiyat
        max_bakiye_fiyat = trader.Statistics.MaxBakiyeFiyat
        min_bakiye_fiyat_net = trader.Statistics.MinBakiyeFiyatNet
        max_bakiye_fiyat_net = trader.Statistics.MaxBakiyeFiyatNet
        
        profit_factor = trader.Statistics.ProfitFactor
        karli_islem_orani = trader.Statistics.KarliIslemOrani
        min_bakiye_fiyat_yuzde = trader.Statistics.MinBakiyeFiyatYuzde
        max_bakiye_fiyat_yuzde = trader.Statistics.MaxBakiyeFiyatYuzde
        min_bakiye_fiyatNet_yuzde = trader.Statistics.MinBakiyeFiyatNetYuzde
        max_bakiye_fiyatNet_yuzde = trader.Statistics.MaxBakiyeFiyatNetYuzde   

        initial_balance2 = trader.Statistics.IstatistiklerNew["IlkBakiyeFiyat"].strip()

        # self.IstatistiklerNew["GrafikSembol"] = self.GrafikSembol
        # self.IstatistiklerNew["GrafikPeriyot"] = self.GrafikPeriyot
        # self.IstatistiklerNew["SistemId"] = str(self.SistemId)
        # self.IstatistiklerNew["SistemName"] = self.SistemName
        # self.IstatistiklerNew["LastExecutionTime"] = self.LastExecutionTime
        # self.IstatistiklerNew["LastExecutionTimeStart"] = self.LastExecutionTimeStart
        # self.IstatistiklerNew["LastExecutionTimeStop"] = self.LastExecutionTimeStop
        # self.IstatistiklerNew["ExecutionTimeInMSec"] = str(self.ExecutionTimeInMSec)
        # self.IstatistiklerNew["LastExecutionId"] = self.LastExecutionId
        # self.IstatistiklerNew["LastResetTime"] = self.LastResetTime
        # self.IstatistiklerNew["LastStatisticsCalculationTime"] = self.LastStatisticsCalculationTime
        # self.IstatistiklerNew["ToplamGecenSureAy"] = f'{self.ToplamGecenSureAy:.1f}'
        # self.IstatistiklerNew["ToplamGecenSureGun"] = str(self.ToplamGecenSureGun)
        # self.IstatistiklerNew["ToplamGecenSureSaat"] = str(self.ToplamGecenSureSaat)
        # self.IstatistiklerNew["ToplamGecenSureDakika"] = str(self.ToplamGecenSureDakika)
        # self.IstatistiklerNew["ToplamBarSayisi"] = str(self.ToplamBarSayisi)
        # self.IstatistiklerNew["SecilenBarNumarasi"] = str(self.SecilenBarNumarasi)
        # # String tarihleri parse et ("YYYY.MM.DD" formatında)
        # secilen_dt = datetime.datetime.strptime(self.SecilenBarTarihi, "%Y.%m.%d") if isinstance(self.SecilenBarTarihi, str) else self.SecilenBarTarihi
        # ilk_dt = datetime.datetime.strptime(self.IlkBarTarihi, "%Y.%m.%d") if isinstance(self.IlkBarTarihi, str) else self.IlkBarTarihi
        # son_dt = datetime.datetime.strptime(self.SonBarTarihi, "%Y.%m.%d") if isinstance(self.SonBarTarihi, str) else self.SonBarTarihi

        # self.IstatistiklerNew["SecilenBarTarihi"] = secilen_dt.strftime("%d.%m.%Y") if hasattr(secilen_dt, 'strftime') else str(secilen_dt)
        # self.IstatistiklerNew["SecilenBarSaati"] = str(secilen_dt.time()) if hasattr(secilen_dt, 'time') else "00:00:00"
        # self.IstatistiklerNew["IlkBarTarihi"] = ilk_dt.strftime("%d.%m.%Y") if hasattr(ilk_dt, 'strftime') else str(ilk_dt)
        # self.IstatistiklerNew["IlkBarSaati"] = str(ilk_dt.time()) if hasattr(ilk_dt, 'time') else "00:00:00"
        # self.IstatistiklerNew["SonBarTarihi"] = son_dt.strftime("%d.%m.%Y") if hasattr(son_dt, 'strftime') else str(son_dt)
        # self.IstatistiklerNew["SonBarSaati"] = str(son_dt.time()) if hasattr(son_dt, 'time') else "00:00:00"
        # self.IstatistiklerNew["IlkBarIndex"] = str(self.IlkBarIndex)
        # self.IstatistiklerNew["SonBarIndex"] = str(self.SonBarIndex)
        # self.IstatistiklerNew["SonBarAcilisFiyati"] = str(self.SonBarAcilisFiyati)
        # self.IstatistiklerNew["SonBarYuksekFiyati"] = str(self.SonBarYuksekFiyati)
        # self.IstatistiklerNew["SonBarDusukFiyati"] = str(self.SonBarDusukFiyati)
        # self.IstatistiklerNew["SonBarKapanisFiyati"] = str(self.SonBarKapanisFiyati)
        # self.IstatistiklerNew["IlkBakiyeFiyat"] = str(self.IlkBakiyeFiyat)
        # self.IstatistiklerNew["IlkBakiyePuan"] = str(self.IlkBakiyePuan)
        # self.IstatistiklerNew["BakiyeFiyat"] = str(self.BakiyeFiyat)
        # self.IstatistiklerNew["BakiyePuan"] = str(self.BakiyePuan)
        # self.IstatistiklerNew["GetiriFiyat"] = str(self.GetiriFiyat)
        # self.IstatistiklerNew["GetiriPuan"] = str(self.GetiriPuan)
        # self.IstatistiklerNew["GetiriFiyatYuzde"] = str(self.GetiriFiyatYuzde)
        # self.IstatistiklerNew["GetiriPuanYuzde"] = str(self.GetiriPuanYuzde)
        # self.IstatistiklerNew["BakiyeFiyatNet"] = str(self.BakiyeFiyatNet)
        # self.IstatistiklerNew["BakiyePuanNet"] = str(self.BakiyePuanNet)
        # self.IstatistiklerNew["GetiriFiyatNet"] = str(self.GetiriFiyatNet)
        # self.IstatistiklerNew["GetiriPuanNet"] = str(self.GetiriPuanNet)
        # self.IstatistiklerNew["GetiriFiyatYuzdeNet"] = str(self.GetiriFiyatYuzdeNet)
        # self.IstatistiklerNew["GetiriPuanYuzdeNet"] = str(self.GetiriPuanYuzdeNet)
        # self.IstatistiklerNew["GetiriKz"] = str(self.GetiriKz)
        # self.IstatistiklerNew["GetiriKzNet"] = str(self.GetiriKzNet)
        # self.IstatistiklerNew["MinBakiyeFiyat"] = str(self.MinBakiyeFiyat)
        # self.IstatistiklerNew["MaxBakiyeFiyat"] = str(self.MaxBakiyeFiyat)
        # self.IstatistiklerNew["MinBakiyePuan"] = str(self.MinBakiyePuan)
        # self.IstatistiklerNew["MaxBakiyePuan"] = str(self.MaxBakiyePuan)
        # self.IstatistiklerNew["MinBakiyeFiyatYuzde"] = str(self.MinBakiyeFiyatYuzde)
        # self.IstatistiklerNew["MaxBakiyeFiyatYuzde"] = str(self.MaxBakiyeFiyatYuzde)
        # self.IstatistiklerNew["MinBakiyeFiyatIndex"] = str(self.MinBakiyeFiyatIndex)
        # self.IstatistiklerNew["MaxBakiyeFiyatIndex"] = str(self.MaxBakiyeFiyatIndex)
        # self.IstatistiklerNew["MinBakiyePuanIndex"] = str(self.MinBakiyePuanIndex)
        # self.IstatistiklerNew["MaxBakiyePuanIndex"] = str(self.MaxBakiyePuanIndex)
        # self.IstatistiklerNew["MinBakiyeFiyatNet"] = str(self.MinBakiyeFiyatNet)
        # self.IstatistiklerNew["MaxBakiyeFiyatNet"] = str(self.MaxBakiyeFiyatNet)
        # self.IstatistiklerNew["MinBakiyeFiyatNetIndex"] = str(self.MinBakiyeFiyatNetIndex)
        # self.IstatistiklerNew["MaxBakiyeFiyatNetIndex"] = str(self.MaxBakiyeFiyatNetIndex)
        # self.IstatistiklerNew["MinBakiyeFiyatNetYuzde"] = str(self.MinBakiyeFiyatNetYuzde)
        # self.IstatistiklerNew["MaxBakiyeFiyatNetYuzde"] = str(self.MaxBakiyeFiyatNetYuzde)
        # self.IstatistiklerNew["GetiriKzSistem"] = f'{self.GetiriKzSistem:.2f}'
        # self.IstatistiklerNew["GetiriKzSistemYuzde"] = f'{self.GetiriKzSistemYuzde:.2f}'
        # self.IstatistiklerNew["GetiriKzNetSistem"] = f'{self.GetiriKzNetSistem:.2f}'
        # self.IstatistiklerNew["GetiriKzNetSistemYuzde"] = f'{self.GetiriKzNetSistemYuzde:.2f}'
        # self.IstatistiklerNew["IslemSayisi"] = str(self.IslemSayisi)
        # self.IstatistiklerNew["AlisSayisi"] = str(self.AlisSayisi)
        # self.IstatistiklerNew["SatisSayisi"] = str(self.SatisSayisi)
        # self.IstatistiklerNew["FlatSayisi"] = str(self.FlatSayisi)
        # self.IstatistiklerNew["PassSayisi"] = str(self.PassSayisi)
        # self.IstatistiklerNew["KarAlSayisi"] = str(self.KarAlSayisi)
        # self.IstatistiklerNew["ZararKesSayisi"] = str(self.ZararKesSayisi)
        # self.IstatistiklerNew["KazandiranIslemSayisi"] = str(self.KazandiranIslemSayisi)
        # self.IstatistiklerNew["KaybettirenIslemSayisi"] = str(self.KaybettirenIslemSayisi)
        # self.IstatistiklerNew["NotrIslemSayisi"] = str(self.NotrIslemSayisi)
        # self.IstatistiklerNew["KazandiranAlisSayisi"] = str(self.KazandiranAlisSayisi)
        # self.IstatistiklerNew["KaybettirenAlisSayisi"] = str(self.KaybettirenAlisSayisi)
        # self.IstatistiklerNew["NotrAlisSayisi"] = str(self.NotrAlisSayisi)
        # self.IstatistiklerNew["KazandiranSatisSayisi"] = str(self.KazandiranSatisSayisi)
        # self.IstatistiklerNew["KaybettirenSatisSayisi"] = str(self.KaybettirenSatisSayisi)
        # self.IstatistiklerNew["NotrSatisSayisi"] = str(self.NotrSatisSayisi)
        # self.IstatistiklerNew["AlKomutSayisi"] = str(self.AlKomutSayisi)
        # self.IstatistiklerNew["SatKomutSayisi"] = str(self.SatKomutSayisi)
        # self.IstatistiklerNew["PasGecKomutSayisi"] = str(self.PasGecKomutSayisi)
        # self.IstatistiklerNew["KarAlKomutSayisi"] = str(self.KarAlKomutSayisi)
        # self.IstatistiklerNew["ZararKesKomutSayisi"] = str(self.ZararKesKomutSayisi)
        # self.IstatistiklerNew["FlatOlKomutSayisi"] = str(self.FlatOlKomutSayisi)
        # self.IstatistiklerNew["KomisyonIslemSayisi"] = str(self.KomisyonIslemSayisi)
        # self.IstatistiklerNew["KomisyonVarlikAdedSayisi"] = str(self.KomisyonVarlikAdedSayisi)
        # self.IstatistiklerNew["KomisyonCarpan"] = str(self.KomisyonCarpan)
        # self.IstatistiklerNew["KomisyonFiyat"] = str(self.KomisyonFiyat)
        # self.IstatistiklerNew["KomisyonFiyatYuzde"] = str(self.KomisyonFiyatYuzde)
        # self.IstatistiklerNew["KomisyonuDahilEt"] = str(self.KomisyonuDahilEt)
        # self.IstatistiklerNew["KarZararFiyat"] = str(self.KarZararFiyat)
        # self.IstatistiklerNew["KarZararFiyatYuzde"] = str(self.KarZararFiyatYuzde)
        # self.IstatistiklerNew["KarZararPuan"] = str(self.KarZararPuan)
        # self.IstatistiklerNew["ToplamKarFiyat"] = str(self.ToplamKarFiyat)
        # self.IstatistiklerNew["ToplamZararFiyat"] = str(self.ToplamZararFiyat)
        # self.IstatistiklerNew["NetKarFiyat"] = str(self.NetKarFiyat)
        # self.IstatistiklerNew["ToplamKarPuan"] = str(self.ToplamKarPuan)
        # self.IstatistiklerNew["ToplamZararPuan"] = str(self.ToplamZararPuan)
        # self.IstatistiklerNew["NetKarPuan"] = str(self.NetKarPuan)
        # self.IstatistiklerNew["MaxKarFiyat"] = str(self.MaxKarFiyat)
        # self.IstatistiklerNew["MaxZararFiyat"] = str(self.MaxZararFiyat)
        # self.IstatistiklerNew["MaxKarPuan"] = str(self.MaxKarPuan)
        # self.IstatistiklerNew["MaxZararPuan"] = str(self.MaxZararPuan)
        # self.IstatistiklerNew["MaxZararFiyatIndex"] = str(self.MaxZararFiyatIndex)
        # self.IstatistiklerNew["MaxKarFiyatIndex"] = str(self.MaxKarFiyatIndex)
        # self.IstatistiklerNew["MaxZararPuanIndex"] = str(self.MaxZararPuanIndex)
        # self.IstatistiklerNew["MaxKarPuanIndex"] = str(self.MaxKarPuanIndex)
        # self.IstatistiklerNew["KardaBarSayisi"] = str(self.KardaBarSayisi)
        # self.IstatistiklerNew["ZarardaBarSayisi"] = str(self.ZarardaBarSayisi)
        # self.IstatistiklerNew["KarliIslemOrani"] = f'{self.KarliIslemOrani:.2f}'
        # self.IstatistiklerNew["GetiriMaxDD"] = str(self.GetiriMaxDD)
        # self.IstatistiklerNew["GetiriMaxDDTarih"] = "" #self.GetiriMaxDDTarih.strftime("%d.%m.%Y")
        # self.IstatistiklerNew["GetiriMaxDDSaat"] = "" #str(self.GetiriMaxDDTarih.time())
        # self.IstatistiklerNew["GetiriMaxKayip"] = str(self.GetiriMaxKayip)
        # self.IstatistiklerNew["ProfitFactor"] = f'{self.ProfitFactor:.2f}'
        # self.IstatistiklerNew["ProfitFactorSistem"] = f'{self.ProfitFactorSistem:.2f}'
        # self.IstatistiklerNew["OrtAylikIslemSayisi"] = f'{self.OrtAylikIslemSayisi:.2f}'
        # self.IstatistiklerNew["OrtHaftalikIslemSayisi"] = f'{self.OrtHaftalikIslemSayisi:.2f}'
        # self.IstatistiklerNew["OrtGunlukIslemSayisi"] = f'{self.OrtGunlukIslemSayisi:.2f}'
        # self.IstatistiklerNew["OrtSaatlikIslemSayisi"] = f'{self.OrtSaatlikIslemSayisi:.2f}'
        # self.IstatistiklerNew["Sinyal"] = str(self.Sinyal)
        # self.IstatistiklerNew["SonYon"] = str(self.SonYon)
        # self.IstatistiklerNew["PrevYon"] = str(self.PrevYon)
        # self.IstatistiklerNew["SonFiyat"] = str(self.SonFiyat)
        # self.IstatistiklerNew["SonAFiyat"] = str(self.SonAFiyat)
        # self.IstatistiklerNew["SonSFiyat"] = str(self.SonSFiyat)
        # self.IstatistiklerNew["SonFFiyat"] = str(self.SonFFiyat)
        # self.IstatistiklerNew["SonPFiyat"] = str(self.SonPFiyat)
        # self.IstatistiklerNew["PrevFiyat"] = str(self.PrevFiyat)
        # self.IstatistiklerNew["PrevAFiyat"] = str(self.PrevAFiyat)
        # self.IstatistiklerNew["PrevSFiyat"] = str(self.PrevSFiyat)
        # self.IstatistiklerNew["PrevFFiyat"] = str(self.PrevFFiyat)
        # self.IstatistiklerNew["PrevPFiyat"] = str(self.PrevPFiyat)
        # self.IstatistiklerNew["SonBarNo"] = str(self.SonBarNo)
        # self.IstatistiklerNew["SonABarNo"] = str(self.SonABarNo)
        # self.IstatistiklerNew["SonSBarNo"] = str(self.SonSBarNo)
        # self.IstatistiklerNew["SonFBarNo"] = str(self.SonFBarNo)
        # self.IstatistiklerNew["SonPBarNo"] = str(self.SonPBarNo)
        # self.IstatistiklerNew["PrevBarNo"] = str(self.PrevBarNo)
        # self.IstatistiklerNew["PrevABarNo"] = str(self.PrevABarNo)
        # self.IstatistiklerNew["PrevSBarNo"] = str(self.PrevSBarNo)
        # self.IstatistiklerNew["PrevFBarNo"] = str(self.PrevFBarNo)
        # self.IstatistiklerNew["PrevPBarNo"] = str(self.PrevPBarNo)
        # self.IstatistiklerNew["EmirKomut"] = str(self.EmirKomut)
        # self.IstatistiklerNew["EmirStatus"] = str(self.EmirStatus)
        # self.IstatistiklerNew["HisseSayisi"] = str(self.HisseSayisi)
        # self.IstatistiklerNew["KontratSayisi"] = str(self.KontratSayisi)
        # self.IstatistiklerNew["VarlikAdedCarpani"] = str(self.VarlikAdedCarpani)
        # self.IstatistiklerNew["VarlikAdedSayisi"] = str(self.VarlikAdedSayisi)
        # self.IstatistiklerNew["KaymaMiktari"] = str(self.KaymaMiktari)
        # self.IstatistiklerNew["KaymayiDahilEt"] = str(self.KaymayiDahilEt)
        # self.IstatistiklerNew["GetiriFiyatBuAy"] = f'{self.GetiriFiyatBuAy:.2f}'
        # self.IstatistiklerNew["GetiriFiyatAy1"] = f'{self.GetiriFiyatAy1:.2f}'
        # self.IstatistiklerNew["GetiriFiyatAy2"] = f'{self.GetiriFiyatAy2:.2f}'
        # self.IstatistiklerNew["GetiriFiyatAy3"] = f'{self.GetiriFiyatAy3:.2f}'
        # self.IstatistiklerNew["GetiriFiyatAy4"] = f'{self.GetiriFiyatAy4:.2f}'
        # self.IstatistiklerNew["GetiriFiyatAy5"] = f'{self.GetiriFiyatAy5:.2f}'
        # self.IstatistiklerNew["GetiriFiyatBuHafta"] = f'{self.GetiriFiyatBuHafta:.2f}'
        # self.IstatistiklerNew["GetiriFiyatHafta1"] = f'{self.GetiriFiyatHafta1:.2f}'
        # self.IstatistiklerNew["GetiriFiyatHafta2"] = f'{self.GetiriFiyatHafta2:.2f}'
        # self.IstatistiklerNew["GetiriFiyatHafta3"] = f'{self.GetiriFiyatHafta3:.2f}'
        # self.IstatistiklerNew["GetiriFiyatHafta4"] = f'{self.GetiriFiyatHafta4:.2f}'
        # self.IstatistiklerNew["GetiriFiyatHafta5"] = f'{self.GetiriFiyatHafta5:.2f}'
        # self.IstatistiklerNew["GetiriFiyatBuGun"] = f'{self.GetiriFiyatBuGun:.2f}'
        # self.IstatistiklerNew["GetiriFiyatGun1"] = f'{self.GetiriFiyatGun1:.2f}'
        # self.IstatistiklerNew["GetiriFiyatGun2"] = f'{self.GetiriFiyatGun2:.2f}'
        # self.IstatistiklerNew["GetiriFiyatGun3"] = f'{self.GetiriFiyatGun3:.2f}'
        # self.IstatistiklerNew["GetiriFiyatGun4"] = f'{self.GetiriFiyatGun4:.2f}'
        # self.IstatistiklerNew["GetiriFiyatGun5"] = f'{self.GetiriFiyatGun5:.2f}'
        # self.IstatistiklerNew["GetiriFiyatBuSaat"] = f'{self.GetiriFiyatBuSaat:.2f}'
        # self.IstatistiklerNew["GetiriFiyatSaat1"] = f'{self.GetiriFiyatSaat1:.2f}'
        # self.IstatistiklerNew["GetiriFiyatSaat2"] = f'{self.GetiriFiyatSaat2:.2f}'
        # self.IstatistiklerNew["GetiriFiyatSaat3"] = f'{self.GetiriFiyatSaat3:.2f}'
        # self.IstatistiklerNew["GetiriFiyatSaat4"] = f'{self.GetiriFiyatSaat4:.2f}'
        # self.IstatistiklerNew["GetiriFiyatSaat5"] = f'{self.GetiriFiyatSaat5:.2f}'
        # self.IstatistiklerNew["GetiriPuanBuAy"] = f'{self.GetiriPuanBuAy:.2f}'
        # self.IstatistiklerNew["GetiriPuanAy1"] = f'{self.GetiriPuanAy1:.2f}'
        # self.IstatistiklerNew["GetiriPuanAy2"] = f'{self.GetiriPuanAy2:.2f}'
        # self.IstatistiklerNew["GetiriPuanAy3"] = f'{self.GetiriPuanAy3:.2f}'
        # self.IstatistiklerNew["GetiriPuanAy4"] = f'{self.GetiriPuanAy4:.2f}'
        # self.IstatistiklerNew["GetiriPuanAy5"] = f'{self.GetiriPuanAy5:.2f}'
        # self.IstatistiklerNew["GetiriPuanBuHafta"] = f'{self.GetiriPuanBuHafta:.2f}'
        # self.IstatistiklerNew["GetiriPuanHafta1"] = f'{self.GetiriPuanHafta1:.2f}'
        # self.IstatistiklerNew["GetiriPuanHafta2"] = f'{self.GetiriPuanHafta2:.2f}'
        # self.IstatistiklerNew["GetiriPuanHafta3"] = f'{self.GetiriPuanHafta3:.2f}'
        # self.IstatistiklerNew["GetiriPuanHafta4"] = f'{self.GetiriPuanHafta4:.2f}'
        # self.IstatistiklerNew["GetiriPuanHafta5"] = f'{self.GetiriPuanHafta5:.2f}'
        # self.IstatistiklerNew["GetiriPuanBuGun"] = f'{self.GetiriPuanBuGun:.2f}'
        # self.IstatistiklerNew["GetiriPuanGun1"] = f'{self.GetiriPuanGun1:.2f}'
        # self.IstatistiklerNew["GetiriPuanGun2"] = f'{self.GetiriPuanGun2:.2f}'
        # self.IstatistiklerNew["GetiriPuanGun3"] = f'{self.GetiriPuanGun3:.2f}'
        # self.IstatistiklerNew["GetiriPuanGun4"] = f'{self.GetiriPuanGun4:.2f}'
        # self.IstatistiklerNew["GetiriPuanGun5"] = f'{self.GetiriPuanGun5:.2f}'
        # self.IstatistiklerNew["GetiriPuanBuSaat"] = f'{self.GetiriPuanBuSaat:.2f}'
        # self.IstatistiklerNew["GetiriPuanSaat1"] = f'{self.GetiriPuanSaat1:.2f}'
        # self.IstatistiklerNew["GetiriPuanSaat2"] = f'{self.GetiriPuanSaat2:.2f}'
        # self.IstatistiklerNew["GetiriPuanSaat3"] = f'{self.GetiriPuanSaat3:.2f}'
        # self.IstatistiklerNew["GetiriPuanSaat4"] = f'{self.GetiriPuanSaat4:.2f}'
        # self.IstatistiklerNew["GetiriPuanSaat5"] = f'{self.GetiriPuanSaat5:.2f}'

        return {
            'current_iteration': current_iteration,
            # -----------------------------------------------
            'period': period,
            'percent': percent,
            # -----------------------------------------------
            "initial_balance": initial_balance,
            'final_balance': final_balance,
            'getiri_fiyat': getiri_fiyat,
            'komisyon_fiyat': komisyon_fiyat,
            'getiri_fiyat_net': getiri_fiyat_net,
            # -----------------------------------------------
            'total_trades': total_trades,
            'profit_trades': profit_trades,
            'loss_trades': loss_trades,
            'win_rate': win_rate,
            # -----------------------------------------------
            'islem_sayisi': islem_sayisi,
            'alis_sayisi': alis_sayisi,
            'satis_sayisi': satis_sayisi,
            'flat_sayisi': flat_sayisi,
            'pass_sayisi': pass_sayisi,
            'komisyon_islem_sayisi': komisyon_islem_sayisi,
            # -----------------------------------------------
            'bakiye_fiyat_net': bakiye_fiyat_net,
            'getiri_fiyat_yuzde': getiri_fiyat_yuzde,
            'getiri_fiyat_yuzde_net': getiri_fiyat_yuzde_net,

            'getiri_kz': getiri_kz,
            'getiri_kz_net': getiri_kz_net,
            # -----------------------------------------------
            "max_kar" : max_kar,
            "max_zarar": max_zarar,
            # -----------------------------------------------
            "max_dd": max_dd,
            "max_dd_percent" : max_dd_percent,
            "sharpe_ratio" : sharpe_ratio,
            "sortino_ratio" : sortino_ratio,
            # -----------------------------------------------
            "max_kar_fiyat": max_kar_fiyat,
            "max_zarar_fiyat": max_zarar_fiyat,
            "min_bakiye_fiyat": min_bakiye_fiyat,
            "max_bakiye_fiyat": max_bakiye_fiyat,
            "min_bakiye_fiyat_net": min_bakiye_fiyat_net,
            "max_bakiye_fiyat_net": max_bakiye_fiyat_net,
            "profit_factor": profit_factor,
            "karli_islem_orani": karli_islem_orani,
            "min_bakiye_fiyat_yuzde": min_bakiye_fiyat_yuzde,
            "max_bakiye_fiyat_yuzde": max_bakiye_fiyat_yuzde,
            "min_bakiye_fiyatNet_yuzde": min_bakiye_fiyatNet_yuzde,
            "max_bakiye_fiyatNet_yuzde": max_bakiye_fiyatNet_yuzde,

            "initial_balance2": initial_balance2
            
        }

    def calculate_performance_metrics(self, trader):
        """Trader'dan performans metriklerini hesapla"""

        # Bakiye listesinden Max DD hesapla
        bakiye_list = trader.Lists.BakiyeFiyatList
        max_dd, max_dd_percent = self.calculate_max_drawdown(bakiye_list)

        # Getiri yüzdeleri hesapla (her bar için)
        getiri_yuzde_list = []
        for i in range(1, len(bakiye_list)):
            if bakiye_list[i - 1] != 0:
                getiri = (bakiye_list[i] - bakiye_list[i - 1]) / bakiye_list[i - 1] * 100
                getiri_yuzde_list.append(getiri)

        # Sharpe ve Sortino hesapla
        sharpe = self.calculate_sharpe_ratio(getiri_yuzde_list)
        sortino = self.calculate_sortino_ratio(getiri_yuzde_list)

        return {
            'max_dd': max_dd,
            'max_dd_percent': max_dd_percent,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino
        }

    def calculate_max_drawdown(self, bakiye_list):
        max_dd = 0.0
        max_dd_percent = 0.0
        peak = bakiye_list[0] if len(bakiye_list) > 0 else 0

        for bakiye in bakiye_list:
            if bakiye > peak:
                peak = bakiye
            drawdown = peak - bakiye
            if drawdown > max_dd:
                max_dd = drawdown
                max_dd_percent = (drawdown / peak * 100) if peak != 0 else 0.0

        return max_dd, max_dd_percent

    def calculate_sharpe_ratio(self, getiri_list, risk_free_rate=0.0):
        if len(getiri_list) == 0:
            return 0.0
        getiri_array = np.array(getiri_list)
        mean_return = np.mean(getiri_array)
        std_return = np.std(getiri_array, ddof=1)
        if std_return == 0:
            return 0.0
        return (mean_return - risk_free_rate) / std_return

    def calculate_sortino_ratio(self, getiri_list, target_return=0.0):
        if len(getiri_list) == 0:
            return 0.0
        getiri_array = np.array(getiri_list)
        mean_return = np.mean(getiri_array)
        downside_returns = getiri_array[getiri_array < target_return]
        if len(downside_returns) == 0:
            return float('inf')
        downside_std = np.std(downside_returns, ddof=1)
        if downside_std == 0:
            return 0.0
        return (mean_return - target_return) / downside_std





    def run_optimization_with_single_trader_ESKISI(self):
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
                self.print_current_result_3(result)
                
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

        return 0 

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

        # print(f"DEBUG: {len(segments)} segments found")
        return segments

    def plotDataFinal(self, trader):

        # Time array boşsa, basit index array oluştur
        if len(self.Time) == 0:
            print("=== WARNING: Time array boş! Index array oluşturuluyor ===")
            time_array = list(range(len(self.Close)))
        else:
            time_array = self.Time

        LevelZero1 = self.create_level_series(self.BarCount, 0)
        LevelZero2 = self.create_level_series(self.BarCount, 0)

        balance = trader.Lists.BakiyeFiyatList
        bakiye = trader.Lists.BakiyeFiyatList

        getiriFiyatList = trader.Lists.GetiriFiyatList
        getiriFiyatNetList = trader.Lists.GetiriFiyatNetList

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

        # # Listenin sonunda
        # plt.figure(figsize=(12, 6))
        # plt.plot(farkList)
        # plt.title('farkList Debug Plot')
        # plt.grid(True)
        # plt.show()
        #
        # plt.figure(figsize=(12, 8))
        # plt.subplot(2, 1, 1)
        # plt.plot(farkList)
        # plt.title('farkList')
        # plt.grid(True)
        #
        # plt.subplot(2, 1, 2)
        # plt.plot(farkList2)
        # plt.title('farkList2')
        # plt.grid(True)
        #
        # plt.tight_layout()
        # plt.show()

        print(f"farkList: {farkList[-1] if farkList else 'Empty'}")
        print(f"farkList2: {farkList2[-1] if farkList2 else 'Empty'}")

        print("=== plotData başlıyor ===")
        self.dataPlotter2.Clear()

        self.dataPlotter2.SetData(trader)

        symbol = "BTCUSD"
        timeframe = "1min"
        self.dataPlotter2.SetTitle(f"{symbol} {timeframe}")

        self.dataPlotter2.AddYData(0, trader.combined_data_normalized, "_TradingSignals")
        self.dataPlotter2.AddYData(1, LevelZero1, "LevelZero1")
        self.dataPlotter2.AddYData(2, balance, "balance")
        self.dataPlotter2.AddYData(3, bakiye, "bakiye")
        self.dataPlotter2.AddYData(4, getiriFiyatList, "getiriFiyatList")
        self.dataPlotter2.AddYData(5, getiriFiyatNetList, "getiriFiyatNetList")
        self.dataPlotter2.AddYData(6, getiriKz, "getiriKz")
        self.dataPlotter2.AddYData(7, getiriKzNet, "getiriKzNet")
        self.dataPlotter2.AddYData(8, karZararPuanList, "karZararPuanList")
        self.dataPlotter2.AddYData(9, karZararFiyatList, "karZararFiyatList")
        self.dataPlotter2.AddYData(10, farkList, "farkList")
        self.dataPlotter2.AddYData(11, farkList2, "farkList2")

        self.dataPlotter2.AddYData(12, self.Ma5, "Ma5")
        self.dataPlotter2.AddYData(13, self.Ma8, "Ma8")
        self.dataPlotter2.AddYData(14, self.Ma13, "Ma13")
        self.dataPlotter2.AddYData(15, self.Ma21, "Ma21")
        self.dataPlotter2.AddYData(16, self.Ma50, "Ma50")
        self.dataPlotter2.AddYData(17, self.Ma100, "Ma100")
        self.dataPlotter2.AddYData(18, self.Ma200, "Ma200")
        self.dataPlotter2.AddYData(19, self.Most, "Most")
        self.dataPlotter2.AddYData(20, self.ExMov, "ExMov")

        self.dataPlotter2.AddYData(21, LevelZero2, "LevelZero2")

        self.dataPlotter2.RegisterDataSeriesToPanel("_TradingSignals", 1)
        self.dataPlotter2.RegisterDataSeriesToPanel("LevelZero1", 1)
        self.dataPlotter2.SetLineProperties("_TradingSignals", color='cyan', lineWidth=1)
        self.dataPlotter2.SetLineProperties("LevelZero1", color='red', lineWidth=1)
        # self.dataPlotter2.ShowTradingSignals(trader.combined_data, trader.segments)  # Al/sat sinyallerini ekle

        self.dataPlotter2.RegisterDataSeriesToPanel("ExMov", 0)
        self.dataPlotter2.RegisterDataSeriesToPanel("Most", 0)

        self.dataPlotter2.RegisterDataSeriesToPanel("LevelZero2", 2)
        self.dataPlotter2.RegisterDataSeriesToPanel("karZararFiyatList", 2)
        self.dataPlotter2.RegisterDataSeriesToPanel("getiriFiyatNetList", 3)

        self.dataPlotter2.SetLineProperties("LevelZero2", color='red', lineWidth=1)

        self.dataPlotter2.SetLineProperties("MA5", color='blue', lineWidth=2)
        self.dataPlotter2.SetLineProperties("MA200", color='orange', lineWidth=3)

        self.dataPlotter2.Show()
        print("=== plotData bitti ===")

    def plotDataLightningChart(self, trader):
        # Valid until 24/10/2025
        # lc.set_license(
        #     license_key="0002-n2gsgjA3DFwG6JDuQ314OhA/o8xDLgBsLLswNw5IH+KI+lp3YDFFMJ4eUHeEm5UnO5tsUMx0tVdr4TCZl05m+MajLKAe-MEQCIEW8i0YSNbGU2hHsWF4KL18tM1jC+58Xp5Z6uuJcthAxAiBArtShQ52lTtDXvK4MDmpeP36b91TWwdpGHosAjJZ5nw==",
        #     license_information={
        #         "appTitle": "LightningChart Python Trial",
        #         "company": "LightningChart Ltd.",
        #     }
        # )

        # Your license key
        # license_key = '0002-n2gsgjA3DFwG6JDuQ314OhA/o8xDLgBsLLswNw5IH+KI+lp3YDFFMJ4eUHeEm5UnO5tsUMx0tVdr4TCZl05m+MajLKAe-MEQCIEW8i0YSNbGU2hHsWF4KL18tM1jC+58Xp5Z6uuJcthAxAiBArtShQ52lTtDXvK4MDmpeP36b91TWwdpGHosAjJZ5nw=='

        # Valid until 24/10/2025
        license_key = 'T001-igghKW24Hy+bNW3D75Vsrt4Dehy+LQAJIcR5oRU3vzU9upv9A8CKcRN90iUTGV+NMh6rGFz0u6VblO4xQC+LJhUQW+I=-MEUCIQDN6JiBmSjXsJsnLeHSPI7xG/RXPCoRNlueCvJQrR1V8AIgb/If/lPsciYTm3x0ELZA3nqyv7unFgd1wyxsPNpH1PA='

        # Initialize TAChart turquoiseHexagon
        lightningChartTrader = TAChart(
            license_key,
            html_text_rendering=False,
            load_from_storage=False,
            theme='darkGold',
            axis_on_right=True
        )

        # Configure the chart
        lightningChartTrader.set_price_chart_type('CandleStick')  # Set the chart type
        lightningChartTrader.set_chart_title('Trading Chart with Sample Data')  # Set the chart title
        # lightningChartTrader.show_zoom_band_chart(True)  # Enable the zoom band chart
        lightningChartTrader.set_vertical_zooming(True)
        lightningChartTrader.set_rectangle_zooming_button(1)
        lightningChartTrader.set_panning_button(0)
        # set_wheel_zooming(zooming_mode)[source]

        # lightningChartTrader.show_file_selection(False)  # Hide the file selection button
        # lightningChartTrader.set_chart_title('myChart v1')  # Set the chart title
        # lightningChartTrader.set_percent_scale(True)  # Enable percentage scale
        # lightningChartTrader.set_ohlc_cursor_tracking('Close')  # Set OHLC cursor tracking type to 'Close'

        # Adding sample OHLC (Open, High, Low, Close) data programmatically
        # ohlc_data = [
        #     {'open': 1.1, 'high': 1.2, 'low': 1.0, 'close': 1.15, 'dateTime': 'Jan 1, 1970'},
        #     {'open': 1.1, 'high': 1.2, 'low': 1.0, 'close': 1.15, 'dateTime': 'Thu, 01 Jan 1970 00:00:00 GMT+0000', },
        #     {'open': 2, 'high': 2, 'low': 1.8, 'close': 1.95, 'dateTime': '04 Dec 1995'},
        #     {'open': 2.1, 'high': 2.1, 'low': 1.9, 'close': 2.05, 'dateTime': '04 December 1995', },
        #     {'open': 1.3, 'high': 1.4, 'low': 1.2, 'close': 1.35, 'dateTime': '2019-01-01'},
        #     {'open': 1.4, 'high': 1.5, 'low': 1.3, 'close': 1.45, 'dateTime': '2019-01-01T00:00:00', },
        #     {'open': 1.8, 'high': 1.8, 'low': 1.6, 'close': 1.75, 'dateTime': '2019-01-01T00:00:00.000+00:00', },
        #     {'open': 1.5, 'high': 1.6, 'low': 1.4, 'close': 1.55, 'dateTime': 'March 15, 2020'},
        #     {'open': 1.2, 'high': 1.3, 'low': 1.1, 'close': 1.25, 'dateTime': '01/02/2022'},
        #     {'open': 1.6, 'high': 1.7, 'low': 1.5, 'close': 1.65, 'dateTime': '2022/12/31'},
        # ]

        # Create OHLC data from trader's data using a loop
        ohlc_data = []
        for i in range(len(trader.Close)):
            ohlc_data.append(
                {
                'open': trader.Open[i],
                'high': trader.High[i],
                'low': trader.Low[i],
                'close': trader.Close[i],
                'dateTime': str(trader.DateTime[i])
                }
            )

        print("DateTime    :", ohlc_data[-5:])

        # Clearing all data from the chart
        lightningChartTrader.clear_data()

        # Sending the data to the chart
        lightningChartTrader.set_data(ohlc_data)

        # Setting the chart type in code.
        lightningChartTrader.set_price_chart_type('CandleStick')

        # Open the chart
        lightningChartTrader.open()

        # ==============================================================================================================

        # Time array boşsa, basit index array oluştur
        if len(self.Time) == 0:
            print("=== WARNING: Time array boş! Index array oluşturuluyor ===")
            time_array = list(range(len(self.Close)))
        else:
            time_array = self.Time

        LevelZero1 = self.create_level_series(self.BarCount, 0)
        LevelZero2 = self.create_level_series(self.BarCount, 0)

        balance = trader.Lists.BakiyeFiyatList
        bakiye = trader.Lists.BakiyeFiyatList

        getiriFiyatList = trader.Lists.GetiriFiyatList
        getiriFiyatNetList = trader.Lists.GetiriFiyatNetList

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

        # ==============================================================================================================

        # _TradingSignals

        # Add custom overlay
        overlay = lightningChartTrader.add_custom_overlay()
        overlay.set_line_color('#30EE50')
        overlay.set_name('Most')
        overlay.set_offset(13-1)

        # Set data to overlay
        overlay.set_data(self.Most.tolist())

        # Add custom overlay
        overlay1 = lightningChartTrader.add_custom_overlay()
        overlay1.set_line_color('#50EE50')
        overlay1.set_name('ExMov')
        overlay1.set_offset(14)

        # Set data to overlay
        overlay1.set_data(self.ExMov.tolist())


        # Add custom study
        study = lightningChartTrader.add_custom_study()
        study.set_line_color('#EE3050')
        study.set_name('combined_data_normalized')
        study.set_offset(13)

        # Set data to study
        study.set_data(trader.combined_data_normalized)

        # # Add custom study
        # study1 = study.add_custom_study()
        # study1.set_line_color('#EE3050')
        # study1.set_name('LevelZero1')
        # study1.set_offset(13)
        #
        # # Set data to study
        # study1.set_data(LevelZero1.tolist())

        # Add custom study
        study = lightningChartTrader.add_custom_study()
        study.set_line_color('#EE3050')
        study.set_name('karZararFiyatList')
        study.set_offset(13)

        # Set data to study
        study.set_data(karZararFiyatList)

        # Add custom study
        study = lightningChartTrader.add_custom_study()
        study.set_line_color('#EE3050')
        study.set_name('getiriFiyatNetList')
        study.set_offset(13)

        # Set data to study
        study.set_data(getiriFiyatNetList)

        #
        # LevelZero1
        # # Al/sat sinyallerini ekle
        # trader.combined_data, trader.segments
        #
        # self.Most
        # self.ExMov
        #
        # LevelZero2


        # ==============================================================================================================





        self.dataPlotter2.RegisterDataSeriesToPanel("_TradingSignals", 1)
        self.dataPlotter2.RegisterDataSeriesToPanel("LevelZero1", 1)
        self.dataPlotter2.SetLineProperties("_TradingSignals", color='cyan', lineWidth=1)
        self.dataPlotter2.SetLineProperties("LevelZero1", color='red', lineWidth=1)
        # self.dataPlotter2.ShowTradingSignals(trader.combined_data, trader.segments)  # Al/sat sinyallerini ekle

        self.dataPlotter2.RegisterDataSeriesToPanel("ExMov", 0)
        self.dataPlotter2.RegisterDataSeriesToPanel("Most", 0)

        self.dataPlotter2.RegisterDataSeriesToPanel("LevelZero2", 2)
        self.dataPlotter2.RegisterDataSeriesToPanel("karZararFiyatList", 2)
        self.dataPlotter2.RegisterDataSeriesToPanel("getiriFiyatNetList", 3)

    def plotDataPlotly(self, trader):
        # DataPlotter3 kullanarak plotly ile grafik çizimi
        from src.DataPlotter3 import DataPlotter3
        
        # DataPlotter3 instance oluştur
        dataPlotter3 = DataPlotter3()
        
        # plotDataFinal'daki kodu kopyala ve adapt et
        dataPlotter3.Clear()
        dataPlotter3.SetData(trader)
        
        symbol = "BTCUSD"
        timeframe = "1min"
        dataPlotter3.SetTitle(f"{symbol} {timeframe}")
        
        # plotDataFinal'daki verileri plotDataPlotly'ye aktar
        # Performance: 200K veri için 10K'ya düşür (20x hızlanma)
        max_points = 10000 if len(self.Close) > 10000 else len(self.Close)
        print(f"Using max_points: {max_points} for {len(self.Close)} data points")
        dataPlotter3.plotDataPlotly(trader, max_points=max_points)
        dataPlotter3.Show()

    def create_signal_segments(self, trader):
        """
        Create signal segments from trader's YönList and SeviyeList
        Returns combined_data, segments, and combined_data_normalized
        """
        try:
            # Dinamik yatay çizgiler için seviye listesi oluştur
            # Önce trader'dan güncel verileri al
            self.YonList = trader.Lists.YonList
            self.SeviyeList = trader.Lists.SeviyeList

            import numpy as np
            segments = self.get_signal_segments()

            # Tüm segmentleri tek bir combined data olarak birleştir
            combined_data = [np.nan] * len(self.Close)
            
            # Combined data normalized - 0 çizgisine oturtulmuş sinyal değerleri
            combined_data_normalized = [0] * len(self.Close)
            
            for seg in segments:
                # Combined data için level değerleri
                for j in range(seg["start"], seg["end"] + 1):
                    if j < len(combined_data):
                        combined_data[j] = seg["level"]
                
                # Combined data normalized için sinyal tipine göre değer
                signal_value = 0  # Default for unknown signals
                direction = seg.get("direction", "")
                
                if direction == "BUY" or direction == "A":
                    signal_value = 1  # Buy signal = 1
                elif direction == "SELL" or direction == "S":
                    signal_value = -1  # Sell signal = -1
                elif direction == "FLAT" or direction == "F":
                    signal_value = 0  # Flat signal = 0
                
                # Fill normalized data for this segment
                for j in range(seg["start"], seg["end"] + 1):
                    if j < len(combined_data_normalized):
                        combined_data_normalized[j] = signal_value
                
                # print(f"DEBUG: Added {seg['direction']} segment {seg['start']}→{seg['end']} at level {seg['level']:.2f}, normalized: {signal_value}")

            return segments, combined_data, combined_data_normalized
            
        except Exception as e:
            print(f"ERROR in create_signal_segments: {e}")
            import traceback
            traceback.print_exc()
            return [], [], []

    def plot_combined_signals(self, combined_data, bar_count=-1):
        """
        Plot combined signal data using matplotlib
        Args:
            combined_data: Signal data array
            bar_count: Number of bars to plot (-1 for all bars, positive number for last N bars)
        """
        try:
            # Plot combined_data using matplotlib
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Determine data range based on bar_count
            if bar_count > 0 and bar_count < len(combined_data):
                # Plot last N bars
                start_idx = len(combined_data) - bar_count
                end_idx = len(combined_data)
                plot_range = range(start_idx, end_idx)
                combined_data_slice = combined_data[start_idx:end_idx]
                title_suffix = f" (Last {bar_count} bars)"
            else:
                # Plot all bars
                start_idx = 0
                end_idx = len(combined_data)
                plot_range = range(len(combined_data))
                combined_data_slice = combined_data
                title_suffix = " (All data)"
            
            # Create figure and axis
            plt.figure(figsize=(12, 8))
            
            # Plot main price data (assuming Close prices exist)
            if hasattr(self, 'Close') and len(self.Close) > 0:
                if bar_count > 0 and bar_count < len(self.Close):
                    close_slice = self.Close[start_idx:end_idx]
                    plt.plot(plot_range, close_slice, 
                            label='Price', color='blue', linewidth=1)
                else:
                    plt.plot(range(len(self.Close)), self.Close, 
                            label='Price', color='blue', linewidth=1)
            
            # Plot combined signal data
            valid_indices = []
            valid_values = []
            
            for i, value in enumerate(combined_data_slice):
                actual_index = start_idx + i
                if not (np.isnan(value) if isinstance(value, (int, float)) else value is None):
                    valid_indices.append(actual_index)
                    valid_values.append(value)
            
            if valid_indices:
                plt.plot(valid_indices, valid_values, 
                        label='Trading Signals', color='red', 
                        linewidth=2, marker='o', markersize=3)
            
            # Set labels and title
            plt.xlabel('Bar Index')
            plt.ylabel('Price')
            plt.title(f'Price Chart with Trading Signals{title_suffix}')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Show plot
            plt.tight_layout()
            plt.show()
            
            print(f"DEBUG: Plotted {len(valid_indices)} signal points{title_suffix}")
            
        except Exception as e:
            print(f"ERROR: Failed to plot combined_data: {e}")
            import traceback
            traceback.print_exc()
    
    def SavePlotData(self, active_trader, dstDir="."):
        """CSV dosyalarına plot verileri kaydeden method"""
        # OHLC verilerini CSV dosyasına kaydet
        dstFileName = "_ohlc.csv"
        dstFilePath = dstDir + "/" + dstFileName
        
        # Header bilgilerini hazırla
        header_lines = [
            f"# Kayit_Zamani     : {time.strftime('%Y.%m.%d %H:%M:%S')}",
            f"# GrafikSembol     : .........",
            f"# GrafikPeriyot    : ........",
            f"# BarCount         : {self.dataManager.get_bar_count()}",
            f"# Baslangic_Tarihi : {pd.to_datetime(self.dataManager.get_timestamp_array()[0], unit='s').strftime('%Y.%m.%d %H:%M:%S')}" if self.dataManager.get_bar_count() > 0 else "# Baslangic_Tarihi: ",
            f"# Bitis_Tarihi     : {pd.to_datetime(self.dataManager.get_timestamp_array()[-1], unit='s').strftime('%Y.%m.%d %H:%M:%S')}" if self.dataManager.get_bar_count() > 0 else "# Bitis_Tarihi: ",
            f"# Format           : Id Date Time Open High Low Close Volume Lot",
            "# Data"
        ]
        
        # CSV dosyasını yaz
        with open(dstFilePath, 'w', newline='', encoding='utf-8') as f:
            # Header'ı yaz
            for line in header_lines:
                f.write(line + '\n')
            
            # Data satırlarını yaz
            timestamps = self.dataManager.get_timestamp_array()
            opens = self.dataManager.get_open_array()
            highs = self.dataManager.get_high_array()
            lows = self.dataManager.get_low_array()
            closes = self.dataManager.get_close_array()
            volumes = self.dataManager.get_volume_array()
            lots = self.dataManager.get_lot_array()
            
            total_bars = self.dataManager.get_bar_count()
            progress_step = max(1, total_bars // 10)  # Her %10'da progress göster
            
            for i in range(total_bars):
                # Progress göster
                if i % progress_step == 0 or i == total_bars - 1:
                    progress_percent = (i + 1) * 100 // total_bars
                    print(f"Writing OHLC data... {progress_percent}% ({i+1}/{total_bars})")
                
                # Timestamp'i date ve time'a çevir
                dt = pd.to_datetime(timestamps[i], unit='s')
                date_str = dt.strftime('%Y.%m.%d')
                time_str = dt.strftime('%H:%M:%S')
                
                # Satırı formatla
                line = f"{i};{date_str};{time_str};{opens[i]:.2f};{highs[i]:.2f};{lows[i]:.2f};{closes[i]:.2f};{int(volumes[i])};{int(lots[i])}"
                f.write(line + '\n')
        
        print(f"OHLC data saved to: {dstFilePath}")
        
        # Trading sinyallerini CSV dosyasına kaydet (Buy:1, Sell:-1, Flat:0)
        dstFileName2 = "_signals.csv"
        dstFilePath2 = dstDir + "/" + dstFileName2
        
        # Header bilgilerini hazırla
        header_lines2 = [
            f"# Kayit_Zamani     : {time.strftime('%Y.%m.%d %H:%M:%S')}",
            f"# GrafikSembol     : .........",
            f"# GrafikPeriyot    : ........",
            f"# BarCount         : {len(active_trader.combined_data_normalized)}",
            f"# Baslangic_Tarihi : {pd.to_datetime(self.dataManager.get_timestamp_array()[0], unit='s').strftime('%Y.%m.%d %H:%M:%S')}" if self.dataManager.get_bar_count() > 0 else "# Baslangic_Tarihi: ",
            f"# Bitis_Tarihi     : {pd.to_datetime(self.dataManager.get_timestamp_array()[-1], unit='s').strftime('%Y.%m.%d %H:%M:%S')}" if self.dataManager.get_bar_count() > 0 else "# Bitis_Tarihi: ",
            f"# Format           : Id Date Time Signal ( Buy:1, Sell:-1, Flat:0 )",
            "# Data"
        ]
        
        # CSV dosyasını yaz
        with open(dstFilePath2, 'w', newline='', encoding='utf-8') as f:
            # Header'ı yaz
            for line in header_lines2:
                f.write(line + '\n')
            
            # Data satırlarını yaz
            timestamps = self.dataManager.get_timestamp_array()
            total_bars = len(active_trader.combined_data_normalized)
            progress_step = max(1, total_bars // 10)  # Her %10'da progress göster
            
            for i in range(total_bars):
                # Progress göster
                if i % progress_step == 0 or i == total_bars - 1:
                    progress_percent = (i + 1) * 100 // total_bars
                    print(f"Writing trading signals... {progress_percent}% ({i+1}/{total_bars})")
                
                # Timestamp'i date ve time'a çevir
                if i < len(timestamps):
                    dt = pd.to_datetime(timestamps[i], unit='s')
                    date_str = dt.strftime('%Y.%m.%d')
                    time_str = dt.strftime('%H:%M:%S')
                else:
                    date_str = ""
                    time_str = ""
                
                # List elemanını as-is kullan
                value = active_trader.combined_data_normalized[i]
                
                # Satırı formatla
                line = f"{i};{date_str};{time_str};{value:.6f}" if isinstance(value, (int, float)) else f"{i};{date_str};{time_str};{value}"
                f.write(line + '\n')
        
        print(f"Trading signals saved to: {dstFilePath2}")
        
        # PnL verilerini CSV dosyasına kaydet
        dstFileName3 = "_pnl.csv"
        dstFilePath3 = dstDir + "/" + dstFileName3
        
        # Header bilgilerini hazırla
        header_lines3 = [
            f"# Kayit_Zamani     : {time.strftime('%Y.%m.%d %H:%M:%S')}",
            f"# GrafikSembol     : .........",
            f"# GrafikPeriyot    : ........",
            f"# BarCount         : {len(active_trader.Lists.KarZararPuanList)}",
            f"# Baslangic_Tarihi : {pd.to_datetime(self.dataManager.get_timestamp_array()[0], unit='s').strftime('%Y.%m.%d %H:%M:%S')}" if self.dataManager.get_bar_count() > 0 else "# Baslangic_Tarihi: ",
            f"# Bitis_Tarihi     : {pd.to_datetime(self.dataManager.get_timestamp_array()[-1], unit='s').strftime('%Y.%m.%d %H:%M:%S')}" if self.dataManager.get_bar_count() > 0 else "# Bitis_Tarihi: ",
            f"# Format           : Id Date Time KarZararPuanList KarZararFiyatList GetiriFiyatList GetiriFiyatNetList BakiyeFiyatList",
            "# Data"
        ]
        
        # CSV dosyasını yaz
        with open(dstFilePath3, 'w', newline='', encoding='utf-8') as f:
            # Header'ı yaz
            for line in header_lines3:
                f.write(line + '\n')
            
            # Data satırlarını yaz
            timestamps = self.dataManager.get_timestamp_array()
            total_bars = len(active_trader.Lists.KarZararPuanList)
            progress_step = max(1, total_bars // 10)  # Her %10'da progress göster
            
            for i in range(total_bars):
                # Progress göster
                if i % progress_step == 0 or i == total_bars - 1:
                    progress_percent = (i + 1) * 100 // total_bars
                    print(f"Writing PnL data... {progress_percent}% ({i+1}/{total_bars})")
                
                # Timestamp'i date ve time'a çevir
                if i < len(timestamps):
                    dt = pd.to_datetime(timestamps[i], unit='s')
                    date_str = dt.strftime('%Y.%m.%d')
                    time_str = dt.strftime('%H:%M:%S')
                else:
                    date_str = ""
                    time_str = ""
                
                # List elemanlarını al
                kar_zarar_puan = active_trader.Lists.KarZararPuanList[i]
                kar_zarar_fiyat = active_trader.Lists.KarZararFiyatList[i]
                getiri_fiyat = active_trader.Lists.GetiriFiyatList[i]
                getiri_fiyat_net = active_trader.Lists.GetiriFiyatNetList[i]
                bakiye_fiyat = active_trader.Lists.BakiyeFiyatList[i]
                
                # Satırı formatla
                line = f"{i};{date_str};{time_str};{kar_zarar_puan:.6f};{kar_zarar_fiyat:.6f};{getiri_fiyat:.6f};{getiri_fiyat_net:.6f};{bakiye_fiyat:.6f}"
                f.write(line + '\n')
        
        print(f"PnL data saved to: {dstFilePath3}")
        
        # İndikatör verilerini CSV dosyasına kaydet
        dstFileName4 = "_most.csv"
        dstFilePath4 = dstDir + "/" + dstFileName4
        
        # Total data length
        total_data_length = self.dataManager.get_bar_count()
        
        # İndikatör listelerini al ve gerekirse başına 0 ekle
        most_values = list(self.Most) if hasattr(self, 'Most') and self.Most is not None else []
        exmov_values = list(self.ExMov) if hasattr(self, 'ExMov') and self.ExMov is not None else []
        
        # Listelerin uzunluklarını total_data_length'e eşitle
        if len(most_values) < total_data_length:
            padding_count = total_data_length - len(most_values)
            most_values = [0.0] * padding_count + most_values
        
        if len(exmov_values) < total_data_length:
            padding_count = total_data_length - len(exmov_values)
            exmov_values = [0.0] * padding_count + exmov_values
        
        # Header bilgilerini hazırla
        header_lines4 = [
            f"# Kayit_Zamani     : {time.strftime('%Y.%m.%d %H:%M:%S')}",
            f"# GrafikSembol     : .........",
            f"# GrafikPeriyot    : ........",
            f"# BarCount         : {total_data_length}",
            f"# Baslangic_Tarihi : {pd.to_datetime(self.dataManager.get_timestamp_array()[0], unit='s').strftime('%Y.%m.%d %H:%M:%S')}" if self.dataManager.get_bar_count() > 0 else "# Baslangic_Tarihi: ",
            f"# Bitis_Tarihi     : {pd.to_datetime(self.dataManager.get_timestamp_array()[-1], unit='s').strftime('%Y.%m.%d %H:%M:%S')}" if self.dataManager.get_bar_count() > 0 else "# Bitis_Tarihi: ",
            f"# Format           : Id Date Time Most ExMov",
            "# Data"
        ]
        
        # CSV dosyasını yaz
        with open(dstFilePath4, 'w', newline='', encoding='utf-8') as f:
            # Header'ı yaz
            for line in header_lines4:
                f.write(line + '\n')
            
            # Data satırlarını yaz
            timestamps = self.dataManager.get_timestamp_array()
            progress_step = max(1, total_data_length // 10)  # Her %10'da progress göster
            
            for i in range(total_data_length):
                # Progress göster
                if i % progress_step == 0 or i == total_data_length - 1:
                    progress_percent = (i + 1) * 100 // total_data_length
                    print(f"Writing indicator data... {progress_percent}% ({i+1}/{total_data_length})")
                
                # Timestamp'i date ve time'a çevir
                if i < len(timestamps):
                    dt = pd.to_datetime(timestamps[i], unit='s')
                    date_str = dt.strftime('%Y.%m.%d')
                    time_str = dt.strftime('%H:%M:%S')
                else:
                    date_str = ""
                    time_str = ""
                
                # İndikatör değerlerini al
                most_value = most_values[i] if i < len(most_values) else 0.0
                exmov_value = exmov_values[i] if i < len(exmov_values) else 0.0
                
                # Satırı formatla
                line = f"{i};{date_str};{time_str};{most_value:.6f};{exmov_value:.6f}"
                f.write(line + '\n')
        
        print(f"Indicator data saved to: {dstFilePath4}")

    def createPanelsByHandCoded(self,  trader : 'CTrader', reader: 'CSVBarDataReader', plotter: 'DataPlotterImgBundle'):

        # self.dataPlotter2.AddYData(2, balance, "balance")
        # self.dataPlotter2.AddYData(3, bakiye, "bakiye")
        # self.dataPlotter2.AddYData(4, getiriFiyatList, "getiriFiyatList")
        # self.dataPlotter2.AddYData(5, getiriFiyatNetList, "getiriFiyatNetList")
        # self.dataPlotter2.AddYData(6, getiriKz, "getiriKz")
        # self.dataPlotter2.AddYData(7, getiriKzNet, "getiriKzNet")
        # self.dataPlotter2.AddYData(8, karZararPuanList, "karZararPuanList")
        # self.dataPlotter2.AddYData(9, karZararFiyatList, "karZararFiyatList")


        plotter.setWindowTitle(f"{reader.get_metadata('GrafikSembol')} - Multi Panel Chart")

        plotter.setTimeData(reader.time_data)
        plotter.setOHLCData(reader.ohlc)
        plotter.setVolumeData(reader.volume_data)
        plotter.setLotData(reader.lot_data)
        plotter.setDeltaData(reader.delta)
        plotter.setDeltaPctData(reader.delta_pct)
        dt_labels = [f"{bar.date} {bar.time}" for bar in reader.bars]
        plotter.setDateTimeLabels(dt_labels)
        plotter.setTradeSignals(tradeSignals)

        plotter.grafik_sembol = reader.get_metadata('GrafikSembol')
        plotter.grafik_periyot = reader.get_metadata('GrafikPeriyot')
        plotter.grafik_periyot_extension = reader.get_metadata('dk')

        # Panel 0: OHLC + Moving Averages
        panel0 = plotter.AddPanel(0)
        panel0.setTitle("Price Chart")
        panel0.setYAxisLabel("Price")
        panel0.setHeightRatio(2.0)  # Ana panel daha büyük
        panel0.setOHLCData(plotter.getOHLCData())
        # Info panel positioning for Panel 0 (adjust as desired)
        panel0.setInfoPanelPosition(100, 2)
        panel0.setInfoPanelOffsets(label_dx=5, value_dx=80)

        # Moving averages ekle
        panel0.setData(0, DataType.Line, sma_5, "SMA(5)", (1.0, 0.5, 0.0, 1.0))  # Turuncu
        panel0.setData(1, DataType.Line, sma_20, "SMA(20)", (0.0, 0.5, 1.0, 1.0))  # Mavi
        panel0.setData(2, DataType.Line, ema_20, "EMA(20)", (1.0, 0.0, 1.0, 1.0))  # Mor

        # MOST ekle
        panel0.setData(3, DataType.Line, most, "MOST", (0.6, 0.6, 0.0, 1.0))
        panel0.setData(4, DataType.Line, exmov, "EMA", (0.5, 0.2, 0.8, 1.0))

        # Panel 1: TradeSignals
        panel1 = plotter.AddPanel(1)
        panel1.setTitle("TradeSignals")
        panel1.setYAxisLabel("TradeSignals")
        panel1.setHeightRatio(1.0)
        # Info panel positioning for Panel 1
        panel1.setInfoPanelPosition(100, 2)
        panel1.setInfoPanelOffsets(label_dx=5, value_dx=80)

        panel1.setData(0, DataType.Stairs, tradeSignals, "TradeSignals", (0.2, 0.8, 1.0, 1.0))
        # ------------------------------------------
        # Gizli Y-axis padding çizgileri (autoscale hack)
        # ------------------------------------------
        padding_min = np.full(len(tradeSignals), -2.0, dtype=np.float64)  # alt sınır
        padding_max = np.full(len(tradeSignals), +2.0, dtype=np.float64)  # üst sınır
        # görünmez çizgiler (alpha=0)
        panel1.setData(
            998,
            DataType.Line,
            padding_min,
            "##pad_min",
            (1, 1, 1, 0)
        )

        panel1.setData(
            999,
            DataType.Line,
            padding_max,
            "##pad_max",
            (1, 1, 1, 0)
        )

        # Panel 2: Bollinger Bands
        panel2 = plotter.AddPanel(2)
        panel2.setTitle("BB(20,2)")
        panel2.setYAxisLabel("Bollinger")
        panel2.setHeightRatio(1.0)
        # Info panel positioning for Panel 2
        panel2.setInfoPanelPosition(100, 2)
        panel2.setInfoPanelOffsets(label_dx=5, value_dx=80)
        panel2.setData(0, DataType.Line, bb_upper, "BollingerUpper", (0.0, 1.0, 1.0, 1.0))  # Cyan
        panel2.setData(1, DataType.Line, bb_middle, "BollingerMiddile", (1.0, 0.5, 0.0, 1.0))  # Turuncu
        panel2.setData(2, DataType.Line, bb_lower, "BollingerLower", (1.0, 0.0, 1.0, 1.0))  # Mor

        # Panel 3: SuperTrend
        panel3 = plotter.AddPanel(3)
        panel3.setTitle("SuperTrend (10,3.0)")
        panel3.setYAxisLabel("SuperTrend")
        panel3.setHeightRatio(1.0)
        # Info panel positioning for Panel 3
        panel3.setInfoPanelPosition(100, 2)
        panel3.setInfoPanelOffsets(label_dx=5, value_dx=80)
        panel3.setData(0, DataType.Line, supertrend, "SuperTrend", (0.2, 0.8, 1.0, 1.0))

        # Panel 4: MOST
        panel4 = plotter.AddPanel(4)
        panel4.setTitle("MOST (21,1.0)")
        panel4.setYAxisLabel("MOST")
        panel4.setHeightRatio(1.0)
        # Info panel positioning for Panel 3
        panel4.setInfoPanelPosition(100, 2)
        panel4.setInfoPanelOffsets(label_dx=5, value_dx=80)
        panel4.setData(0, DataType.Line, most, "MOST", (0.6, 0.6, 0.0, 1.0))
        panel4.setData(1, DataType.Line, exmov, "EMA", (0.5, 0.2, 0.8, 1.0))

        # Panel 5: Volume
        panel5 = plotter.AddPanel(5)
        panel5.setTitle("Volume")
        panel5.setYAxisLabel("Volume")
        panel5.setHeightRatio(1.0)
        # Info panel positioning for Panel 4
        panel5.setInfoPanelPosition(100, 2)
        panel5.setInfoPanelOffsets(label_dx=5, value_dx=80)
        panel5.setData(0, DataType.Volume, volumes, "Volume", (0.3, 0.7, 1.0, 0.6))
        sma_100 = indicator.sma(volumes, 100)
        panel5.setData(1, DataType.Line, sma_100, "SMA(100)", (1.0, 0.5, 0.0, 1.0))  # Turuncu

        # Panel 6: RSI
        panel6 = plotter.AddPanel(6)
        panel6.setTitle("RSI (14)")
        panel6.setYAxisLabel("RSI")
        panel6.setHeightRatio(1.0)
        # Info panel positioning for Panel 5
        panel6.setInfoPanelPosition(100, 2)
        panel6.setInfoPanelOffsets(label_dx=5, value_dx=80)
        panel6.setData(0, DataType.Line, rsi_14, "RSI(14)", (1.0, 1.0, 0.0, 1.0))  # Sarı
        panel6.setData(1, DataType.Levels, [30.0, 70.0], "Levels", (1.0, 0.0, 0.0, 0.5))  # Kırmızı çizgiler

        # Panel 7: MACD
        panel7 = plotter.AddPanel(7)
        panel7.setTitle("MACD (12,26,9)")
        panel7.setYAxisLabel("MACD")
        panel7.setHeightRatio(1.0)
        # Info panel positioning for Panel 6
        panel7.setInfoPanelPosition(140, 2)
        panel7.setInfoPanelOffsets(label_dx=5, value_dx=80)
        panel7.setData(0, DataType.Line, macd_line, "MACD", (0.0, 1.0, 1.0, 1.0))  # Cyan
        panel7.setData(1, DataType.Line, signal_line, "Signal", (1.0, 0.5, 0.0, 1.0))  # Turuncu
        panel7.setData(2, DataType.Histogram, histogram, "Histogram")

        # Panel 8: Momentum
        panel8 = plotter.AddPanel(8)
        panel8.setTitle("Momentum (10)")
        panel8.setYAxisLabel("Momentum")
        panel8.setHeightRatio(1.0)
        # Info panel positioning for Panel 7
        panel8.setInfoPanelPosition(100, 2)
        panel8.setInfoPanelOffsets(label_dx=5, value_dx=80)
        panel8.setData(0, DataType.Line, momentum_10, "Momentum(10)", (1.0, 0.5, 0.0, 1.0))

        # Panel 9: Stochastic
        panel9 = plotter.AddPanel(9)
        panel9.setTitle("Stochastic (14,3)")
        panel9.setYAxisLabel("%K / %D")
        panel9.setHeightRatio(1.0)
        # Info panel positioning for Panel 8
        panel9.setInfoPanelPosition(100, 2)
        panel9.setInfoPanelOffsets(label_dx=5, value_dx=80)
        panel9.setData(0, DataType.Line, stoch_k, "%K", (0.0, 0.8, 0.0, 1.0))
        panel9.setData(1, DataType.Line, stoch_d, "%D", (0.8, 0.0, 0.0, 1.0))

        # Panel 10: ADX ve DI+/DI-
        panel10 = plotter.AddPanel(10)
        panel10.setTitle("ADX (14) & DI")
        panel10.setYAxisLabel("ADX / DI")
        panel10.setHeightRatio(1.0)
        # Info panel positioning for Panel 9
        panel10.setInfoPanelPosition(100, 2)
        panel10.setInfoPanelOffsets(label_dx=5, value_dx=80)
        panel10.setData(0, DataType.Line, adx, "ADX", (1.0, 1.0, 0.0, 1.0))  # Sarı
        panel10.setData(1, DataType.Line, di_plus, "+DI", (0.0, 1.0, 0.0, 1.0))  # Yeşil
        panel10.setData(2, DataType.Line, di_minus, "-DI", (1.0, 0.0, 0.0, 1.0))  # Kırmızı

        groupId = 0  # Group 0: Panel 0,1,2
        plotter.RegisterYSyncGroup(groupId, panel0)
        plotter.RegisterYSyncGroup(groupId, panel2)
        plotter.RegisterYSyncGroup(groupId, panel3)
        plotter.RegisterYSyncGroup(groupId, panel4)

        try:
            plotter.setEnableVerticalScrollBar(True)
            plotter.setEnableSharedCrossHair(True)
            plotter.setEnableSharedXAxis(True)
            plotter.setShowInfoOnAllPanels(True)
            plotter.setShowTradeSignals(True)
        except Exception:
            pass

    def plotDataImgBundle(self, trader):

        # ==============================================================================
        plotter = self.dataPlotterImgBundle
        reader = self.dataManager.get_reader()

        # ==============================================================================
        plotter.setTimeData(reader.time_data)
        plotter.setOHLCData(reader.ohlc)
        plotter.setVolumeData(reader.volume_data)
        plotter.setLotData(reader.lot_data)
        plotter.setDeltaData(reader.delta)
        plotter.setDeltaPctData(reader.delta_pct)
        dt_labels = [f"{bar.date} {bar.time}" for bar in reader.bars]
        plotter.setDateTimeLabels(dt_labels)


        # ==============================================================================
        # self.dataPlotter2.SetTitle(f"{symbol} {timeframe}")
        #
        # self.dataPlotter2.AddYData(0, trader.combined_data_normalized, "_TradingSignals")
        # self.dataPlotter2.AddYData(1, LevelZero1, "LevelZero1")
        # self.dataPlotter2.AddYData(2, balance, "balance")
        # self.dataPlotter2.AddYData(3, bakiye, "bakiye")
        # self.dataPlotter2.AddYData(4, getiriFiyatList, "getiriFiyatList")
        # self.dataPlotter2.AddYData(5, getiriFiyatNetList, "getiriFiyatNetList")
        # self.dataPlotter2.AddYData(6, getiriKz, "getiriKz")
        # self.dataPlotter2.AddYData(7, getiriKzNet, "getiriKzNet")
        # self.dataPlotter2.AddYData(8, karZararPuanList, "karZararPuanList")
        # self.dataPlotter2.AddYData(9, karZararFiyatList, "karZararFiyatList")
        # self.dataPlotter2.AddYData(10, farkList, "farkList")
        # self.dataPlotter2.AddYData(11, farkList2, "farkList2")
        #
        # self.dataPlotter2.AddYData(12, self.Ma5, "Ma5")
        # self.dataPlotter2.AddYData(13, self.Ma8, "Ma8")
        # self.dataPlotter2.AddYData(14, self.Ma13, "Ma13")
        # self.dataPlotter2.AddYData(15, self.Ma21, "Ma21")
        # self.dataPlotter2.AddYData(16, self.Ma50, "Ma50")
        # self.dataPlotter2.AddYData(17, self.Ma100, "Ma100")
        # self.dataPlotter2.AddYData(18, self.Ma200, "Ma200")
        # self.dataPlotter2.AddYData(19, self.Most, "Most")
        # self.dataPlotter2.AddYData(20, self.ExMov, "ExMov")
        #
        # self.dataPlotter2.AddYData(21, LevelZero2, "LevelZero2")
        #
        # self.dataPlotter2.RegisterDataSeriesToPanel("_TradingSignals", 1)
        # self.dataPlotter2.RegisterDataSeriesToPanel("LevelZero1", 1)
        # self.dataPlotter2.SetLineProperties("_TradingSignals", color='cyan', lineWidth=1)
        # self.dataPlotter2.SetLineProperties("LevelZero1", color='red', lineWidth=1)
        # # self.dataPlotter2.ShowTradingSignals(trader.combined_data, trader.segments)  # Al/sat sinyallerini ekle
        #
        # self.dataPlotter2.RegisterDataSeriesToPanel("ExMov", 0)
        # self.dataPlotter2.RegisterDataSeriesToPanel("Most", 0)
        #
        # self.dataPlotter2.RegisterDataSeriesToPanel("LevelZero2", 2)
        # self.dataPlotter2.RegisterDataSeriesToPanel("karZararFiyatList", 2)
        # self.dataPlotter2.RegisterDataSeriesToPanel("getiriFiyatNetList", 3)
        #
        # self.dataPlotter2.SetLineProperties("LevelZero2", color='red', lineWidth=1)
        #
        # self.dataPlotter2.SetLineProperties("MA5", color='blue', lineWidth=2)
        # self.dataPlotter2.SetLineProperties("MA200", color='orange', lineWidth=3)
        # # ==============================================================================

        # ==============================================================================
        tradeSignals = self.active_trader.combined_data_normalized
        karZararFiyatList = self.active_trader.Lists.KarZararFiyatList #self.karZararFiyatList
        getiriFiyatList = self.active_trader.Lists.GetiriFiyatList #self.GetiriFiyatList
        getiriFiyatNetList = self.active_trader.Lists.GetiriFiyatNetList #self.getiriFiyatNetList
        most = self.Most
        exMov = self.ExMov

        # ==============================================================================
        tradeSignals = np.array(tradeSignals, dtype=np.float64)
        karZararFiyatList = np.array(karZararFiyatList, dtype=np.float64)
        getiriFiyatList = np.array(getiriFiyatList, dtype=np.float64)
        getiriFiyatNetList = np.array(getiriFiyatNetList, dtype=np.float64)
        most = np.array(most, dtype=np.float64)
        exMov = np.array(exMov, dtype=np.float64)
        
        # ==============================================================================
        plotter.setTradeSignals(tradeSignals)

        # ==============================================================================
        plotter.setWindowTitle(f"{reader.get_metadata('GrafikSembol')} - Multi Panel Chart")

        # ==============================================================================
        plotter.grafik_sembol = reader.get_metadata('GrafikSembol')
        plotter.grafik_periyot = reader.get_metadata('GrafikPeriyot')
        plotter.grafik_periyot_extension = reader.get_metadata('dk')

        # ==============================================================================
        HeightRatioList= [1.0, 0.7, 0.7, 0.7, 1.0]

        # ==============================================================================
        # Panel 0: OHLC + Moving Averages
        panel0 = plotter.AddPanel(0)
        panel0.setTitle("Price Chart")
        panel0.setYAxisLabel("Price")
        panel0.setHeightRatio(HeightRatioList[0])  # Ana panel daha büyük
        panel0.setOHLCData(plotter.getOHLCData())
        # Info panel positioning for Panel 0 (adjust as desired)
        panel0.setInfoPanelPosition(100, 2)
        panel0.setInfoPanelOffsets(label_dx=5, value_dx=80)

        # Moving averages ekle
        panel0.setData(0, DataType.Line, self.Ma5, "SMA(5)", (1.0, 0.5, 0.0, 1.0))  # Turuncu
        panel0.setData(1, DataType.Line, self.Ma21, "SMA(21)", (0.0, 0.5, 1.0, 1.0))  # Mavi
        panel0.setData(2, DataType.Line, self.Ma200, "SMA(200)", (1.0, 0.0, 1.0, 1.0))  # Mor

        # MOST ekle
        panel0.setData(3, DataType.Line, self.Most, "MOST", (0.6, 0.6, 0.0, 1.0))
        panel0.setData(4, DataType.Line, self.ExMov, "EMA", (0.5, 0.2, 0.8, 1.0))

        # ==============================================================================
        # Panel 1: TradeSignals
        panel1 = plotter.AddPanel(1)
        panel1.setTitle("TradeSignals")
        panel1.setYAxisLabel("TradeSignals")
        panel1.setHeightRatio(HeightRatioList[1])
        # Info panel positioning for Panel 1
        panel1.setInfoPanelPosition(120, 2)
        panel1.setInfoPanelOffsets(label_dx=5, value_dx=80)

        panel1.setData(0, DataType.Stairs, tradeSignals, "Signals", (0.2, 0.8, 1.0, 1.0))
        # ------------------------------------------
        # Gizli Y-axis padding çizgileri (autoscale hack)
        # ------------------------------------------
        padding_min = np.full(len(tradeSignals), -2.0, dtype=np.float64)  # alt sınır
        padding_max = np.full(len(tradeSignals), +2.0, dtype=np.float64)  # üst sınır
        # görünmez çizgiler (alpha=0)
        panel1.setData(
            998,
            DataType.Line,
            padding_min,
            "##pad_min",
            (1, 1, 1, 0)
        )

        panel1.setData(
            999,
            DataType.Line,
            padding_max,
            "##pad_max",
            (1, 1, 1, 0)
        )


        # ==============================================================================
        # Panel 2: karZararFiyatList
        panel2 = plotter.AddPanel(2)
        panel2.setTitle("PnL")
        panel2.setYAxisLabel("karZararFiyatList")
        panel2.setHeightRatio(HeightRatioList[2])
        # Info panel positioning for Panel 2
        panel2.setInfoPanelPosition(100, 2)
        panel2.setInfoPanelOffsets(label_dx=5, value_dx=80)
        panel2.setData(0, DataType.Line, karZararFiyatList, "PnL", (1.0, 1.0, 0.0, 1.0))  # Sarı

        # ==============================================================================
        # Panel 3: getiriFiyatNetList
        panel3 = plotter.AddPanel(3)
        panel3.setTitle("Balance")
        panel3.setYAxisLabel("getiriFiyat")
        panel3.setHeightRatio(HeightRatioList[3])
        # Info panel positioning for Panel 3
        panel3.setInfoPanelPosition(100, 2)
        panel3.setInfoPanelOffsets(label_dx=5, value_dx=80)
        panel3.setData(0, DataType.Line, getiriFiyatList, "Balance",  (0.0, 0.5, 1.0, 1.0))       # Mavi
        panel3.setData(1, DataType.Line, getiriFiyatNetList, "Net Balance", (1.0, 1.0, 0.0, 1.0))  # Sarı

        # Purple (0.5, 0.0, 0.5, 1.0)

        # ==============================================================================
        # Panel 4: MOST
        panel4 = plotter.AddPanel(4)
        panel4.setTitle("MOST (21,1.0)")
        panel4.setYAxisLabel("MOST")
        panel4.setHeightRatio(HeightRatioList[4])
        # Info panel positioning for Panel 3
        panel4.setInfoPanelPosition(100, 2)
        panel4.setInfoPanelOffsets(label_dx=5, value_dx=80)
        panel4.setData(0, DataType.Line, most, "MOST", (0.6, 0.6, 0.0, 1.0))
        panel4.setData(1, DataType.Line, exMov, "EMA", (0.5, 0.2, 0.8, 1.0))

        # ==============================================================================
        groupId = 0  # Group 0: Panel 0,1,2
        plotter.RegisterYSyncGroup(groupId, panel0)
        # plotter.RegisterYSyncGroup(groupId, panel2)
        # plotter.RegisterYSyncGroup(groupId, panel3)
        # plotter.RegisterYSyncGroup(groupId, panel4)

        try:
            plotter.setEnableVerticalScrollBar(True)
            plotter.setEnableSharedCrossHair(True)
            plotter.setEnableSharedXAxis(True)
            plotter.setShowInfoOnAllPanels(True)
            plotter.setShowTradeSignals(True)
            plotter.setEnableRangeSlider(True)
        except Exception:
            pass

        # ==============================================================================
        # Grafiği göster
        print(f"\nToplam {len(plotter.panels)} panel oluşturuldu:")
        for idx in sorted(plotter.panels.keys()):
            panel = plotter.panels[idx]
            print(f"  - Panel {idx}: {panel.title} ({len(panel.data_items)} data series)")
        print("\nMulti-panel grafik açılıyor...")

        # ==============================================================================
        immapp.run(plotter.Plot, with_implot=True, window_size=(1600, 1200))

        # self.createPanelsByHandCoded(trader, reader, plotter)

        return

        # ==============================================================================
        plotter.setTimeData(reader.time_data)
        plotter.setOHLCData(reader.ohlc)
        plotter.setVolumeData(reader.volume_data)
        plotter.setLotData(reader.lot_data)
        plotter.setDeltaData(reader.delta)
        plotter.setDeltaPctData(reader.delta_pct)
        dt_labels = [f"{bar.date} {bar.time}" for bar in reader.bars]
        plotter.setDateTimeLabels(dt_labels)
        plotter.setTradeSignals(tradeSignals)

        # ==============================================================================
        plotter.setWindowTitle(f"{reader.get_metadata('GrafikSembol')} - Multi Panel Chart")
        # ==============================================================================
        plotter.grafik_sembol = reader.get_metadata('GrafikSembol')
        plotter.grafik_periyot = reader.get_metadata('GrafikPeriyot')
        plotter.grafik_periyot_extension = reader.get_metadata('dk')
        # ==============================================================================
        self.createPanelsByHandCoded(plotter)

        # ==============================================================================
        # Grafiği göster
        print(f"\nToplam {len(plotter.panels)} panel oluşturuldu:")
        for idx in sorted(plotter.panels.keys()):
            panel = plotter.panels[idx]
            print(f"  - Panel {idx}: {panel.title} ({len(panel.data_items)} data series)")
        print("\nMulti-panel grafik açılıyor...")

        # ==============================================================================
        immapp.run(plotter.Plot, with_implot=True, window_size=(1600, 1200))

        pass

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
