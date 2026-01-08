"""
Optimization Log Analyzer
Optimizasyon log dosyalarını analiz etmek için kullanılan sınıf.
CSV ve TXT formatlarını destekler.
"""

import pandas as pd
from typing import Optional, List, Union, Dict, Any
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


class OptLogAnalyzer:
    """
    SingleTrader optimizasyon log dosyalarını analiz eden sınıf.

    Özellikler:
    - CSV/TXT dosya okuma
    - Pandas DataFrame ile veri yönetimi
    - SQL benzeri sorgulama (pandasql kullanarak)
    - Filtreleme ve gruplama
    - İstatistiksel analizler
    """

    def __init__(self, file_path: Optional[str] = None, separator: str = ';', encoding: str = 'utf-8-sig'):
        """
        OptLogAnalyzer başlatıcı

        Args:
            file_path: Okunacak dosyanın yolu
            separator: CSV ayırıcı karakter (varsayılan: ';')
            encoding: Dosya encoding (varsayılan: 'utf-8-sig' - BOM karakterini otomatik kaldırır)
        """
        self.file_path = file_path
        self.separator = separator
        self.encoding = encoding
        self.df: Optional[pd.DataFrame] = None
        self.original_df: Optional[pd.DataFrame] = None

        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str) -> pd.DataFrame:
        """
        CSV veya TXT dosyasını yükler

        Args:
            file_path: Dosya yolu

        Returns:
            Yüklenen DataFrame
        """
        self.file_path = file_path
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")

        try:
            # CSV dosyasını basitçe oku
            self.df = pd.read_csv(
                file_path,
                sep=self.separator,
                encoding=self.encoding,
                low_memory=False,
                index_col=False
            )

            # Virgüllü sayıları düzelt (Türk formatı)
            self._fix_numeric_columns()

            # Orijinal kopyasını sakla
            self.original_df = self.df.copy()

            print(f"[OK] Dosya basariyla yuklendi: {path.name}")
            print(f"  Satir sayisi: {len(self.df):,}")
            print(f"  Sutun sayisi: {len(self.df.columns)}")

            return self.df

        except Exception as e:
            raise Exception(f"Dosya okunurken hata: {str(e)}")

    def _fix_numeric_columns(self) -> None:
        """
        Virgüllü (Türk formatı) sayıları düzeltir.
        String olarak okunan numeric kolonları float'a çevirir.
        """
        for col in self.df.columns:
            # Eğer sütun object (string) tipindeyse
            if self.df[col].dtype == 'object':
                # İlk birkaç değere bak, sayı formatı gibi mi?
                sample = self.df[col].dropna().head(10).astype(str)

                # Virgüllü sayı formatını kontrol et
                is_numeric = sample.str.match(r'^-?\d+[\.,]?\d*$').any()

                if is_numeric:
                    try:
                        # Virgülü noktaya çevir ve float'a dönüştür
                        self.df[col] = (self.df[col]
                                        .astype(str)
                                        .str.replace(',', '.')
                                        .str.replace('nan', '')
                                        .replace('', None))
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                    except:
                        pass  # Dönüştürülemezse olduğu gibi bırak

    def info(self) -> None:
        """DataFrame hakkında genel bilgi gösterir"""
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return

        print(f"\n{'='*60}")
        print(f"Veri Seti Bilgileri")
        print(f"{'='*60}")
        print(f"Satır sayısı     : {len(self.df):,}")
        print(f"Sütun sayısı     : {len(self.df.columns)}")
        print(f"Bellek kullanımı : {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print(f"{'='*60}\n")

    def columns(self) -> List[str]:
        """Tüm sütun isimlerini döndürür"""
        if self.df is None:
            return []
        return self.df.columns.tolist()

    def head(self, n: int = 5) -> pd.DataFrame:
        """İlk n satırı gösterir"""
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return pd.DataFrame()
        return self.df.head(n)

    def tail(self, n: int = 5) -> pd.DataFrame:
        """Son n satırı gösterir"""
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return pd.DataFrame()
        return self.df.tail(n)

    def describe(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        İstatistiksel özet bilgileri gösterir

        Args:
            columns: İncelenecek sütunlar (None ise tüm numerik sütunlar)
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return pd.DataFrame()

        if columns:
            return self.df[columns].describe()
        return self.df.describe()

    def select(self, columns: Union[str, List[str]]) -> pd.DataFrame:
        """
        SQL SELECT benzeri: Belirli sütunları seçer

        Args:
            columns: Sütun adı veya sütun listesi

        Returns:
            Seçilen sütunları içeren DataFrame
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return pd.DataFrame()

        if isinstance(columns, str):
            columns = [columns]

        return self.df[columns]

    def where(self, condition: str) -> pd.DataFrame:
        """
        SQL WHERE benzeri: Koşula göre filtreleme

        Args:
            condition: Pandas query formatında koşul
                      Örnek: "OR_NetProf > 1000 and OR_WinRate > 50"

        Returns:
            Filtrelenmiş DataFrame
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return pd.DataFrame()

        try:
            return self.df.query(condition)
        except Exception as e:
            print(f"[!] Sorgu hatası: {str(e)}")
            return pd.DataFrame()

    def order_by(self, columns: Union[str, List[str]], ascending: Union[bool, List[bool]] = True) -> pd.DataFrame:
        """
        SQL ORDER BY benzeri: Sıralama

        Args:
            columns: Sıralama için sütun(lar)
            ascending: Artan sıralama (True) veya azalan (False)

        Returns:
            Sıralanmış DataFrame
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return pd.DataFrame()

        if isinstance(columns, str):
            columns = [columns]

        return self.df.sort_values(by=columns, ascending=ascending)

    def group_by(self, columns: Union[str, List[str]]) -> pd.core.groupby.DataFrameGroupBy:
        """
        SQL GROUP BY benzeri: Gruplama

        Args:
            columns: Gruplama için sütun(lar)

        Returns:
            GroupBy nesnesi
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return None

        if isinstance(columns, str):
            columns = [columns]

        return self.df.groupby(columns)

    def filter(self, **kwargs) -> pd.DataFrame:
        """
        Basit filtreleme: Kolon=Değer şeklinde filtreleme

        Args:
            **kwargs: Kolon adı ve değer çiftleri

        Örnek:
            analyzer.filter(period=5, percent=0.5)

        Returns:
            Filtrelenmiş DataFrame
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return pd.DataFrame()

        result = self.df.copy()
        for col, value in kwargs.items():
            if col in result.columns:
                result = result[result[col] == value]
            else:
                print(f"[!] Sütun bulunamadı: {col}")

        return result

    def top(self, n: int, sort_by: str, ascending: bool = False) -> pd.DataFrame:
        """
        En iyi/en kötü n kaydı getir

        Args:
            n: Kayıt sayısı
            sort_by: Sıralama sütunu
            ascending: True ise en düşük, False ise en yüksek

        Returns:
            Top n DataFrame
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return pd.DataFrame()

        return self.df.nlargest(n, sort_by) if not ascending else self.df.nsmallest(n, sort_by)

    def search(self, column: str, value: Any, exact: bool = False) -> pd.DataFrame:
        """
        Belirli bir sütunda değer arama

        Args:
            column: Aranacak sütun
            value: Aranacak değer
            exact: True ise tam eşleşme, False ise içeren

        Returns:
            Bulunan kayıtlar
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return pd.DataFrame()

        if column not in self.df.columns:
            print(f"[!] Sütun bulunamadı: {column}")
            return pd.DataFrame()

        if exact:
            return self.df[self.df[column] == value]
        else:
            return self.df[self.df[column].astype(str).str.contains(str(value), case=False, na=False)]

    def reset(self) -> None:
        """DataFrame'i orijinal haline döndürür"""
        if self.original_df is not None:
            self.df = self.original_df.copy()
            print("[OK] Veri seti orijinal haline döndürüldü")
        else:
            print("[!] Orijinal veri bulunamadı!")

    def save(self, output_path: str, index: bool = False, format: str = 'csv') -> None:
        """
        Mevcut DataFrame'i dosyaya kaydeder

        Args:
            output_path: Çıktı dosyası yolu
            index: Index'i de kaydet mi?
            format: Dosya formatı ('csv' veya 'txt')
                    'csv': CSV formatında (virgülle ayrılmış)
                    'txt': Tabular format (düzgün hizalanmış tablo)
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return

        try:
            if format.lower() == 'csv':
                self.df.to_csv(output_path, sep=self.separator, index=index, encoding=self.encoding)
            elif format.lower() == 'txt':
                self.save_as_table(output_path, index=index)
            else:
                print(f"[!] Geçersiz format: {format}. 'csv' veya 'txt' kullanın.")
                return

            print(f"[OK] Dosya kaydedildi: {output_path}")
        except Exception as e:
            print(f"[!] Kaydetme hatası: {str(e)}")

    def save_csv(self, output_path: str, index: bool = False, separator: str = None) -> None:
        """
        DataFrame'i CSV formatında kaydeder

        Args:
            output_path: Çıktı dosyası yolu
            index: Index'i de kaydet mi?
            separator: Ayırıcı karakter (None ise varsayılan separator kullanılır)
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return

        sep = separator if separator else self.separator
        try:
            self.df.to_csv(output_path, sep=sep, index=index, encoding=self.encoding)
            print(f"[OK] CSV dosyasi kaydedildi: {output_path}")
        except Exception as e:
            print(f"[!] Kaydetme hatasi: {str(e)}")

    def save_as_table(self, output_path: str, index: bool = False,
                      col_width: int = 25, col_space: int = 3,
                      max_col_width: int = None, use_custom_format: bool = True) -> None:
        """
        DataFrame'i düzgün hizalanmış tablo formatında TXT olarak kaydeder

        Args:
            output_path: Çıktı dosyası yolu
            index: Index'i de kaydet mi?
            col_width: Tüm sütunlar için varsayılan genişlik (karakter sayısı)
            col_space: Sütunlar arası boşluk sayısı (karakter)
            max_col_width: Maksimum sütun genişliği (None ise col_width kullanılır)
            use_custom_format: True ise manuel formatting, False ise pandas default

        Örnek:
            # Geniş sütunlar, bol boşluk
            analyzer.save_as_table('output.txt', col_width=30, col_space=5)

            # Dar sütunlar, az boşluk
            analyzer.save_as_table('output.txt', col_width=15, col_space=2)

            # Pandas default formatting
            analyzer.save_as_table('output.txt', use_custom_format=False)
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return

        try:
            if use_custom_format:
                # Manuel formatting - sabit genişlikte sütunlar
                self._save_table_custom_format(output_path, index, col_width, col_space)
            else:
                # Pandas default formatting
                with open(output_path, 'w', encoding=self.encoding) as f:
                    table_str = self.df.to_string(
                        index=index,
                        max_colwidth=max_col_width or col_width,
                        col_space=col_space,
                        justify='right',
                        min_rows=None
                    )
                    f.write(table_str)

            print(f"[OK] Tabular TXT dosyasi kaydedildi: {output_path}")
            print(f"    Sutun genisligi: {col_width}, Sutun arasi bosluk: {col_space}")
        except Exception as e:
            print(f"[!] Kaydetme hatasi: {str(e)}")

    def _save_table_custom_format(self, output_path: str, index: bool,
                                   col_width: int, col_space: int) -> None:
        """
        Manuel olarak formatlanmış tablo oluşturur (sabit genişlikte sütunlar)
        """
        separator = ' ' * col_space

        with open(output_path, 'w', encoding=self.encoding) as f:
            # Header satırı
            if index:
                header_parts = ['Index'.rjust(col_width)]
            else:
                header_parts = []

            for col in self.df.columns:
                # Sütun adını kısalt ve hizala
                col_str = str(col)
                if len(col_str) > col_width:
                    col_str = col_str[:col_width-3] + '...'
                header_parts.append(col_str.rjust(col_width))

            f.write(separator.join(header_parts) + '\n')

            # Ayırıcı çizgi
            sep_line = separator.join(['-' * col_width for _ in range(len(header_parts))])
            f.write(sep_line + '\n')

            # Data satırları
            for idx, row in self.df.iterrows():
                row_parts = []

                if index:
                    idx_str = str(idx)
                    if len(idx_str) > col_width:
                        idx_str = idx_str[:col_width-3] + '...'
                    row_parts.append(idx_str.rjust(col_width))

                for val in row:
                    val_str = str(val) if pd.notna(val) else ''
                    if len(val_str) > col_width:
                        val_str = val_str[:col_width-3] + '...'
                    row_parts.append(val_str.rjust(col_width))

                f.write(separator.join(row_parts) + '\n')

    def save_both(self, base_path: str, index: bool = False,
                  col_width: int = 25, col_space: int = 3) -> None:
        """
        Hem CSV hem de tabular TXT formatında kaydeder

        Args:
            base_path: Temel dosya yolu (uzantısız)
            index: Index'i de kaydet mi?
            col_width: TXT dosyası için sütun genişliği
            col_space: TXT dosyası için sütunlar arası boşluk

        Örnek:
            analyzer.save_both('results/optimized_data')
            # Şu dosyaları oluşturur:
            # - results/optimized_data.csv
            # - results/optimized_data.txt

            # Özel formatla
            analyzer.save_both('results/data', col_width=30, col_space=5)
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return

        # Uzantıyı kaldır
        if base_path.endswith('.csv') or base_path.endswith('.txt'):
            base_path = base_path.rsplit('.', 1)[0]

        csv_path = f"{base_path}.csv"
        txt_path = f"{base_path}.txt"

        self.save_csv(csv_path, index=index)
        self.save_as_table(txt_path, index=index, col_width=col_width, col_space=col_space)

    def query_sql(self, sql_query: str) -> pd.DataFrame:
        """
        SQL sorgusu çalıştır (pandasql gerektirir)

        NOT: Bu metodu kullanmak için 'pandasql' kütüphanesi gereklidir:
        pip install pandasql

        Args:
            sql_query: SQL sorgusu (FROM self.df kullanın)

        Returns:
            Sorgu sonucu DataFrame
        """
        try:
            from pandasql import sqldf

            # pandasql için yerel fonksiyon
            pysqldf = lambda q: sqldf(q, {'df': self.df})

            # SQL sorgusunda "FROM df" kullanımını destekle
            result = pysqldf(sql_query)
            return result

        except ImportError:
            print("[!] 'pandasql' kütüphanesi yüklü değil!")
            print("  Yüklemek için: pip install pandasql")
            return pd.DataFrame()
        except Exception as e:
            print(f"[!] SQL sorgu hatası: {str(e)}")
            return pd.DataFrame()

    def get_statistics(self, column: str) -> Dict[str, float]:
        """
        Bir sütun için detaylı istatistikler

        Args:
            column: Sütun adı

        Returns:
            İstatistik bilgileri dictionary
        """
        if self.df is None or column not in self.df.columns:
            return {}

        col_data = self.df[column]

        if pd.api.types.is_numeric_dtype(col_data):
            return {
                'count': col_data.count(),
                'mean': col_data.mean(),
                'std': col_data.std(),
                'min': col_data.min(),
                'max': col_data.max(),
                'median': col_data.median(),
                '25%': col_data.quantile(0.25),
                '75%': col_data.quantile(0.75),
            }
        else:
            return {
                'count': col_data.count(),
                'unique': col_data.nunique(),
                'top': col_data.mode()[0] if not col_data.mode().empty else None,
                'freq': col_data.value_counts().iloc[0] if len(col_data.value_counts()) > 0 else 0
            }

    def reorder_columns(self, columns: Union[List[int], List[str]], append_remaining: bool = True) -> pd.DataFrame:
        """
        Sütunların sırasını değiştirir

        Args:
            columns: Sütun index'leri (int) veya sütun isimleri (str) listesi
                     Örnek: [0, 3, 5, 1] veya ['CombNo', 'OR_NetProf', 'period']
            append_remaining: True ise geri kalan sütunları sonuna ekler, False ise sadece belirtilen sütunları gösterir

        Returns:
            Yeniden sıralanmış DataFrame

        Örnek kullanım:
            # Index ile
            analyzer.reorder_columns([0, 2, 5, 10, 1])

            # İsim ile
            analyzer.reorder_columns(['CombNo', 'period', 'OR_NetProf', 'OR_WinRate'])

            # Sadece belirli sütunlar
            analyzer.reorder_columns([1, 3, 5], append_remaining=False)
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return pd.DataFrame()

        all_cols = self.df.columns.tolist()

        # Eğer int index'lerse, sütun isimlerine çevir
        if columns and isinstance(columns[0], int):
            selected_cols = [all_cols[i] for i in columns if 0 <= i < len(all_cols)]
        else:
            selected_cols = [col for col in columns if col in all_cols]

        if not selected_cols:
            print("[!] Geçerli sütun bulunamadı!")
            return self.df

        # Geri kalan sütunları ekle
        if append_remaining:
            remaining_cols = [col for col in all_cols if col not in selected_cols]
            new_order = selected_cols + remaining_cols
        else:
            new_order = selected_cols

        # DataFrame'i yeniden sırala
        self.df = self.df[new_order]
        return self.df

    def move_columns_to_front(self, columns: Union[List[int], List[str]]) -> pd.DataFrame:
        """
        Belirtilen sütunları en başa taşır (kısayol metod)

        Args:
            columns: Sütun index'leri veya isimleri

        Returns:
            Yeniden sıralanmış DataFrame
        """
        return self.reorder_columns(columns, append_remaining=True)

    def select_and_reorder(self, columns: Union[List[int], List[str]]) -> pd.DataFrame:
        """
        Sadece belirtilen sütunları seçer ve o sırada gösterir (kısayol metod)

        Args:
            columns: Sütun index'leri veya isimleri

        Returns:
            Seçilmiş ve sıralanmış DataFrame
        """
        return self.reorder_columns(columns, append_remaining=False)

    def __repr__(self) -> str:
        """String gösterimi"""
        if self.df is None:
            return "OptLogAnalyzer(no data loaded)"
        return f"OptLogAnalyzer(rows={len(self.df):,}, cols={len(self.df.columns)})"

    def __len__(self) -> int:
        """Satır sayısı"""
        return len(self.df) if self.df is not None else 0
