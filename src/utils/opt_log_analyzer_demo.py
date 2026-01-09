"""
OptLogAnalyzer Örnek Kullanım ve Test Dosyası
"""

from opt_log_analyzer import OptLogAnalyzer
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
        result = result_1

        # # Ekrana yazdır
        # display_result(result_1, n_cols=DISPLAY_COLS, n_rows=DISPLAY_ROWS,
        #               title="Sorgu 1 - OR_GetFy%N'e gore siralanmis")


        # # SORGU 1.1: Result_1'i OR_KomFiyat'a gore azalan sirala
        # result_1 = result_1.sort_values(by='OR_KomFiyat', ascending=False)
        # result = result_1

        # SORGU 1.2: Once OR_GetFy%N (azalan), sonra OR_KomFiyat (azalan)
        # Bu sayede ana siralama bozulmadan ikincil kriter ile siralama yapilir
        result_1 = result_1.sort_values(by=['OR_GetFy%N', 'OR_KomFiyat'], ascending=[False, False])
        result = result_1

        # SORGU 1.3: OR_KomFiyat 100000 ile 500000 arasinda olanlari filtrele
        min_kom = 50000
        max_kom = 99000
        # result_1 uzerinden filtreleme yapiyoruz, sirali listeden seciyoruz
        result_1 = result_1[(result_1['OR_KomFiyat'] >= min_kom) & (result_1['OR_KomFiyat'] <= max_kom)]
        result = result_1


        # # SORGU 2: Sıralama + Filtreleme - OR_KomFiyat aralığı
        # print("\n\n3.2. Sorgu 2: SIRALAMA + FILTRELEME (OR_KomFiyat araligi)")
        # print("-" * 80)
        #
        # # Örnek aralık değerleri
        # min_kom = 100000
        # max_kom = 500000
        #
        # sql_2 = f"""
        # SELECT *
        # FROM df
        # WHERE OR_KomFiyat BETWEEN {min_kom} AND {max_kom}
        # ORDER BY `OR_GetFy%N` DESC
        # LIMIT 10
        # """
        #
        # result_2 = sqldf(sql_2, locals())
        #
        # # # Ekrana yazdır
        # # display_result(result_2, n_cols=DISPLAY_COLS, n_rows=DISPLAY_ROWS,
        # #               title=f"Sorgu 2 - OR_KomFiyat [{min_kom:,} - {max_kom:,}] araliginda filtreli")
        #
        # result = result_2

        # # SORGU 3: Çoklu koşul - İşlem sayısı + Kar filtresi
        # print("\n\n3.3. Sorgu 3: COKLU KOSUL (Islem sayisi + NetProf filtresi)")
        # print("-" * 80)
        #
        # min_islem = 1000
        # min_netprof = 500000
        #
        # sql_3 = f"""
        # SELECT *
        # FROM df
        # WHERE OR_TotTrade >= {min_islem}
        #   AND OR_NetProf >= {min_netprof}
        # ORDER BY OR_NetProf DESC
        # LIMIT 15
        # """
        #
        # result_3 = sqldf(sql_3)
        # print(f"Sonuc: OR_TotTrade >= {min_islem:,} VE OR_NetProf >= {min_netprof:,} olan {len(result_3)} kayit")
        # display_cols_3 = ['CombNo', 'period', 'OR_TotTrade', 'OR_NetProf', 'OR_WinRate', 'OR_ProfFact']
        # print(result_3[display_cols_3].head(15))
        #
        # # SORGU 4: Min/Max kar kriterleri
        # print("\n\n3.4. Sorgu 4: MIN/MAX KAR KRITERLERI")
        # print("-" * 80)
        #
        # min_maxkar = 500000  # Maksimum kar en az bu kadar olmalı
        # max_maxzar = -300000  # Maksimum zarar bu değerden büyük olmalı (daha az zarar)
        #
        # sql_4 = f"""
        # SELECT *
        # FROM df
        # WHERE OR_MaxKarFy >= {min_maxkar}
        #   AND OR_MaxZarFy >= {max_maxzar}
        # ORDER BY OR_MaxKarFy DESC
        # LIMIT 10
        # """
        #
        # result_4 = sqldf(sql_4)
        # print(f"Sonuc: MaxKar >= {min_maxkar:,} VE MaxZarar >= {max_maxzar:,} olan {len(result_4)} kayit")
        # display_cols_4 = ['CombNo', 'period', 'OR_MaxKarFy', 'OR_MaxZarFy', 'OR_NetProf', 'OR_ProfFact']
        # print(result_4[display_cols_4].head(10))
        #
        # # SORGU 5: Kazanan/Kaybeden oran analizi
        # print("\n\n3.5. Sorgu 5: KAZANAN/KAYBEDEN ORAN ANALIZI")
        # print("-" * 80)
        #
        # min_kazand = 100
        # min_kar_oran = 0.4  # Kazanan/Toplam işlem oranı
        #
        # sql_5 = f"""
        # SELECT *,
        #        (CAST(OR_Kazand AS FLOAT) / CAST(OR_Islem AS FLOAT)) as KazananOran
        # FROM df
        # WHERE OR_Kazand >= {min_kazand}
        #   AND OR_Islem > 0
        # ORDER BY KazananOran DESC
        # LIMIT 10
        # """
        #
        # result_5 = sqldf(sql_5)
        # print(f"Sonuc: OR_Kazand >= {min_kazand} olan {len(result_5)} kayit")
        # display_cols_5 = ['CombNo', 'period', 'OR_Islem', 'OR_Kazand', 'KazananOran', 'OR_NetProf']
        # print(result_5[display_cols_5].head(10))
        #
        # # SORGU 6: Kompleks - Tüm kriterleri birleştir
        # print("\n\n3.6. Sorgu 6: KOMPLEKS - TUM KRITERLERI BIRLESTIR")
        # print("-" * 80)
        #
        # sql_6 = f"""
        # SELECT *,
        #        (CAST(OR_Kazand AS FLOAT) / CAST(OR_Islem AS FLOAT)) as KazananOran,
        #        (OR_NetProf / OR_MaxDD) as RiskReward
        # FROM df
        # WHERE OR_TotTrade >= 500
        #   AND OR_NetProf >= 1000000
        #   AND OR_ProfFact >= 1.2
        #   AND OR_MaxDD > 0
        # ORDER BY RiskReward DESC
        # LIMIT 20
        # """
        #
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

            # Orijinal plot_getfyt_percent metodu
            # viz.plot_getfyt_percent(show=True, save=True)

            # # Diğer hazır metodlar
            # viz.plot_net_profit(show=True, save=True)
            # viz.plot_win_rate(show=True, save=True)
            # viz.plot_total_trades(show=True, save=True)
            #
            # # Özel parametrelerle plot_custom
            # viz.plot_custom(
            #     x='CombNo',
            #     y='OR_NetProf',
            #     color='period',
            #     size='OR_TotTrade',
            #     hover_cols=['period', 'percent', 'OR_WinRate']
            # )
            #
            # # Çoklu metrik plot_multiple
            # viz.plot_multiple(
            #     y_cols=['OR_GetFyt%', 'OR_GetFy%N', 'OR_NetProf', 'OR_WinRate'],
            #     x_col='CombNo',
            #     color_col='period'
            # )
            #
            # # OR_GetFyt% analizleri - X ekseninde OR_GetFyt% kullanarak ilişki analizi
            #
            # # 1. OR_GetFyt% vs OR_NetProf - En önemli ilişki!
            # print("\n[1] OR_GetFyt% vs OR_NetProf ilişkisi...")
            # viz.plot_custom(
            #     x='OR_GetFyt%',
            #     y='OR_NetProf',
            #     color='period',
            #     size='OR_TotTrade',
            #     title='Getiri Yüzdesi vs Net Kar İlişkisi',
            #     hover_cols=['CombNo', 'period', 'percent', 'OR_GetFyt%', 'OR_NetProf',
            #                'OR_WinRate', 'OR_TotTrade', 'OR_ProfFact'],
            #     show=True,
            #     save=True
            # )
            #
            # # 2. OR_GetFyt% vs OR_WinRate
            # print("\n[2] OR_GetFyt% vs OR_WinRate ilişkisi...")
            # viz.plot_custom(
            #     x='OR_GetFyt%',
            #     y='OR_WinRate',
            #     color='OR_ProfFact',
            #     size='OR_TotTrade',
            #     title='Getiri Yüzdesi vs Kazanma Oranı İlişkisi',
            #     hover_cols=['CombNo', 'period', 'OR_GetFyt%', 'OR_WinRate',
            #                'OR_ProfFact', 'OR_NetProf'],
            #     show=True,
            #     save=True
            # )
            #
            # # 3. OR_GetFyt% vs OR_TotTrade
            # print("\n[3] OR_GetFyt% vs OR_TotTrade ilişkisi...")
            # viz.plot_custom(
            #     x='OR_GetFyt%',
            #     y='OR_TotTrade',
            #     color='period',
            #     size='OR_NetProf',
            #     title='Getiri Yüzdesi vs İşlem Sayısı İlişkisi',
            #     hover_cols=['CombNo', 'period', 'OR_GetFyt%', 'OR_TotTrade',
            #                'OR_NetProf', 'OR_WinRate'],
            #     show=True,
            #     save=True
            # )
            #
            # # 4. OR_GetFyt% vs OR_MaxDD (Risk-Getiri analizi)
            # print("\n[4] OR_GetFyt% vs OR_MaxDD (Risk-Getiri) ilişkisi...")
            # viz.plot_custom(
            #     x='OR_GetFyt%',
            #     y='OR_MaxDD',
            #     color='OR_NetProf',
            #     size='OR_TotTrade',
            #     title='Getiri Yüzdesi vs Max Drawdown (Risk) İlişkisi',
            #     hover_cols=['CombNo', 'period', 'OR_GetFyt%', 'OR_MaxDD',
            #                'OR_NetProf', 'OR_WinRate'],
            #     show=True,
            #     save=True
            # )
            # 5. OR_GetFyt% vs period (size parametresi YOK - sabit boyut)
            # print("\n[5] OR_GetFyt% vs period ilişkisi...")
            # viz.plot_custom(
            #     x='OR_GetFyt%',
            #     y='period',
            #     color='OR_NetProf',
            #     size=None,  # Sabit nokta boyutu
            #     title='Getiri Yüzdesi vs Period İlişkisi',
            #     hover_cols=['CombNo', 'period', 'percent', 'OR_GetFyt%',
            #                'OR_NetProf', 'OR_WinRate', 'OR_TotTrade'],
            #     show=True,
            #     save=True
            # )
            #
            # # 6. OR_GetFyt% vs percent (size parametresi YOK - sabit boyut)
            # print("\n[6] OR_GetFyt% vs percent ilişkisi...")
            # viz.plot_custom(
            #     x='OR_GetFyt%',
            #     y='percent',
            #     color='period',
            #     size=None,  # Sabit nokta boyutu
            #     title='Getiri Yüzdesi vs Percent İlişkisi',
            #     hover_cols=['CombNo', 'period', 'percent', 'OR_GetFyt%',
            #                'OR_NetProf', 'OR_WinRate', 'OR_TotTrade'],
            #     show=True,
            #     save=True
            # )
            #
            # # 7. COMBINED: OR_GetFyt% vs Period & Percent (Tek grafikte!)
            # print("\n[7] OR_GetFyt% vs Period & Percent (Combined)...")
            # viz.plot_period_percent_combined(show=True, save=True)

            # 8. ESNEK X-Y-Z PLOT - İstediğiniz kombinasyonlar
            print("\n[8] Esnek X-Y-Z Plotlar...")

            # 8.1: OR_GetFyt% (x), period (y), percent (renk)
            print("\n[8.1] X=OR_GetFyt%, Y=period, Color=percent")
            viz.plot_x_y_z(
                x='OR_GetFyt%',
                y='period',
                z='percent',
                title='Getiri % vs Period (Percent ile renkli)',
                size_ref='OR_GetFyt%',
                show=True,
                save=True
            )

            # 8.2: OR_GetFyt (x), period (y), percent (renk)
            print("\n[8.2] X=OR_GetFiyat, Y=period, Color=percent")
            viz.plot_x_y_z(
                x='OR_GetFiyat',
                y='period',
                z='percent',
                title='Getiri  vs Period (Percent ile renkli)',
                size_ref='OR_GetFiyat',
                show=True,
                save=True
            )


            # 8.3: OR_GetFyt (x), period (y), percent (renk)
            print("\n[8.3] X=OR_GetFyNet, Y=CombNo, Color=OR_KomFiyat")
            viz.plot_x_y_z(
                x='OR_GetFyNet',
                y='OR_Islem',
                z='OR_KomFiyat',
                title='Getiri  vs Period (Percent ile renkli)',
                size_ref='OR_GetFyNet',
                show=True,
                save=True
            )


            # 8.3: OR_GetFyt (x), period (y), percent (renk)
            print("\n[8.3] X=OR_GetFyNet, Y=CombNo, Color=OR_KomFiyat")
            viz.plot_x_y_z(
                x='CombNo',
                y='OR_GetFyNet',
                z='OR_KomFiyat',
                title='Getiri  vs Period (Percent ile renkli)',
                size_ref='OR_GetFyNet',
                show=True,
                save=True
            )







#         print("\n" + "=" * 80)
#         print("SQL SORGU SABLONLARI - Kendi sorgulariniz icin:")
#         print("=" * 80)
#
#         print("""
# # SABLON 1: Siralama
# sql = '''
# SELECT * FROM df
# ORDER BY SutunAdi DESC
# LIMIT 10
# '''
#
# # SABLON 2: Filtreleme + Siralama
# sql = '''
# SELECT * FROM df
# WHERE Sutun1 >= Deger1
#   AND Sutun2 BETWEEN Deger2 AND Deger3
# ORDER BY Sutun1 DESC
# LIMIT 20
# '''
#
# # SABLON 3: Hesaplanmis sütun ekleme
# sql = '''
# SELECT *,
#        (Sutun1 / Sutun2) as YeniSutun
# FROM df
# WHERE Sutun1 > 0 AND Sutun2 > 0
# ORDER BY YeniSutun DESC
# '''
#
# # SABLON 4: Gruplama ve Agregasyon
# sql = '''
# SELECT period,
#        COUNT(*) as Sayi,
#        AVG(OR_NetProf) as OrtalamaKar,
#        MAX(OR_WinRate) as MaxWinRate
# FROM df
# GROUP BY period
# ORDER BY OrtalamaKar DESC
# '''
#
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
    main()

    # Gelişmiş örnekler için yorum satırını kaldırın
    # advanced_examples()
