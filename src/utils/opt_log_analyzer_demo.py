"""
OptLogAnalyzer Örnek Kullanım ve Test Dosyası
"""
from imgui_bundle.notebook_patch_runners import notebook_do_patch_runners_if_needed

from opt_log_analyzer import OptLogAnalyzer
from my_custom_visualizer import MyCustomVisualizer
import os
import pandas as pd


def display_result(df, n_cols=10, n_rows=10, title="Sonuc"):
    """
    DataFrame sonucunu ekrana yazdırır (sınırlı sütun ve satır ile)

    Args:
        df: Gösterilecek DataFrame
        n_cols: Gösterilecek sütun sayısı (-1 = tümünü göster)
        n_rows: Gösterilecek satır sayısı (-1 = tümünü göster)
        title: Başlık metni
    """
    if len(df) == 0:
        print(f"{title}: Sonuc bulunamadi!")
        return

    # -1 ise tümünü göster
    actual_cols = len(df.columns) if n_cols == -1 else n_cols
    actual_rows = len(df) if n_rows == -1 else n_rows

    # Başlık
    col_text = "tum sutunlar" if n_cols == -1 else f"ilk {actual_cols} sutun"
    row_text = "tum satirlar" if n_rows == -1 else f"ilk {actual_rows} satir"
    print(f"\n{title} ({len(df)} kayit, {col_text}, {row_text}):")
    print("-" * 80)

    # Sütun ve satırları seç
    display_df = df.iloc[:actual_rows, :actual_cols]

    # Pandas display ayarları
    with pd.option_context('display.max_columns', None if n_cols == -1 else actual_cols,
                           'display.max_rows', None if n_rows == -1 else actual_rows,
                           'display.width', None,  # Genişlik sınırı kaldır
                           'display.max_colwidth', 15):
        # Manuel hizalama için string formatla
        print(display_df.to_string(index=False, justify='left'))

    # Uyarı mesajları (sadece sınırlı gösterimde)
    if n_rows != -1 and len(df) > actual_rows:
        print(f"\n... ve {len(df) - actual_rows} satir daha")
    if n_cols != -1 and len(df.columns) > actual_cols:
        print(f"... ve {len(df.columns) - actual_cols} sutun daha")


def usage_examples():
    print("=" * 80)
    print("OptLogAnalyzer - Örnek Kullanım")
    print("=" * 80)

    # Dosya yolu
    data_path = os.path.join("..", "..", "data", "singleTraderOptLog.csv")

    # Analyzer'ı başlat ve dosyayı yükle
    print("\n1. Dosya Yükleme")
    print("-" * 80)
    analyzer = OptLogAnalyzer(data_path)

    # Genel bilgi
    print("\n2. Genel Bilgiler")
    print("-" * 80)
    analyzer.info()

    # Sütun isimleri (ilk 20 sütun)
    print("\n3. Sütun İsimleri (ilk 20)")
    print("-" * 80)
    columns = analyzer.columns()
    for i, col in enumerate(columns[:20], 1):
        print(f"{i:2d}. {col}")
    print(f"... ve {len(columns) - 20} sütun daha")

    # İlk 5 satır
    print("\n4. İlk 5 Satır (bazı önemli sütunlar)")
    print("-" * 80)
    important_cols = ['CombNo', 'period', 'percent', 'OR_NetProf', 'OR_WinRate',
                      'OR_ProfFact', 'OR_MaxDD', 'OR_TotTrade']
    print(analyzer.select(important_cols).head())

    # İstatistiksel özet
    print("\n5. İstatistiksel Özet (Performans Metrikleri)")
    print("-" * 80)
    stats_cols = ['OR_NetProf', 'OR_WinRate', 'OR_ProfFact', 'OR_MaxDD']
    print(analyzer.describe(stats_cols))

    # Filtreleme örnekleri
    print("\n6. Filtreleme Örnekleri")
    print("-" * 80)

    # Örnek 1: WHERE ile filtreleme (Karlı sistemler)
    print("\n6.1. Karlı Sistemler (NetProf > 1000000)")
    profitable = analyzer.where("OR_NetProf > 1000000")
    print(f"Bulunan kayıt sayısı: {len(profitable)}")
    if len(profitable) > 0:
        print(profitable[important_cols].head())

    # Örnek 2: Basit filter ile (period=5)
    print("\n6.2. Period=5 olan sistemler")
    period5 = analyzer.filter(period=5)
    print(f"Bulunan kayıt sayısı: {len(period5)}")

    # Örnek 3: Karmaşık koşul
    print("\n6.3. İyi Performans Kriterleri (WinRate > 40 ve ProfitFactor > 1.5)")
    good_systems = analyzer.where("OR_WinRate > 40 and OR_ProfFact > 1.5")
    print(f"Bulunan kayıt sayısı: {len(good_systems)}")
    if len(good_systems) > 0:
        print(good_systems[important_cols].head())

    # Sıralama
    print("\n7. Sıralama Örnekleri")
    print("-" * 80)

    # En yüksek net kar
    print("\n7.1. En Yüksek Net Kar (Top 10)")
    top_profit = analyzer.top(10, 'OR_NetProf', ascending=False)
    print(top_profit[important_cols])

    # En yüksek win rate
    print("\n7.2. En Yüksek Win Rate (Top 5)")
    top_winrate = analyzer.top(5, 'OR_WinRate', ascending=False)
    print(top_winrate[['CombNo', 'period', 'percent', 'OR_WinRate', 'OR_NetProf', 'OR_TotTrade']])

    # Gruplama
    print("\n8. Gruplama Örnekleri")
    print("-" * 80)

    # Period'a göre ortalama performans
    print("\n8.1. Period'a Göre Ortalama Performans")
    grouped = analyzer.group_by('period')
    avg_by_period = grouped[['OR_NetProf', 'OR_WinRate', 'OR_ProfFact']].mean()
    print(avg_by_period)

    # Tek bir sütunun istatistikleri
    print("\n9. Detaylı İstatistikler")
    print("-" * 80)
    print("\n9.1. Net Profit İstatistikleri")
    netprof_stats = analyzer.get_statistics('OR_NetProf')
    for key, value in netprof_stats.items():
        print(f"{key:10s}: {value:,.2f}")

    # Search örneği
    print("\n10. Arama Örnekleri")
    print("-" * 80)
    print("\n10.1. Period değeri 5 olan kayıtlar (ilk 3)")
    search_result = analyzer.search('period', 5, exact=True)
    print(f"Bulunan kayıt sayısı: {len(search_result)}")
    print(search_result[important_cols].head(3))

    # SQL sorgusu (pandasql yüklüyse)
    print("\n11. SQL Sorgusu Örneği (pandasql gerekli)")
    print("-" * 80)
    try:
        sql_query = """
        SELECT period,
               COUNT(*) as count,
               AVG(OR_NetProf) as avg_profit,
               MAX(OR_WinRate) as max_winrate
        FROM df
        WHERE OR_NetProf > 0
        GROUP BY period
        ORDER BY avg_profit DESC
        """
        sql_result = analyzer.query_sql(sql_query)
        if not sql_result.empty:
            print(sql_result)
    except Exception as e:
        print(f"SQL sorgusu çalıştırılamadı: {e}")
        print("pandasql yüklemek için: pip install pandasql")

    # Zincirleme işlemler
    print("\n12. Zincirleme İşlemler")
    print("-" * 80)
    print("Performanslı sistemleri bul ve en iyileri göster")
    result = (analyzer.where("OR_NetProf > 500000 and OR_WinRate > 35")
              .pipe(lambda df: df.nlargest(5, 'OR_ProfFact')))
    print(result[['CombNo', 'period', 'percent', 'OR_NetProf', 'OR_WinRate', 'OR_ProfFact']])

    # Sütun Sıralama
    print("\n13. Sutun Siralama Ornekleri")
    print("-" * 80)
    analyzer.reset()  # Orijinal veri setine dön

    # 13.1 Index ile sıralama
    print("\n13.1. Index ile Sutun Siralama: [0, 1, 2, 40, 41, 39, 44]")
    print("(CombNo, period, percent, OR_NetProf, OR_WinRate, OR_ProfFact, OR_TotTrade)")
    analyzer.reorder_columns([0, 1, 2, 40, 41, 39, 44])
    print(analyzer.head(3))

    # 13.2 İsim ile en başa taşıma
    print("\n13.2. Onemli Sutunlari En Basa Tasima")
    analyzer.reset()
    analyzer.move_columns_to_front(['CombNo', 'period', 'percent', 'OR_NetProf', 'OR_WinRate', 'OR_ProfFact'])
    print("Yeni ilk 10 sutun:", analyzer.columns()[:10])
    print(analyzer.head(3)[analyzer.columns()[:8]])

    # 13.3 Sadece belirli sütunları seç
    print("\n13.3. Sadece Belirli Sutunlari Goster")
    analyzer.reset()
    filtered_df = analyzer.select_and_reorder(['CombNo', 'period', 'OR_NetProf', 'OR_WinRate', 'OR_ProfFact', 'OR_TotTrade'])
    print(filtered_df.head(5))

    # Dosya Kaydetme
    print("\n14. Dosya Kaydetme Ornekleri")
    print("-" * 80)

    # Çıktı klasörü oluştur
    output_dir = os.path.join("..", "..", "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Cikti klasoru olusturuldu: {output_dir}")

    # 14.1 CSV olarak kaydet
    print("\n14.1. CSV Formatinda Kaydetme")
    csv_path = os.path.join(output_dir, "filtered_results.csv")
    analyzer.save_csv(csv_path)

    # 14.2 Tabular TXT olarak kaydet (farklı genişliklerle)
    print("\n14.2. Tabular TXT Formatinda Kaydetme (Farkli Genislikler)")

    # 14.2a - Dar sütunlar
    txt_path_narrow = os.path.join(output_dir, "filtered_results_narrow.txt")
    analyzer.save_as_table(txt_path_narrow, col_width=15, col_space=2)

    # 14.2b - Normal sütunlar
    txt_path_normal = os.path.join(output_dir, "filtered_results_normal.txt")
    analyzer.save_as_table(txt_path_normal, col_width=25, col_space=3)

    # 14.2c - Geniş sütunlar
    txt_path_wide = os.path.join(output_dir, "filtered_results_wide.txt")
    analyzer.save_as_table(txt_path_wide, col_width=35, col_space=5)

    # 14.3 Her ikisini de kaydet
    print("\n14.3. Hem CSV Hem TXT Olarak Kaydetme")
    base_path = os.path.join(output_dir, "best_systems")

    # En iyi sistemleri seç ve kaydet
    analyzer.reset()
    best = analyzer.where("OR_NetProf > 1000000 and OR_ProfFact > 1.2")
    analyzer.df = best  # Filtrelenmiş veriyi ana df'e ata
    analyzer.move_columns_to_front(['CombNo', 'period', 'percent', 'OR_NetProf', 'OR_WinRate', 'OR_ProfFact'])
    analyzer.save_both(base_path, col_width=30, col_space=4)  # Geniş ve okunabilir
    print(f"En iyi {len(best)} sistem kaydedildi (col_width=30, col_space=4)")

    # 14.4 Farklı ayırıcı ile CSV
    print("\n14.4. Farkli Ayirici ile CSV Kaydetme (virgul)")
    comma_csv_path = os.path.join(output_dir, "results_comma_separated.csv")
    analyzer.save_csv(comma_csv_path, separator=',')

    print("\n" + "=" * 80)
    print("Ornekler tamamlandi!")
    print(f"Cikti dosyalari: {output_dir}")
    print("=" * 80)


def advanced_examples():
    """Daha gelişmiş kullanım örnekleri"""
    print("\n" + "=" * 80)
    print("Gelişmiş Örnekler")
    print("=" * 80)

    data_path = os.path.join("..", "..", "data", "singleTraderOptLog.csv")
    analyzer = OptLogAnalyzer(data_path)

    # 1. Risk-Reward analizi
    print("\n1. Risk-Reward Analizi")
    print("-" * 80)
    print("Düşük MaxDD, yüksek Net Profit")

    # MaxDD negatif değerler içerebilir, mutlak değer alıyoruz
    analyzer.df['Risk_Reward'] = analyzer.df['OR_NetProf'] / analyzer.df['OR_MaxDD'].abs()

    # En iyi risk-reward oranına sahip sistemler
    best_rr = analyzer.order_by('Risk_Reward', ascending=False)
    print(best_rr[['CombNo', 'period', 'percent', 'OR_NetProf', 'OR_MaxDD', 'Risk_Reward']].head(10))

    # 2. Sharpe Ratio bazlı filtreleme
    print("\n2. Sharpe Ratio Analizi")
    print("-" * 80)
    if 'OR_Sharpe' in analyzer.columns():
        high_sharpe = analyzer.where("OR_Sharpe > 0.5")
        print(f"Sharpe > 0.5 olan sistem sayısı: {len(high_sharpe)}")

    # 3. Period ve Percent kombinasyonları
    print("\n3. Period-Percent Kombinasyonları (En İyi 3)")
    print("-" * 80)
    pivot = analyzer.df.groupby(['period', 'percent'])['OR_NetProf'].mean().reset_index()
    pivot_sorted = pivot.sort_values('OR_NetProf', ascending=False).head(3)
    print(pivot_sorted)

    print("\n" + "=" * 80)

def plot_graphs(viz : MyCustomVisualizer):

    #########################################################################
    viz.plot_x_y_z(
        x='OR_GetFiyat',
        y='period',
        z='percent',
        title='Getiri vs Period (Percent ile renkli)',
        size_ref='OR_GetFiyat',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='OR_GetFiyat',
        y='percent',
        z='period',
        title='Getiri vs Percent (Period ile renkli)',
        size_ref='OR_GetFiyat',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='OR_GetFyNet',
        y='OR_Islem',
        z='OR_KomFiyat',
        title='Getiri vs İslem (Komisyon ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='OR_GetFyNet',
        y='OR_KomFiyat',
        z='OR_Islem',
        title='Getiri vs Komisyon (İslem ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    # viz.plot_x_y_z(
    #     x='OR_GetFyNet',
    #     y='OR_MinBakFy',
    #     z='OR_GetFyNet',
    #     title='Getiri vs MinBakFy (Getiri ile renkli)',
    #     size_ref='OR_GetFyNet',
    #     show=True,
    #     save=True
    # )
    #
    # viz.plot_x_y_z(
    #     x='OR_GetFyNet',
    #     y='OR_MaxBakFy',
    #     z='OR_GetFyNet',
    #     title='Getiri vs MaxBakFy (Getiri ile renkli)',
    #     size_ref='OR_GetFyNet',
    #     show=True,
    #     save=True
    # )

    viz.plot_x_y_z(
        x='OR_GetFyNet',
        y='OR_MinBakNt',
        z='OR_GetFyNet',
        title='Getiri vs MinBakNt (Getiri ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='OR_GetFyNet',
        y='OR_MaxBakNt',
        z='OR_GetFyNet',
        title='Getiri vs MaxBakNt (Getiri ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    #########################################################################
    viz.plot_x_y_z(
        x='CombNo',
        y='OR_GetFy%N',
        z='OR_KomFiyat',
        title='CombNo vs Getiri% (Komisyon ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='CombNo',
        y='OR_GetFyNet',
        z='OR_KomFiyat',
        title='CombNo vs Getiri (Komisyon ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='CombNo',
        y='OR_KomFiyat',
        z='OR_GetFyNet',
        title='CombNo vs Komisyon (etFyNet ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='CombNo',
        y='OR_Islem',
        z='OR_GetFyNet',
        title='CombNo vs İslem (Getiri ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='CombNo',
        y='OR_MinBakNt',
        z='OR_GetFyNet',
        title='CombNo vs MinBakNt (Getiri ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='CombNo',
        y='OR_MaxBakNt',
        z='OR_GetFyNet',
        title='CombNo vs MaxBakNt (Getiri ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='CombNo',
        y='OR_MaxDD',
        z='OR_GetFyNet',
        title='CombNo vs MaxDD (Getiri ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='CombNo',
        y='OR_NetProf',
        z='OR_GetFyNet',
        title='CombNo vs NetProfit (Getiri ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='CombNo',
        y='OR_KarliOra',
        z='OR_GetFyNet',
        title='CombNo vs KarliOrani (Getiri ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    #########################################################################
    viz.plot_x_y_z(
        x='OR_MinBakNt',
        y='OR_MaxBakNt',
        z='OR_GetFyNet',
        title='MinBakiye vs MaxBakiye (Getiri renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='OR_GetFyNet',
        y='OR_MaxDD',
        z='OR_GetFyNet',
        title='Getiri vs MaxDD (Getiri ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='OR_GetFyNet',
        y='OR_NetProf',    # OR_NetProf, OR_ProfFact
        z='OR_GetFyNet',
        title='Getiri vs ProfFactNet (Getiri ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    viz.plot_x_y_z(
        x='OR_GetFyNet',
        y='OR_KarliOra',
        z='OR_GetFyNet',
        title='Getiri vs KarliOra (Getiri ile renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )


    # """
    # Tüm grafikleri tek bir HTML sayfasında alt alta gösterir
    # """
    # print("\n" + "=" * 80)
    # print("Grafikleri tek HTML'de alt alta çizdiriliyor...")
    # print("=" * 80)
    #
    # # Grafik konfigürasyonları
    # plots = [
    #     {
    #         'x': 'OR_GetFiyat',
    #         'y': 'period',
    #         'z': 'percent',
    #         'title': 'Getiri vs Period (Percent ile renkli)',
    #         'size_ref': 'OR_GetFiyat'
    #     },
    #     {
    #         'x': 'CombNo',
    #         'y': 'OR_GetFyNet',
    #         'z': 'OR_KomFiyat',
    #         'title': 'CombNo vs Getiri (Komisyon ile renkli)',
    #         'size_ref': 'OR_GetFyNet'
    #     },
    #     {
    #         'x': 'OR_GetFyNet',
    #         'y': 'OR_Islem',
    #         'z': 'OR_KomFiyat',
    #         'title': 'Getiri vs İslem (Komisyon ile renkli)',
    #         'size_ref': 'OR_GetFyNet'
    #     },
    #     {
    #         'x': 'OR_GetFyNet',
    #         'y': 'OR_KomFiyat',
    #         'z': 'OR_Islem',
    #         'title': 'Getiri vs Komisyon (İslem ile renkli)',
    #         'size_ref': 'OR_GetFyNet'
    #     },
    #     {
    #         'x': 'CombNo',
    #         'y': 'OR_Islem',
    #         'z': 'OR_GetFyNet',
    #         'title': 'CombNo vs İşlem (Getiri ile renkli)',
    #         'size_ref': 'OR_GetFyNet'
    #     }
    # ]
    #
    # # Tek bir HTML'de alt alta (cols=1)
    # viz.plot_x_y_z_dashboard(
    #     plots=plots,
    #     cols=1,  # Alt alta çizdirmek için 1 sütun
    #     title="Tüm Grafikler - Alt Alta",
    #     width=1600,
    #     height=7*800,  # 3 grafik için yeterli yükseklik
    #     show=True,
    #     save=True
    # )

def calculate_composite_score(df: pd.DataFrame, top_n: int = 20, weights: dict = None) -> pd.DataFrame:
    """
    İlk N kayıt içinden composite score hesaplar ve en iyisini bulur.

    Metrikler:
    - OR_GetFyNet: Net Getiri (yüksek = iyi)
    - OR_MaxDD: Maximum Drawdown (düşük = iyi, dikkat: pozitif değer)
    - OR_ProfFact: Profit Factor (yüksek = iyi)
    - OR_KarliOra: Win Rate % (yüksek = iyi)
    - OR_MinBakNt: Minimum Bakiye (yüksek = iyi, daha az batmış)
    - OR_KomFiyat: Komisyon (düşük = iyi)

    Args:
        df: DataFrame (zaten sıralanmış olmalı)
        top_n: İlk kaç kayıt içinden seçim yapılacak
        weights: Ağırlıklar dict'i (varsayılan kullanılır)

    Returns:
        Skorlanmış ve sıralanmış DataFrame
    """
    import numpy as np

    # Varsayılan ağırlıklar (toplamı 1.0 olmalı)
    # AYARLANABILIR: Risk-ağırlıklı profil için getiri düşür, maxdd/minbak artır
    if weights is None:
        weights = {
            'getiri': 0.15,      # Net getiri (düşürüldü - sadece getiriye bakma!)
            'maxdd': 0.30,       # Maximum Drawdown - EN ÖNEMLİ RİSK METRİĞİ
            'profact': 0.20,     # Profit Factor (tutarlılık)
            'karliora': 0.15,    # Win Rate
            'minbak': 0.15,      # Minimum Bakiye (ne kadar batmış) - artırıldı
            'komisyon': 0.05     # Komisyon maliyeti
        }

    print(f"\n{'='*80}")
    print(f"COMPOSITE SCORE HESAPLAMA (İlk {top_n} kayıt)")
    print(f"{'='*80}")
    print(f"Ağırlıklar: {weights}")

    # İlk N kaydı al
    df_top = df.head(top_n).copy()

    if len(df_top) == 0:
        print("HATA: DataFrame boş!")
        return df_top

    # Min-Max normalizasyon fonksiyonu (0-100 arası)
    def normalize(series, reverse=False):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series), index=series.index)
        normalized = (series - min_val) / (max_val - min_val) * 100
        if reverse:
            normalized = 100 - normalized
        return normalized

    # Her metrik için normalize skor hesapla
    df_top['_score_getiri'] = normalize(df_top['OR_GetFyNet'], reverse=False)
    df_top['_score_maxdd'] = normalize(df_top['OR_MaxDD'], reverse=True)  # Düşük DD = yüksek skor
    df_top['_score_profact'] = normalize(df_top['OR_ProfFact'], reverse=False)
    df_top['_score_karliora'] = normalize(df_top['OR_KarliOra'], reverse=False)
    df_top['_score_minbak'] = normalize(df_top['OR_MinBakNt'], reverse=False)  # Yüksek = iyi
    df_top['_score_komisyon'] = normalize(df_top['OR_KomFiyat'], reverse=True)  # Düşük = iyi

    # Risk-Adjusted Return (bonus metrik)
    df_top['_risk_adj_return'] = df_top['OR_GetFyNet'] / (df_top['OR_MaxDD'].abs() + 1)
    df_top['_score_risk_adj'] = normalize(df_top['_risk_adj_return'], reverse=False)

    # Composite Score hesapla
    df_top['CompositeScore'] = (
        df_top['_score_getiri'] * weights['getiri'] +
        df_top['_score_maxdd'] * weights['maxdd'] +
        df_top['_score_profact'] * weights['profact'] +
        df_top['_score_karliora'] * weights['karliora'] +
        df_top['_score_minbak'] * weights['minbak'] +
        df_top['_score_komisyon'] * weights['komisyon']
    )

    # Skor sütunlarını temizle (isteğe bağlı gösterim için tut)
    score_cols = ['_score_getiri', '_score_maxdd', '_score_profact',
                  '_score_karliora', '_score_minbak', '_score_komisyon',
                  '_risk_adj_return', '_score_risk_adj']

    # Composite Score'a göre sırala
    df_sorted = df_top.sort_values('CompositeScore', ascending=False)

    # Sonuçları göster
    print(f"\n{'='*80}")
    print("EN İYİ 10 KOMBİNASYON (Composite Score'a göre)")
    print(f"{'='*80}")

    display_cols = ['CombNo', 'period', 'percent', 'OR_GetFyNet', 'OR_MaxDD',
                    'OR_ProfFact', 'OR_KarliOra', 'OR_MinBakNt', 'OR_KomFiyat', 'CompositeScore']

    # Mevcut sütunları filtrele
    available_cols = [c for c in display_cols if c in df_sorted.columns]

    print(df_sorted[available_cols].head(10).to_string(index=False))

    # DEBUG: Her metriğin skorunu göster
    print(f"\n{'='*80}")
    print("DETAYLI SKOR ANALİZİ (Normalize edilmiş 0-100)")
    print(f"{'='*80}")
    print("Skor = (Metrik normalize edilmiş) × Ağırlık")
    print(f"Ağırlıklar: getiri={weights['getiri']}, maxdd={weights['maxdd']}, profact={weights['profact']}, karliora={weights['karliora']}, minbak={weights['minbak']}, kom={weights['komisyon']}")
    print("-" * 120)

    debug_cols = ['CombNo', '_score_getiri', '_score_maxdd', '_score_profact',
                  '_score_karliora', '_score_minbak', '_score_komisyon', 'CompositeScore']
    debug_available = [c for c in debug_cols if c in df_sorted.columns]

    # Formatla ve göster
    debug_df = df_sorted[debug_available].head(10).copy()
    for col in debug_df.columns:
        if col.startswith('_score') or col == 'CompositeScore':
            debug_df[col] = debug_df[col].apply(lambda x: f"{x:.1f}")
    print(debug_df.to_string(index=False))

    # En iyi kombinasyonu vurgula
    best = df_sorted.iloc[0]
    print(f"\n{'='*80}")
    print("🏆 EN İYİ KOMBİNASYON")
    print(f"{'='*80}")
    print(f"  CombNo      : {best['CombNo']}")
    print(f"  Period      : {best['period']}")
    print(f"  Percent     : {best['percent']}")
    print(f"  Net Getiri  : {best['OR_GetFyNet']:,.0f}")
    print(f"  Max DD      : {best['OR_MaxDD']:.2f}")
    print(f"  Profit Fact : {best['OR_ProfFact']:.2f}")
    print(f"  Win Rate    : {best['OR_KarliOra']:.2f}%")
    print(f"  Min Bakiye  : {best['OR_MinBakNt']:,.0f}")
    print(f"  Komisyon    : {best['OR_KomFiyat']:,.0f}")
    print(f"  SKOR        : {best['CompositeScore']:.2f}/100")
    print(f"{'='*80}")

    # Karşılaştırma: 1. sıra vs En iyi skor
    first_row = df.iloc[0]
    if best['CombNo'] != first_row['CombNo']:
        print(f"\n⚠️  DİKKAT: En yüksek getirili (1. sıra) ile en iyi skor farklı!")
        print(f"    1. Sıra  : CombNo={first_row['CombNo']}, Getiri={first_row['OR_GetFyNet']:,.0f}, MaxDD={first_row['OR_MaxDD']:.2f}")
        print(f"    En İyi   : CombNo={best['CombNo']}, Getiri={best['OR_GetFyNet']:,.0f}, MaxDD={best['OR_MaxDD']:.2f}")

        # Fark analizi
        getiri_fark = (best['OR_GetFyNet'] - first_row['OR_GetFyNet']) / first_row['OR_GetFyNet'] * 100
        dd_fark = (first_row['OR_MaxDD'] - best['OR_MaxDD']) / first_row['OR_MaxDD'] * 100
        print(f"\n    Getiri farkı: {getiri_fark:+.2f}%")
        print(f"    DD iyileşme : {dd_fark:+.2f}% (düşük DD daha iyi)")
    else:
        print(f"\n✅ En yüksek getirili kombinasyon aynı zamanda en iyi skorlu!")

    # Skor sütunlarını kaldır (opsiyonel - yorumu kaldırarak tutabilirsiniz)
    # df_sorted = df_sorted.drop(columns=score_cols, errors='ignore')

    return df_sorted


def analyze_combination_diversity(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    Kombinasyonların birbirinden ne kadar farklı olduğunu analiz eder.
    Diversifikasyon için FARKLI davranan kombinasyonlar seçilmeli.

    Args:
        df: DataFrame
        top_n: Analiz edilecek kayıt sayısı
    """
    import numpy as np

    print(f"\n{'='*80}")
    print("KOMBİNASYON DİVERSİFİKASYON ANALİZİ")
    print("Hangi kombinasyonlar birbirinden FARKLI davranıyor?")
    print(f"{'='*80}")

    df_top = df.head(top_n).copy()

    # Normalize edilmiş metrikler (karşılaştırma için)
    metrics = ['OR_GetFyNet', 'OR_MaxDD', 'OR_ProfFact', 'OR_KarliOra',
               'OR_MinBakNt', 'OR_KomFiyat', 'OR_Islem']

    available_metrics = [m for m in metrics if m in df_top.columns]

    # Her kombinasyon için profil oluştur
    from sklearn.preprocessing import MinMaxScaler

    try:
        scaler = MinMaxScaler()
        df_scaled = pd.DataFrame(
            scaler.fit_transform(df_top[available_metrics]),
            columns=available_metrics,
            index=df_top.index
        )
    except ImportError:
        # sklearn yoksa manuel normalize
        def normalize(series):
            return (series - series.min()) / (series.max() - series.min() + 0.0001)
        df_scaled = df_top[available_metrics].apply(normalize)

    # Kombinasyonlar arası mesafe hesapla (Euclidean)
    n = len(df_top)
    distance_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            diff = df_scaled.iloc[i].values - df_scaled.iloc[j].values
            distance_matrix[i, j] = np.sqrt(np.sum(diff ** 2))

    # Her kombinasyon için ortalama mesafe (diğerlerinden ne kadar farklı)
    df_top['Diversity_Score'] = distance_matrix.mean(axis=1)

    # Period ve Percent gruplarını analiz et
    print(f"\n{'='*80}")
    print("PERIOD GRUPLARI")
    print(f"{'='*80}")
    period_groups = df_top.groupby('period').agg({
        'CombNo': 'count',
        'OR_GetFyNet': 'mean',
        'OR_MaxDD': 'mean'
    }).rename(columns={'CombNo': 'Adet'})
    print(period_groups.to_string())

    # En farklı kombinasyonları bul
    print(f"\n{'='*80}")
    print("EN FARKLI DAVRANAN KOMBİNASYONLAR (Yüksek Diversity = İyi)")
    print(f"{'='*80}")

    df_diverse = df_top.sort_values('Diversity_Score', ascending=False)

    display_cols = ['CombNo', 'period', 'percent', 'OR_GetFyNet', 'OR_MaxDD',
                    'OR_ProfFact', 'Diversity_Score']
    print(df_diverse[display_cols].head(10).to_string(index=False))

    # Önerilen portföy: Farklı period'lardan seçim
    print(f"\n{'='*80}")
    print("ÖNERİLEN PORTFÖY (Farklı Period'lardan)")
    print(f"{'='*80}")

    # Her unique period'dan en iyi getiriliyi seç
    unique_periods = df_top['period'].unique()
    portfolio = []

    for period in sorted(unique_periods)[:5]:  # İlk 5 farklı period
        period_best = df_top[df_top['period'] == period].nlargest(1, 'OR_GetFyNet')
        if len(period_best) > 0:
            portfolio.append(period_best.iloc[0])

    if portfolio:
        portfolio_df = pd.DataFrame(portfolio)
        print(portfolio_df[['CombNo', 'period', 'percent', 'OR_GetFyNet', 'OR_MaxDD']].to_string(index=False))

        # Portföy özeti
        print(f"\n📊 PORTFÖY ÖZETİ (eşit ağırlıklı)")
        print(f"   Toplam kombinasyon: {len(portfolio)}")
        print(f"   Ortalama Getiri   : {portfolio_df['OR_GetFyNet'].mean():,.0f}")
        print(f"   Ortalama MaxDD    : {portfolio_df['OR_MaxDD'].mean():.2f}")
        print(f"   Period aralığı    : {portfolio_df['period'].min()} - {portfolio_df['period'].max()}")

    return df_diverse


def calculate_dd_quality(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    MaxDD kalitesini analiz eder - sadece MaxDD değerine değil,
    nasıl oluştuğuna da bakar.

    Hesaplanan Metrikler:
    - DD_per_Trade: MaxDD / Toplam İşlem (işlem başına DD)
    - Trade_Density: Günlük işlem sayısı
    - DD_Duration_Est: Tahmini DD süresi (gün)
    - DD_Quality_Score: Düşük = ani çöküş, Yüksek = yavaş erozyon

    Args:
        df: DataFrame
        top_n: Analiz edilecek kayıt sayısı
    """
    print(f"\n{'='*80}")
    print("DRAWDOWN KALİTE ANALİZİ")
    print("MaxDD'nin NASIL oluştuğunu inceler")
    print(f"{'='*80}")

    df_top = df.head(top_n).copy()

    # Test süresi hesapla (gün olarak)
    # OR_IlkBarDT ve OR_SonBarDT varsa kullan
    if 'OR_IlkBarDT' in df_top.columns and 'OR_SonBarDT' in df_top.columns:
        try:
            df_top['_ilk_tarih'] = pd.to_datetime(df_top['OR_IlkBarDT'], errors='coerce')
            df_top['_son_tarih'] = pd.to_datetime(df_top['OR_SonBarDT'], errors='coerce')
            df_top['Test_Gun'] = (df_top['_son_tarih'] - df_top['_ilk_tarih']).dt.days
        except:
            df_top['Test_Gun'] = 3650  # Varsayılan 10 yıl
    else:
        df_top['Test_Gun'] = 3650

    # Temel hesaplamalar
    df_top['DD_per_Trade'] = df_top['OR_MaxDD'] / df_top['OR_Islem'].replace(0, 1)
    df_top['Trades_per_Day'] = df_top['OR_Islem'] / df_top['Test_Gun'].replace(0, 1)
    df_top['DD_per_Day'] = df_top['OR_MaxDD'] / df_top['Test_Gun'].replace(0, 1)

    # DD Kalite Skoru (yüksek = daha iyi, daha yavaş/yayılmış DD)
    # Çok işlem + düşük DD/işlem = iyi
    # Az işlem + yüksek DD/işlem = kötü (ani çöküş)

    def normalize(series, reverse=False):
        min_val, max_val = series.min(), series.max()
        if max_val == min_val:
            return 50.0
        norm = (series - min_val) / (max_val - min_val) * 100
        return 100 - norm if reverse else norm

    # DD per Trade düşük olmalı (reverse=True)
    df_top['_score_dd_per_trade'] = normalize(df_top['DD_per_Trade'], reverse=True)

    # Trades per Day yüksek olmalı (aktif sistem)
    df_top['_score_trade_density'] = normalize(df_top['Trades_per_Day'], reverse=False)

    # MaxDD düşük olmalı
    df_top['_score_maxdd'] = normalize(df_top['OR_MaxDD'], reverse=True)

    # DD Kalite Skoru
    df_top['DD_Quality'] = (
        df_top['_score_dd_per_trade'] * 0.40 +   # İşlem başına DD düşük mü?
        df_top['_score_trade_density'] * 0.30 +  # Aktif mi? (çok işlem)
        df_top['_score_maxdd'] * 0.30            # Toplam DD düşük mü?
    )

    # Sırala
    df_sorted = df_top.sort_values('DD_Quality', ascending=False)

    # Sonuçları göster
    print(f"\n{'='*80}")
    print("EN İYİ DD KALİTESİNE SAHİP KOMBİNASYONLAR")
    print(f"{'='*80}")
    print("DD_Quality = Yüksek ise DD 'kabul edilebilir' şekilde oluşmuş")
    print("           = Düşük ise DD 'ani çöküş' şeklinde oluşmuş")
    print("-" * 100)

    display_cols = ['CombNo', 'period', 'percent', 'OR_GetFyNet', 'OR_MaxDD',
                    'OR_Islem', 'DD_per_Trade', 'Trades_per_Day', 'DD_Quality']

    # Formatla
    display_df = df_sorted[display_cols].head(15).copy()
    display_df['OR_GetFyNet'] = display_df['OR_GetFyNet'].apply(lambda x: f"{x:,.0f}")
    display_df['DD_per_Trade'] = display_df['DD_per_Trade'].apply(lambda x: f"{x:.4f}")
    display_df['Trades_per_Day'] = display_df['Trades_per_Day'].apply(lambda x: f"{x:.2f}")
    display_df['DD_Quality'] = display_df['DD_Quality'].apply(lambda x: f"{x:.1f}")

    print(display_df.to_string(index=False))

    # En iyi ve en kötü karşılaştırması
    best = df_sorted.iloc[0]
    worst = df_sorted.iloc[-1]

    print(f"\n{'='*80}")
    print("KARŞILAŞTIRMA: En İyi vs En Kötü DD Kalitesi")
    print(f"{'='*80}")
    print(f"{'Metrik':<20} {'En İyi (CombNo=' + str(int(best['CombNo'])) + ')':<25} {'En Kötü (CombNo=' + str(int(worst['CombNo'])) + ')':<25}")
    print("-" * 70)
    print(f"{'MaxDD':<20} {best['OR_MaxDD']:<25.2f} {worst['OR_MaxDD']:<25.2f}")
    print(f"{'Toplam İşlem':<20} {best['OR_Islem']:<25.0f} {worst['OR_Islem']:<25.0f}")
    print(f"{'DD / İşlem':<20} {best['DD_per_Trade']:<25.4f} {worst['DD_per_Trade']:<25.4f}")
    print(f"{'İşlem / Gün':<20} {best['Trades_per_Day']:<25.2f} {worst['Trades_per_Day']:<25.2f}")
    print(f"{'DD Kalite Skoru':<20} {best['DD_Quality']:<25.1f} {worst['DD_Quality']:<25.1f}")

    # Yorum
    print(f"\n💡 YORUM:")
    if best['DD_per_Trade'] < worst['DD_per_Trade']:
        print(f"   CombNo={int(best['CombNo'])}: İşlem başına DD düşük → DD yavaş/dağınık oluşmuş (iyi)")
        print(f"   CombNo={int(worst['CombNo'])}: İşlem başına DD yüksek → DD ani/yoğun oluşmuş (kötü)")

    return df_sorted


def find_best_risk_adjusted(df: pd.DataFrame,
                            top_n: int = 50,
                            min_getiri_pct: float = 50) -> pd.DataFrame:
    """
    "Yeterli getiri + En düşük risk" yaklaşımı.

    1. İlk N kayıttan, getiri skoru >= min_getiri_pct olanları filtrele
    2. Bu filtrelenmiş grup içinde SADECE RİSK metriklerine göre sırala

    Args:
        df: Sıralanmış DataFrame
        top_n: İlk kaç kayıt içinden seçim
        min_getiri_pct: Minimum getiri yüzdesi (0-100).
                        50 = en yüksek getirinin %50'sinden fazla olanlar
    """
    print(f"\n{'='*80}")
    print("YETERLİ GETİRİ + EN DÜŞÜK RİSK ANALİZİ")
    print(f"{'='*80}")

    df_top = df.head(top_n).copy()

    # Getiriyi normalize et
    max_getiri = df_top['OR_GetFyNet'].max()
    min_getiri = df_top['OR_GetFyNet'].min()
    df_top['_getiri_pct'] = (df_top['OR_GetFyNet'] - min_getiri) / (max_getiri - min_getiri) * 100

    # Minimum getiri eşiğini geçenleri filtrele
    df_filtered = df_top[df_top['_getiri_pct'] >= min_getiri_pct].copy()
    print(f"Getiri skoru >= {min_getiri_pct} olanlar: {len(df_filtered)} kayıt")

    if len(df_filtered) == 0:
        print("UYARI: Filtreleme sonrası kayıt kalmadı!")
        return df_filtered

    # SADECE RİSK metriklerini normalize et
    def normalize(series, reverse=False):
        min_val, max_val = series.min(), series.max()
        if max_val == min_val:
            return 50.0
        norm = (series - min_val) / (max_val - min_val) * 100
        return 100 - norm if reverse else norm

    # Risk skorları (getiri YOK!)
    df_filtered['_risk_maxdd'] = normalize(df_filtered['OR_MaxDD'], reverse=True)
    df_filtered['_risk_minbak'] = normalize(df_filtered['OR_MinBakNt'], reverse=False)
    df_filtered['_risk_profact'] = normalize(df_filtered['OR_ProfFact'], reverse=False)
    df_filtered['_risk_karliora'] = normalize(df_filtered['OR_KarliOra'], reverse=False)

    # RİSK SKORU (getiri dahil değil!)
    df_filtered['RiskScore'] = (
        df_filtered['_risk_maxdd'] * 0.40 +      # MaxDD en önemli
        df_filtered['_risk_minbak'] * 0.25 +     # MinBak ikinci
        df_filtered['_risk_profact'] * 0.20 +    # ProfFact
        df_filtered['_risk_karliora'] * 0.15     # WinRate
    )

    # Risk skoruna göre sırala (yüksek = düşük risk)
    df_sorted = df_filtered.sort_values('RiskScore', ascending=False)

    print(f"\n{'='*80}")
    print(f"EN DÜŞÜK RİSKLİ KOMBİNASYONLAR (Getiri >= {min_getiri_pct}% eşiğini geçenler)")
    print(f"{'='*80}")
    print("RiskScore = MaxDD×0.40 + MinBak×0.25 + ProfFact×0.20 + WinRate×0.15")
    print("-" * 100)

    display_cols = ['CombNo', 'period', 'percent', 'OR_GetFyNet', 'OR_MaxDD',
                    'OR_MinBakNt', 'OR_ProfFact', 'OR_KarliOra', '_getiri_pct', 'RiskScore']
    print(df_sorted[display_cols].head(10).to_string(index=False))

    # En iyi
    best = df_sorted.iloc[0]
    print(f"\n{'='*80}")
    print("🏆 EN DÜŞÜK RİSKLİ (Yeterli Getirili) KOMBİNASYON")
    print(f"{'='*80}")
    print(f"  CombNo      : {best['CombNo']}")
    print(f"  Period      : {best['period']}")
    print(f"  Percent     : {best['percent']}")
    print(f"  Net Getiri  : {best['OR_GetFyNet']:,.0f} (skor: {best['_getiri_pct']:.1f}%)")
    print(f"  Max DD      : {best['OR_MaxDD']:.2f}")
    print(f"  Min Bakiye  : {best['OR_MinBakNt']:,.0f}")
    print(f"  RİSK SKORU  : {best['RiskScore']:.1f}/100 (yüksek = düşük risk)")
    print(f"{'='*80}")

    return df_sorted


def find_best_combination(df: pd.DataFrame,
                          top_n: int = 20,
                          min_getiri: float = None,
                          max_dd: float = None,
                          min_winrate: float = None,
                          min_profact: float = None,
                          min_islem: int = None,
                          min_komisyon: float = None) -> pd.DataFrame:
    """
    Filtreleme + Composite Score ile en iyi kombinasyonu bulur.

    Args:
        df: Sıralanmış DataFrame
        top_n: İlk kaç kayıt içinden seçim
        min_getiri: Minimum net getiri filtresi
        max_dd: Maximum drawdown filtresi (bu değerden küçük olanlar)
        min_winrate: Minimum win rate %
        min_profact: Minimum profit factor
        min_islem: Minimum işlem sayısı (önemli! az işlem = güvenilmez)
        min_komisyon: Minimum komisyon (az komisyon = az işlem)

    Returns:
        Filtrelenmiş ve skorlanmış DataFrame
    """
    print(f"\n{'='*80}")
    print("FİLTRELEME + COMPOSITE SCORE")
    print(f"{'='*80}")

    df_filtered = df.head(top_n).copy()
    initial_count = len(df_filtered)

    # Filtreleri uygula
    if min_getiri is not None:
        df_filtered = df_filtered[df_filtered['OR_GetFyNet'] >= min_getiri]
        print(f"  Min Getiri >= {min_getiri:,.0f}: {len(df_filtered)} kayıt kaldı")

    if max_dd is not None:
        df_filtered = df_filtered[df_filtered['OR_MaxDD'] <= max_dd]
        print(f"  Max DD <= {max_dd}: {len(df_filtered)} kayıt kaldı")

    if min_winrate is not None:
        df_filtered = df_filtered[df_filtered['OR_KarliOra'] >= min_winrate]
        print(f"  Win Rate >= {min_winrate}%: {len(df_filtered)} kayıt kaldı")

    if min_profact is not None:
        df_filtered = df_filtered[df_filtered['OR_ProfFact'] >= min_profact]
        print(f"  Profit Factor >= {min_profact}: {len(df_filtered)} kayıt kaldı")

    # ÖNEMLİ: İşlem sayısı filtresi (az işlem = istatistiksel olarak güvenilmez)
    if min_islem is not None:
        df_filtered = df_filtered[df_filtered['OR_Islem'] >= min_islem]
        print(f"  Min İşlem >= {min_islem}: {len(df_filtered)} kayıt kaldı")

    # Komisyon filtresi (az komisyon = az işlem)
    if min_komisyon is not None:
        df_filtered = df_filtered[df_filtered['OR_KomFiyat'] >= min_komisyon]
        print(f"  Min Komisyon >= {min_komisyon:,.0f}: {len(df_filtered)} kayıt kaldı")

    print(f"\n  Toplam: {initial_count} -> {len(df_filtered)} kayıt")

    if len(df_filtered) == 0:
        print("UYARI: Filtreleme sonrası kayıt kalmadı! Kriterleri gevşetin.")
        return df_filtered

    # Composite score hesapla
    return calculate_composite_score(df_filtered, top_n=len(df_filtered))


def plot_graphs_2(viz: MyCustomVisualizer):
    """
    Risk-Adjusted ve Performans Analiz Grafikleri
    Kombinasyon seçimi için kritik metrikler
    """
    print("\n" + "=" * 80)
    print("RISK-ADJUSTED PERFORMANS ANALİZİ")
    print("=" * 80)

    # 1. Risk-Adjusted Return (EN KRİTİK)
    # Yüksek getiri + Düşük drawdown = İdeal kombinasyon
    print("\n[1] Getiri vs MaxDrawdown (ProfitFactor renkli)")
    print("    -> Sağ-alt köşe = En iyi (yüksek getiri + düşük DD)")
    viz.plot_x_y_z(
        x='OR_GetFyNet',
        y='OR_MaxDD',
        z='OR_ProfFact',
        title='Getiri vs MaxDrawdown (ProfitFactor renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    # 2. Profit Factor vs Risk
    # ProfFact > 1.5 ve düşük DD = tutarlı sistem
    print("\n[2] ProfitFactor vs MaxDD (Getiri renkli)")
    print("    -> Sağ-alt köşe + parlak renk = En iyi")
    viz.plot_x_y_z(
        x='OR_ProfFact',
        y='OR_MaxDD',
        z='OR_GetFyNet',
        title='ProfitFactor vs MaxDD (Getiri renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    # 3. Win Rate vs Profit Factor
    # Yüksek winrate + yüksek PF = tutarlı karlılık
    print("\n[3] WinRate vs ProfitFactor (Getiri renkli)")
    print("    -> Sağ-üst köşe = İdeal")
    viz.plot_x_y_z(
        x='OR_KarliOra',
        y='OR_ProfFact',
        z='OR_GetFyNet',
        title='WinRate vs ProfitFactor (Getiri renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    # 4. Kazanan vs Kaybeden İşlem
    # Kazanan/Kaybeden oranı görsel
    print("\n[4] Kazanan vs Kaybeden İşlem (Getiri renkli)")
    print("    -> Diagonal üstü = Kazand > Kaybett")
    viz.plot_x_y_z(
        x='OR_Kazand',
        y='OR_Kaybett',
        z='OR_GetFyNet',
        title='Kazanan vs Kaybeden (Getiri renkli)',
        size_ref='OR_GetFyNet',
        show=True,
        save=True
    )

    # 5. Toplam Kar vs Toplam Zarar
    print("\n[5] ToplamKar vs ToplamZarar (ProfitFactor renkli)")
    viz.plot_x_y_z(
        x='OR_TopKarFy',
        y='OR_TopZarFy',
        z='OR_ProfFact',
        title='ToplamKar vs ToplamZarar (ProfFact renkli)',
        size_ref='OR_NetKarFy',
        show=True,
        save=True
    )

    # 6. Bakiye Dalgalanması (Tutarlılık)
    # MinBak yüksek (az batmış) + MaxBak yüksek = tutarlı
    print("\n[6] MinBakiye vs MaxBakiye (Getiri renkli)")
    print("    -> MinBak yüksek = Daha az batmış")



def main():
    """
    Ana kullanım örneği: Sütun listesi + SQL sorguları
    """
    # ========== EKRAN GOSTERIM AYARLARI (KULLANICI BURADAN DEGISTIREBILIR) ==========
    DISPLAY_COLS = 20  # Ekranda gösterilecek sütun sayısı (10-20 arası önerilir, -1 = tümü)
    DISPLAY_ROWS = 90  # Ekranda gösterilecek satır sayısı (10-20 arası önerilir, -1 = tümü)
    # ================================================================================

    print("=" * 80)
    print("OptLogAnalyzer - SQL Sorgu Ornekleri")
    print("=" * 80)
    print(f"Ekran gosterim ayarlari: {DISPLAY_COLS} sutun x {DISPLAY_ROWS} satir")

    # Dosya yolu
    data_path = os.path.join("..", "..", "data", "singleTraderOptLog.csv")

    # Analyzer'ı başlat ve dosyayı yükle
    print("\n1. Dosya Yukleme")
    print("-" * 80)
    analyzer = OptLogAnalyzer(data_path)

    # Tüm sütunları index ile listele
    print("\n2. Tum Sutun Isimleri (Index Numaralariyla)")
    print("-" * 80)
    all_columns = analyzer.columns()
    for idx, col_name in enumerate(all_columns):
        print(f"{idx:3d}: {col_name}")

    print(f"\nToplam {len(all_columns)} sutun bulundu.")

    # SQL Sorguları - Zincirleme/Append edilebilir
    print("\n" + "=" * 80)
    print("3. SQL Sorgulari (pandasql ile)")
    print("=" * 80)

    try:
        # Kontrol: pandasql yüklü mü?
        from pandasql import sqldf

        # DataFrame'i yerel değişkene ata (pandasql için)
        df = analyzer.df

        # SORGU 1: Temel sıralama - OR_GetFy%N'e göre büyükten küçüğe
        print("\n3.1. Sorgu 1: OR_GetFy%N sutununa gore SIRALAMA (DESC)")
        print("-" * 80)

        sql_1 = """
        SELECT *
        FROM df
        ORDER BY `OR_GetFy%N` DESC
        LIMIT 1000
        """

        result_1 = sqldf(sql_1, locals())

        # SORGU 1.1: Result_1'i OR_GetFyNet'a gore azalan sirala
        # result_1 = result_1.sort_values(by='OR_GetFyNet', ascending=False)

        # SORGU 1.2: Result_1'i OR_GetFy%N'a gore azalan sirala
        # result_1 = result_1.sort_values(by='OR_GetFy%N', ascending=False)

        # SORGU 1.3: Result_1'i OR_KomFiyat'a gore azalan sirala
        # result_1 = result_1.sort_values(by='OR_KomFiyat', ascending=False)

        # SORGU 1.4: Once OR_GetFy%N (azalan), sonra OR_KomFiyat (azalan)
        # Bu sayede ana siralama bozulmadan ikincil kriter ile siralama yapilir
        result_1 = result_1.sort_values(by=['OR_GetFyNet', 'OR_KomFiyat'], ascending=[False, False])

        # paramMin = 1000
        # paramMax = 2000
        # result_1 = result_1[(result_1['OR_GetFy%N'] >= paramMin) & (result_1['OR_GetFy%N'] <= paramMax)]
        #
        # paramMin = 1000
        # paramMax = 2000
        # result_1 = result_1[(result_1['OR_GetFyNet'] >= paramMin) & (result_1['OR_GetFyNet'] <= paramMax)]
        #
        # paramMin = 50000
        # paramMax = 99000
        # result_1 = result_1[(result_1['OR_KomFiyat'] >= paramMin) & (result_1['OR_KomFiyat'] <= paramMax)]
        #
        # paramMin = 50000
        # paramMax = 99000
        # result_1 = result_1[(result_1['OR_Islem'] >= paramMin) & (result_1['OR_Islem'] <= paramMax)]
        #
        # paramMin = 50000
        # paramMax = 99000
        # result_1 = result_1[(result_1['OR_KarliOra'] >= paramMin) & (result_1['OR_KarliOra'] <= paramMax)]
        #
        # paramMin = 50000
        # paramMax = 99000
        # result_1 = result_1[(result_1['OR_MaxDD'] >= paramMin) & (result_1['OR_MaxDD'] <= paramMax)]
        #
        # paramMin = 50000
        # paramMax = 99000
        # result_1 = result_1[(result_1['OR_ProfFact'] >= paramMin) & (result_1['OR_ProfFact'] <= paramMax)]
        #
        # paramMin = 50000
        # paramMax = 99000
        # result_1 = result_1[(result_1['OR_NetProf'] >= paramMin) & (result_1['OR_NetProf'] <= paramMax)]
        #
        # paramMin = 50000
        # paramMax = 99000
        # result_1 = result_1[(result_1['OR_MinBakNt'] >= paramMin) & (result_1['OR_MinBakNt'] <= paramMax)]
        #
        # paramMin = 50000
        # paramMax = 99000
        # result_1 = result_1[(result_1['OR_MaxBakNt'] >= paramMin) & (result_1['OR_MaxBakNt'] <= paramMax)]

        result = result_1


        # result_6 = sqldf(sql_6)
        # print(f"Sonuc: Tum kriterleri saglayan {len(result_6)} kayit bulundu")
        # display_cols_6 = ['CombNo', 'period', 'OR_NetProf', 'OR_ProfFact', 'OR_MaxDD', 'RiskReward']
        # if len(result_6) > 0:
        #     print(result_6[display_cols_6].head(20))
        # else:
        #     print("Kriterleri saglayan kayit bulunamadi!")

        # Sonuçları kaydetme örneği
        print("\n\n3.7. Sonuclari Kaydetme")
        print("-" * 80)

        if len(result) > 0:
            output_dir = os.path.join("..", "..", "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Sonucu analyzer'a yükle ve kaydet
            analyzer.df = result

            # Sütunları listeler halinde tanımla
            liste1 = ['CombNo', 'period', 'percent', 'OptResult', 'OR_IlkBakFy', 'OR_BakFiyat']

            liste2 = ['OR_GetFiyat', 'OR_GetFyt%', 'OR_KomFiyat', 'OR_BakFyNet', 'OR_GetFyNet', 'OR_GetFy%N']

            liste3 = ['OR_MinBakFy', 'OR_MaxBakFy', 'OR_MinBak%', 'OR_MaxBak%', 'OR_MinBakNt', 'OR_MaxBakNt']

            liste4 = ['OR_Islem', 'OR_KomIslem', 'OR_Alis', 'OR_Satis', 'OR_Flat', 'OR_Pass', 'OR_KarAl', 'OR_ZararKes']

            liste5 = ['OR_KarliOra', 'OR_MaxDD', 'OR_MaxDDDt', 'OR_MaxKayip', 'OR_ProfFact']

            # Tüm listeleri birleştir
            onemli_sutunlar = liste1 + liste2 + liste3 + liste4 + liste5

            # Bu sütunları en başa taşı, geri kalanlar sağda devam eder
            analyzer.move_columns_to_front(onemli_sutunlar)

            # Dosyaya kaydet
            output_base = os.path.join(output_dir, "sql_filtered_results")
            analyzer.save_both(output_base, col_width=30, col_space=4)
            print(f"\nFiltrelenmis {len(result)} kayit '{output_base}.csv' ve '.txt' olarak kaydedildi")

            # Ekrana da yazdır (yeniden sıralanmış haliyle)
            display_result(analyzer.df, n_cols=DISPLAY_COLS, n_rows=DISPLAY_ROWS,
                          title="Kaydedilen Veri (Sutunlar yeniden siralanmis)")

            # ============================================================
            # CUSTOM VISUALIZATION - MyCustomVisualizer
            # ============================================================
            print("\n" + "=" * 80)
            print("CUSTOM VISUALIZATION")
            print("=" * 80)

            from my_custom_visualizer import MyCustomVisualizer

            # Visualizer oluştur
            viz = MyCustomVisualizer(analyzer.df, output_dir=output_dir)

            # İstatistikleri göster
            viz.get_stats()

            # ============================================================
            # COMPOSITE SCORE - İLK 20'DEN EN İYİSİNİ BUL
            # ============================================================
            print("\n" + "=" * 80)
            print("COMPOSITE SCORE ANALİZİ")
            print("=" * 80)

            # Yöntem 1: Sadece composite score (filtresiz) - DEVRE DIŞI
            # scored_df = calculate_composite_score(result, top_n=20)

            # Yöntem 2: Filtreli composite score
            # min_islem ve min_komisyon ÖNEMLİ: Az işlem = istatistiksel olarak güvenilmez!
            scored_df = find_best_combination(
                result,
                top_n=100,             # İlk 100 içinden ara
                min_getiri=3000000,    # Minimum 3M getiri
                max_dd=350,            # Maximum 350 drawdown
                min_winrate=24,        # Minimum %24 win rate
                min_profact=1.1,       # Minimum 1.1 profit factor
                min_islem=1000,        # ÖNEMLİ: Minimum 1000 işlem
                min_komisyon=30000     # ÖNEMLİ: Minimum 30K komisyon
            )

            # ============================================================
            # YENİ YÖNTEM: Yeterli Getiri + En Düşük Risk
            # ============================================================
            # Getiriyi skor hesabına KATMADAN, sadece minimum eşiği geçenleri al
            # ve bunlar arasından EN DÜŞÜK RİSKLİYİ seç
            risk_df = find_best_risk_adjusted(
                result,
                top_n=100,           # İlk 100 içinden ara
                min_getiri_pct=50    # En yüksek getirinin %50'sinden fazla olanlar
            )

            # ============================================================
            # DRAWDOWN KALİTE ANALİZİ
            # ============================================================
            # MaxDD sadece "ne kadar düştün" der
            # DD Kalite ise "nasıl düştün" e bakar:
            # - Az işlemle büyük DD = ANİ ÇÖKÜŞ (kötü)
            # - Çok işlemle aynı DD = YAVAŞ EROZYON (daha kabul edilebilir)
            dd_quality_df = calculate_dd_quality(result, top_n=20)

            # ============================================================
            # KOMBİNASYON DİVERSİFİKASYON ANALİZİ
            # ============================================================
            # Portföy oluştururken FARKLI davranan kombinasyonlar seç
            # Benzer kombinasyonlar = Aynı anda kazanır/kaybeder (kötü)
            # Farklı kombinasyonlar = Biri kaybederken diğeri kazanır (iyi)
            diversity_df = analyze_combination_diversity(result, top_n=20)

            # Grafikleri çiz
            plot_graphs(viz)

    # # Ornek kullanim:
    # # result = sqldf(sql)
    # # analyzer.df = result  # Sonucu ana df'e yukle
    # # analyzer.save_both('output/sonuc')  # Kaydet
    # """)

    except ImportError:
        print("\n[HATA] 'pandasql' kutuphanesi yuklu degil!")
        print("Yuklemek icin: pip install pandasql")
        print("\nAlternatif: Pandas metodlarini kullanin:")
        print("  analyzer.where('OR_NetProf > 1000000')")
        print("  analyzer.order_by('OR_NetProf', ascending=False)")

    print("\n" + "=" * 80)
    print("Ana ornekler tamamlandi!")
    print("=" * 80)


if __name__ == "__main__":
    # Temel örnekler
    # find_best_combination i kullan
    main()

    # Gelişmiş örnekler için yorum satırını kaldırın
    # advanced_examples()

#   # Filtreleme kriterleri
#   df_filtered = df[
#       (df['OR_MaxDD'] > -5000) &      # Drawdown makul
#       (df['OR_ProfFact'] > 1.2) &      # Profit factor pozitif
#       (df['OR_KarliOra'] > 25) &       # Win rate %25+
#       (df['OR_GetFyNet'] > 0)          # Net getiri pozitif
#   ]

#   # Sonra GetFyNet / abs(MaxDD) oranına göre sırala
#   df_filtered['risk_adj_return'] = df_filtered['OR_GetFyNet'] / abs(df_filtered['OR_MaxDD'])
#   df_filtered.sort_values('risk_adj_return', ascending=False).head(10)    
