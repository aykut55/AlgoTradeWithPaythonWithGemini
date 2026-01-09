# -*- coding: utf-8 -*-
"""
OptLogVisualizer Example Usage and Demo
"""

import sys
import io
# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from opt_log_analyzer import OptLogAnalyzer
from opt_log_visualizer import OptLogVisualizer, quick_plot
import os
import plotly.io as pio

# Set Plotly renderer to browser (avoids IDE port issues)
pio.renderers.default = "browser"


def demo_basic_scatter_plots():
    """Temel scatter plot örnekleri"""
    print("=" * 80)
    print("OptLogVisualizer - Temel Scatter Plot Örnekleri")
    print("=" * 80)

    # Dosya yolu
    data_path = os.path.join("..", "..", "data", "singleTraderOptLog.csv")

    # Veriyi yükle
    print("\n1. Veri Yükleme")
    print("-" * 80)
    analyzer = OptLogAnalyzer(data_path)

    # Visualizer oluştur
    viz = OptLogVisualizer(analyzer.df)

    # Output klasörü oluştur
    output_dir = os.path.join("..", "..", "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Output klasörü oluşturuldu: {output_dir}")

    # ÖRNEK 1: Net Profit Scatter Plot
    print("\n2. Net Profit Scatter Plot")
    print("-" * 80)
    print("CombNo'ya göre Net Profit dağılımı...")

    fig1 = viz.scatter_plot(
        x_col='CombNo',
        y_col='OR_NetProf',
        title='Net Profit Distribution',
        color_col='period',
        hover_cols=['OR_WinRate', 'OR_ProfFact', 'OR_TotTrade'],
        show=True
    )
    # Save to file
    html_path1 = os.path.join(output_dir, "1_net_profit_scatter.html")
    viz.save_figure(fig1, html_path1)

    # ÖRNEK 2: İşlem Sayısı Scatter Plot
    print("\n3. İşlem Sayısı Scatter Plot")
    print("-" * 80)
    print("CombNo'ya göre Toplam İşlem Sayısı...")

    fig2 = viz.scatter_plot(
        x_col='CombNo',
        y_col='OR_TotTrade',
        title='Total Trade Count Distribution',
        color_col='OR_WinRate',
        size_col='OR_NetProf',
        hover_cols=['period', 'percent', 'OR_ProfFact'],
        show=True
    )
    html_path2 = os.path.join(output_dir, "2_trade_count_scatter.html")
    viz.save_figure(fig2, html_path2)

    # ÖRNEK 3: Win Rate vs Net Profit
    print("\n4. Win Rate vs Net Profit")
    print("-" * 80)
    print("Win Rate ile Net Profit arasındaki ilişki...")

    fig3 = viz.scatter_plot(
        x_col='OR_WinRate',
        y_col='OR_NetProf',
        title='Win Rate vs Net Profit',
        color_col='OR_ProfFact',
        size_col='OR_TotTrade',
        hover_cols=['CombNo', 'period', 'percent'],
        show=True
    )
    html_path3 = os.path.join(output_dir, "3_winrate_vs_netprofit.html")
    viz.save_figure(fig3, html_path3)

    # ÖRNEK 4: Profit Factor vs Max Drawdown
    print("\n5. Profit Factor vs Max Drawdown")
    print("-" * 80)

    fig4 = viz.scatter_plot(
        x_col='OR_ProfFact',
        y_col='OR_MaxDD',
        title='Profit Factor vs Max Drawdown',
        color_col='OR_NetProf',
        hover_cols=['CombNo', 'OR_WinRate', 'OR_TotTrade'],
        show=True
    )
    html_path4 = os.path.join(output_dir, "4_profitfactor_vs_maxdd.html")
    viz.save_figure(fig4, html_path4)

    print("\n" + "=" * 80)
    print("Tüm grafikler kaydedildi:")
    print(f"  - {html_path1}")
    print(f"  - {html_path2}")
    print(f"  - {html_path3}")
    print(f"  - {html_path4}")
    print("Tarayıcınızda açılamadıysa, bu HTML dosyalarını manuel olarak açabilirsiniz.")
    print("=" * 80)

    return viz


def demo_multiple_plots():
    """Çoklu plot örnekleri"""
    print("\n" + "=" * 80)
    print("Çoklu Scatter Plot Örnekleri")
    print("=" * 80)

    data_path = os.path.join("..", "..", "data", "singleTraderOptLog.csv")
    analyzer = OptLogAnalyzer(data_path)
    viz = OptLogVisualizer(analyzer.df)

    # Filtreleme: Sadece karlı sistemler
    print("\nKarlı sistemleri filtreliyorum (OR_NetProf > 500000)...")
    profitable = analyzer.where("OR_NetProf > 500000")
    viz.load_dataframe(profitable)

    print(f"Filtrelendi: {len(profitable)} karlı sistem bulundu")

    # Çoklu metrik görselleştirme
    print("\n6. Çoklu Metrik Karşılaştırması")
    print("-" * 80)

    metrics_to_plot = [
        'OR_NetProf',
        'OR_WinRate',
        'OR_ProfFact',
        'OR_TotTrade',
        'OR_MaxDD',
        'OR_Sharpe'
    ]

    fig = viz.multiple_scatter_plots(
        x_col='CombNo',
        y_cols=metrics_to_plot,
        title='Multiple Performance Metrics (Profitable Systems)',
        color_col='period',
        show=True
    )

    return viz


def demo_dashboard():
    """Dashboard örneği"""
    print("\n" + "=" * 80)
    print("Dashboard Oluşturma")
    print("=" * 80)

    data_path = os.path.join("..", "..", "data", "singleTraderOptLog.csv")
    analyzer = OptLogAnalyzer(data_path)

    # En iyi sistemleri seç
    print("\nEn iyi sistemleri seçiyorum...")
    best = analyzer.where("OR_NetProf > 1000000 and OR_WinRate > 30 and OR_ProfFact > 1.1")
    print(f"Seçildi: {len(best)} en iyi sistem")

    viz = OptLogVisualizer(best)

    # Dashboard metrikleri
    metrics = {
        'Net Profit': 'OR_NetProf',
        'Win Rate (%)': 'OR_WinRate',
        'Total Trades': 'OR_TotTrade',
        'Profit Factor': 'OR_ProfFact',
        'Max Drawdown': 'OR_MaxDD',
        'Sharpe Ratio': 'OR_Sharpe'
    }

    print("\n7. Performance Dashboard")
    print("-" * 80)

    fig = viz.create_dashboard(
        metrics=metrics,
        x_col='CombNo',
        color_col='period',
        title='Top Systems Performance Dashboard',
        width=1600,
        height=1200,
        show=True
    )

    # Dashboard'u kaydet
    output_dir = os.path.join("..", "..", "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, "performance_dashboard.html")
    viz.save_figure(fig, output_path, format='html')
    print(f"\n[OK] Dashboard kaydedildi: {output_path}")

    return viz


def demo_advanced_analysis():
    """Gelişmiş analiz örnekleri"""
    print("\n" + "=" * 80)
    print("Gelişmiş Analiz Örnekleri")
    print("=" * 80)

    data_path = os.path.join("..", "..", "data", "singleTraderOptLog.csv")
    analyzer = OptLogAnalyzer(data_path)
    viz = OptLogVisualizer(analyzer.df)

    # 1. Korelasyon analizi
    print("\n8. Korelasyon Analizi")
    print("-" * 80)

    correlation_cols = [
        'OR_NetProf',
        'OR_WinRate',
        'OR_ProfFact',
        'OR_TotTrade',
        'OR_MaxDD',
        'OR_Sharpe'
    ]

    fig_corr = viz.correlation_heatmap(
        columns=correlation_cols,
        title='Performance Metrics Correlation',
        show=True
    )

    # 2. Dağılım analizi
    print("\n9. Net Profit Dağılımı")
    print("-" * 80)

    fig_dist = viz.distribution_plot(
        column='OR_NetProf',
        plot_type='histogram',
        bins=100,
        title='Net Profit Distribution',
        show=True
    )

    # 3. Box plot
    print("\n10. Win Rate Box Plot")
    print("-" * 80)

    fig_box = viz.distribution_plot(
        column='OR_WinRate',
        plot_type='box',
        title='Win Rate Distribution',
        show=True
    )

    return viz


def demo_filtered_analysis():
    """Filtrelenmiş veri analizi"""
    print("\n" + "=" * 80)
    print("Filtrelenmiş Veri Analizi")
    print("=" * 80)

    data_path = os.path.join("..", "..", "data", "singleTraderOptLog.csv")
    analyzer = OptLogAnalyzer(data_path)

    # Farklı period değerleri için analiz
    periods = [5, 10, 15, 20]

    output_dir = os.path.join("..", "..", "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for period in periods:
        print(f"\n11. Period={period} Analizi")
        print("-" * 80)

        # Filtreleme
        period_data = analyzer.filter(period=period)
        print(f"Period={period} için {len(period_data)} kayıt bulundu")

        if len(period_data) > 0:
            # Visualizer oluştur
            viz = OptLogVisualizer(period_data)

            # Scatter plot
            fig = viz.scatter_plot(
                x_col='percent',
                y_col='OR_NetProf',
                title=f'Net Profit vs Percent (Period={period})',
                color_col='OR_WinRate',
                size_col='OR_TotTrade',
                hover_cols=['CombNo', 'OR_ProfFact'],
                show=True
            )

            # Kaydet
            output_path = os.path.join(output_dir, f"period_{period}_analysis.html")
            viz.save_figure(fig, output_path)
            print(f"[OK] Kaydedildi: {output_path}")


def demo_comparison_analysis():
    """Karşılaştırmalı analiz"""
    print("\n" + "=" * 80)
    print("Karşılaştırmalı Analiz")
    print("=" * 80)

    data_path = os.path.join("..", "..", "data", "singleTraderOptLog.csv")
    analyzer = OptLogAnalyzer(data_path)
    viz = OptLogVisualizer(analyzer.df)

    # En iyi 50 sistem
    print("\n12. En İyi 50 Sistem Karşılaştırması")
    print("-" * 80)

    metrics = ['OR_NetProf', 'OR_WinRate', 'OR_ProfFact', 'OR_MaxDD']

    fig = viz.comparison_plot(
        metrics=metrics,
        title='Top 50 Systems - Performance Metrics',
        top_n=50,
        sort_by='OR_NetProf',
        show=True
    )

    # Kaydet
    output_dir = os.path.join("..", "..", "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, "top50_comparison.html")
    viz.save_figure(fig, output_path)


def demo_quick_plot():
    """Hızlı plot örneği"""
    print("\n" + "=" * 80)
    print("Hızlı Plot Kullanımı")
    print("=" * 80)

    data_path = os.path.join("..", "..", "data", "singleTraderOptLog.csv")
    analyzer = OptLogAnalyzer(data_path)

    print("\n13. Quick Plot - Net Profit")
    print("-" * 80)

    # Tek satırda plot
    fig = quick_plot(
        df=analyzer.df,
        x_col='CombNo',
        y_col='OR_NetProf',
        title='Quick Net Profit Plot',
        color_col='period'
    )


def main():
    """Ana demo fonksiyonu"""
    print("\n")
    print("=" * 80)
    print(" " * 20 + "OptLogVisualizer Demo")
    print("=" * 80)

    # User selection
    print("\nPlease select the demo you want to run:")
    print("1. Basic Scatter Plots")
    print("2. Multiple Plots")
    print("3. Dashboard")
    print("4. Advanced Analysis (Correlation, Distribution)")
    print("5. Filtered Analysis (Period-based)")
    print("6. Comparison Analysis")
    print("7. Quick Plot")
    print("8. ALL DEMOS (run sequentially)")
    print("0. Exit")

    try:
        choice = input("\nYour choice (0-8): ").strip()

        if choice == '1':
            demo_basic_scatter_plots()
        elif choice == '2':
            demo_multiple_plots()
        elif choice == '3':
            demo_dashboard()
        elif choice == '4':
            demo_advanced_analysis()
        elif choice == '5':
            demo_filtered_analysis()
        elif choice == '6':
            demo_comparison_analysis()
        elif choice == '7':
            demo_quick_plot()
        elif choice == '8':
            print("\nRunning all demos...\n")
            demo_basic_scatter_plots()
            demo_multiple_plots()
            demo_dashboard()
            demo_advanced_analysis()
            demo_filtered_analysis()
            demo_comparison_analysis()
            demo_quick_plot()
        elif choice == '0':
            print("\nExiting...")
            return
        else:
            print("\n[!] Invalid choice! Please enter a number between 0-8.")
            return

        print("\n" + "=" * 80)
        print("Demo completed!")
        print("You can close the graph window to continue.")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\nDemo cancelled.")
    except Exception as e:
        print(f"\n[ERROR] An error occurred during demo: {e}")


if __name__ == "__main__":
    # If run directly, show all demos
    import sys

    # If command line argument is provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "basic":
            demo_basic_scatter_plots()
        elif sys.argv[1] == "multiple":
            demo_multiple_plots()
        elif sys.argv[1] == "dashboard":
            demo_dashboard()
        elif sys.argv[1] == "advanced":
            demo_advanced_analysis()
        elif sys.argv[1] == "filtered":
            demo_filtered_analysis()
        elif sys.argv[1] == "comparison":
            demo_comparison_analysis()
        elif sys.argv[1] == "quick":
            demo_quick_plot()
        elif sys.argv[1] == "all":
            demo_basic_scatter_plots()
            demo_multiple_plots()
            demo_dashboard()
            demo_advanced_analysis()
            demo_filtered_analysis()
            demo_comparison_analysis()
            demo_quick_plot()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python opt_log_visualizer_demo.py [basic|multiple|dashboard|advanced|filtered|comparison|quick|all]")
    else:
        # No argument - interactive menu
        main()
