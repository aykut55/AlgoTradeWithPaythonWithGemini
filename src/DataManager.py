import os
import sys
import time
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Tuple, List, Dict, Any, TypeAlias

class BarData:
    """Tek bir bar (mum) verisini temsil eder"""
    def __init__(self, id: int, date: str, time: str, open: float, high: float,
                 low: float, close: float, volume: int, lot: int):
        self.id = id
        self.date = date
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.lot = lot
        self.delta = close - open
        self.delta_pct = (close - open) / open * 100 if open != 0 else 0
        self.dateTime = f"{self.date} {self.time}"
        dt = datetime.strptime(self.dateTime, "%Y.%m.%d %H:%M:%S")
        self.epochTime = int(dt.timestamp())

    def __repr__(self):
        return (
            f"Bar(Id:{self.id}, DateTime:{self.date} {self.time}, Epoch:{self.epochTime}, "
            f"O:{self.open:.2f}, H:{self.high:.2f}, L:{self.low:.2f}, C:{self.close:.2f}, "
            f"V:{self.volume}, Lot:{self.lot}, "
            f"D:{self.delta:.2f}, D%:{self.delta_pct:.2f}) "
        )

    def to_dict(self):
        """BarData nesnesini dict olarak döndürür"""
        return {
            "id": self.id,
            "date": self.date,
            "time": self.time,
            "dateTime": self.dateTime,
            "epochTime": self.epochTime,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "lot": self.lot,
            "delta": self.delta,
            "delta_pct": self.delta_pct,
        }

    def to_json(self, indent=None):
        """BarData nesnesini JSON string olarak döndürür"""
        return json.dumps(self.to_dict(), indent=indent)

    def to_dataframe(self):
        """BarData nesnesini tek satırlık pandas DataFrame'e dönüştürür"""
        return pd.DataFrame([self.to_dict()])

    def to_csv_line(self, sep=",", quote=False, none_as_empty=True):
        """BarData nesnesini tam parametrik CSV satırına dönüştürür."""

        def fmt(value):
            # None handling
            if value is None:
                return "" if none_as_empty else "None"

            # String ise quote uygulanabilir
            if isinstance(value, str):
                return f'"{value}"' if quote else value

            # float -> normal çevir
            return str(value)

        fields = [
            fmt(self.id),
            fmt(self.date),
            fmt(self.time),
            fmt(self.dateTime),
            fmt(self.epochTime),
            fmt(self.open),
            fmt(self.high),
            fmt(self.low),
            fmt(self.close),
            fmt(self.volume),
            fmt(self.lot),
            fmt(f"{self.delta:.2f}"),
            fmt(f"{self.delta_pct:.2f}")
        ]

        return sep.join(fields)

    @staticmethod
    def from_dict(d: dict):
        return BarData(
            d["id"],
            d["date"],
            d["time"],
            d["open"],
            d["high"],
            d["low"],
            d["close"],
            d["volume"],
            d["lot"]
        )

    @staticmethod
    def from_json(json_str: str):
        d = json.loads(json_str)
        return BarData.from_dict(d)

    @staticmethod
    def from_dataframe(df: pd.DataFrame):
        """DataFrame → BarData listesi dönüştürücü"""
        bars = []
        for _, row in df.iterrows():
            bars.append(
                BarData(
                    int(row["id"]),
                    str(row["date"]),
                    str(row["time"]),
                    float(row["open"]),
                    float(row["high"]),
                    float(row["low"]),
                    float(row["close"]),
                    int(row["volume"]),
                    int(row["lot"]),
                )
            )
        return bars

    @staticmethod
    def from_csv_line(line: str, sep=","):
        """CSV satırından BarData nesnesi oluşturur."""
        parts = [p.strip().strip('"') for p in line.split(sep)]

        return BarData(
            int(parts[0]),      # id
            parts[1],           # date
            parts[2],           # time
            float(parts[5]),    # open
            float(parts[6]),    # high
            float(parts[7]),    # low
            float(parts[8]),    # close
            int(parts[9]),      # volume
            int(parts[10]),     # lot
        )

class CSVBarDataReader:
    """VIP CSV dosyalarını okur"""

    def __init__(self, file_path = ""):
        self.file_path = file_path
        self.metadata: Dict[str, str] = {}
        self.bars: List[BarData] = []

        # Cached arrays
        self.open_data = np.array([], dtype=np.float64)
        self.high_data = np.array([], dtype=np.float64)
        self.low_data = np.array([], dtype=np.float64)
        self.close_data = np.array([], dtype=np.float64)
        self.volume_data: np.ndarray = np.array([], dtype=np.float64)
        self.lot_data: np.ndarray = np.array([], dtype=np.float64)

        self.epoch_data = np.array([], dtype=np.float64)
        self.date_time_data_str = np.array([], dtype=object)  # string array
        self.date_data_str = np.array([], dtype=object)  # string array
        self.time_data_str = np.array([], dtype=object)  # string array

        self.delta: np.ndarray = np.array([], dtype=np.float64)
        self.delta_pct: np.ndarray = np.array([], dtype=np.float64)

    def set_file_path(self, file_path: str):
        self.file_path = file_path

    def get_file_path(self) -> str:
        return self.file_path

    def _read_metadata_and_data_lines(self) -> tuple[int, List[str]]:
        """Metadata ve data satırlarını okur (ortak metod)"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Metadata'yı oku
        data_start_index = 0
        for i, line in enumerate(lines):
            line = line.strip()

            if line == "# Data":
                data_start_index = i + 1
                break

            if line.startswith('#') and ':' in line:
                key_value = line[1:].strip()
                if ':' in key_value:
                    key, value = key_value.split(':', 1)
                    self.metadata[key.strip()] = value.strip()

        # Tüm data satırlarını topla
        all_data_lines = []
        for line in lines[data_start_index:]:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            all_data_lines.append(line)

        return len(all_data_lines), all_data_lines

    def _parse_data_lines(self, lines: List[str]) -> None:
        """Data satırlarını parse edip bar listesine ekler"""
        self.bars.clear()
        for line in lines:
            parts = line.split(';')
            if len(parts) == 9:
                bar = BarData(
                    id=int(parts[0]),
                    date=parts[1],
                    time=parts[2],
                    open=float(parts[3]),
                    high=float(parts[4]),
                    low=float(parts[5]),
                    close=float(parts[6]),
                    volume=int(parts[7]),
                    lot=int(parts[8])
                )
                self.bars.append(bar)

        # Update cached arrays for quick access
        if len(self.bars) > 0:
            self.volume_data = np.array([b.volume for b in self.bars], dtype=np.float64)
            self.lot_data = np.array([b.lot for b in self.bars], dtype=np.float64)
        else:
            self.volume_data = np.array([], dtype=np.float64)
            self.lot_data = np.array([], dtype=np.float64)

        if len(self.bars) > 0:
            self.open_data = np.array([b.open for b in self.bars], dtype=np.float64)
            self.high_data = np.array([b.high for b in self.bars], dtype=np.float64)
            self.low_data = np.array([b.low for b in self.bars], dtype=np.float64)
            self.close_data = np.array([b.close for b in self.bars], dtype=np.float64)

            self.date_data_str = np.array([b.date for b in self.bars], dtype=object)
            self.time_data_str = np.array([b.time for b in self.bars], dtype=object)
            self.date_time_data_str = np.array([b.dateTime for b in self.bars], dtype=object)

            self.epoch_data = np.array([b.epochTime for b in self.bars], dtype=np.float64)
        else:
            self.open_data = np.array([], dtype=np.float64)
            self.high_data = np.array([], dtype=np.float64)
            self.low_data = np.array([], dtype=np.float64)
            self.close_data = np.array([], dtype=np.float64)

            self.date_data_str = np.array([], dtype=object)
            self.time_data_str = np.array([], dtype=object)
            self.date_time_data_str = np.array([], dtype=object)

            self.epoch_data = np.array([], dtype=np.float64)

        # Always compute delta arrays after parsing data
        self._compute_deltas()

    def _compute_deltas(self) -> None:
        """
        self.bars içindeki her bar için delta (close-open) ve
        delta_pct ((close-open)/open*100) hesaplar ve CSVReader seviyesinde
        numpy dizileri olarak `self.delta` ve `self.delta_pct` içine yazar.
        Ayrıca BarData örneklerindeki alanları da senkron tutar.
        """
        if len(self.bars) == 0:
            self.delta = np.array([], dtype=np.float64)
            self.delta_pct = np.array([], dtype=np.float64)
            return

        deltas = np.empty(len(self.bars), dtype=np.float64)
        delta_pcts = np.empty(len(self.bars), dtype=np.float64)

        for i, b in enumerate(self.bars):
            d = b.close - b.open
            pct = (d / b.open * 100.0) if b.open != 0 else 0.0
            deltas[i] = d
            delta_pcts[i] = pct
            # Keep BarData fields in sync
            b.delta = d
            b.delta_pct = pct

        self.delta = deltas
        self.delta_pct = delta_pcts

    def read_file_full_data(self) -> bool:
        """Tüm veriyi okur"""
        try:
            print("Tüm veri okunuyor...")
            total_bars, all_data_lines = self._read_metadata_and_data_lines()
            print(f"Toplam {total_bars} bar bulundu.")

            self._parse_data_lines(all_data_lines)

            print(f"✓ {len(self.bars)} bar başarıyla yüklendi!")
            return True
        except Exception as e:
            print(f"Hata: Dosya okunurken hata oluştu: {e}")
            return False

    def read_file_last_n_data(self, n: int = 1000) -> bool:
        """Son N adet barı okur"""
        try:
            print(f"Son {n} bar okunuyor...")
            total_bars, all_data_lines = self._read_metadata_and_data_lines()
            print(f"Toplam {total_bars} bar bulundu.")

            selected_lines = all_data_lines[-n:] if n < total_bars else all_data_lines
            self._parse_data_lines(selected_lines)

            print(f"✓ {len(self.bars)} bar başarıyla yüklendi!")
            return True
        except Exception as e:
            print(f"Hata: Dosya okunurken hata oluştu: {e}")
            return False

    def read_file_first_n_data(self, n: int = 1000) -> bool:
        """İlk N adet barı okur"""
        try:
            print(f"İlk {n} bar okunuyor...")
            total_bars, all_data_lines = self._read_metadata_and_data_lines()
            print(f"Toplam {total_bars} bar bulundu.")

            selected_lines = all_data_lines[:n]
            self._parse_data_lines(selected_lines)

            print(f"✓ {len(self.bars)} bar başarıyla yüklendi!")
            return True
        except Exception as e:
            print(f"Hata: Dosya okunurken hata oluştu: {e}")
            return False

    def read_file_range_data(self, n1: int, n2: int) -> bool:
        """n1 ile n2 arasındaki barları okur (n1 dahil, n2 hariç)"""
        try:
            print(f"Bar aralığı {n1}-{n2} okunuyor...")
            total_bars, all_data_lines = self._read_metadata_and_data_lines()
            print(f"Toplam {total_bars} bar bulundu.")

            n1 = max(0, n1)
            n2 = min(total_bars, n2)

            selected_lines = all_data_lines[n1:n2]
            self._parse_data_lines(selected_lines)

            print(f"✓ {len(self.bars)} bar başarıyla yüklendi! (Index {n1}-{n2})")
            return True
        except Exception as e:
            print(f"Hata: Dosya okunurken hata oluştu: {e}")
            return False

    def read_file(self, *args) -> bool:
        """
        Esnek dosya okuma metodu.

        Kullanım:
        - read_file()           -> Tüm veriyi oku (read_file_full_data)
        - read_file(N)          -> Son N barı oku (read_file_last_n_data)
        - read_file(N1, N2)     -> N1-N2 aralığını oku (read_file_range_data)
        """
        if len(args) == 0:
            # Argüman yok -> tüm veriyi oku
            return self.read_file_full_data()
        elif len(args) == 1:
            # Bir argüman -> son N barı oku
            return self.read_file_last_n_data(args[0])
        elif len(args) == 2:
            # İki argüman -> range oku
            return self.read_file_range_data(args[0], args[1])
        else:
            print("Hata: read_file() en fazla 2 parametre alabilir!")
            return False

    def read_file_after_date(self, start_date: str) -> bool:
        """
        Belirli bir tarihten sonraki barları okur (start_date dahil)

        Args:
            start_date: Başlangıç tarihi (format: "YYYY.MM.DD" veya "YYYY.MM.DD HH:MM:SS")
        """
        try:
            print(f"{start_date} tarihinden sonraki barlar okunuyor...")
            total_bars, all_data_lines = self._read_metadata_and_data_lines()
            print(f"Toplam {total_bars} bar bulundu.")

            selected_lines = []
            for line in all_data_lines:
                parts = line.split(';')
                if len(parts) >= 3:
                    bar_datetime = f"{parts[1]} {parts[2]}"  # date + time
                    # Tarih karşılaştırması (string olarak)
                    if bar_datetime >= start_date:
                        selected_lines.append(line)

            self._parse_data_lines(selected_lines)
            print(f"✓ {len(self.bars)} bar başarıyla yüklendi! ({start_date} sonrası)")
            return True
        except Exception as e:
            print(f"Hata: Dosya okunurken hata oluştu: {e}")
            return False

    def read_file_before_date(self, end_date: str) -> bool:
        """
        Belirli bir tarihten önceki barları okur (end_date hariç)

        Args:
            end_date: Bitiş tarihi (format: "YYYY.MM.DD" veya "YYYY.MM.DD HH:MM:SS")
        """
        try:
            print(f"{end_date} tarihinden önceki barlar okunuyor...")
            total_bars, all_data_lines = self._read_metadata_and_data_lines()
            print(f"Toplam {total_bars} bar bulundu.")

            selected_lines = []
            for line in all_data_lines:
                parts = line.split(';')
                if len(parts) >= 3:
                    bar_datetime = f"{parts[1]} {parts[2]}"  # date + time
                    # Tarih karşılaştırması (string olarak)
                    if bar_datetime < end_date:
                        selected_lines.append(line)

            self._parse_data_lines(selected_lines)
            print(f"✓ {len(self.bars)} bar başarıyla yüklendi! ({end_date} öncesi)")
            return True
        except Exception as e:
            print(f"Hata: Dosya okunurken hata oluştu: {e}")
            return False

    def read_file_between_dates(self, start_date: str, end_date: str) -> bool:
        """
        İki tarih arasındaki barları okur (start_date dahil, end_date hariç)

        Args:
            start_date: Başlangıç tarihi (format: "YYYY.MM.DD" veya "YYYY.MM.DD HH:MM:SS")
            end_date: Bitiş tarihi (format: "YYYY.MM.DD" veya "YYYY.MM.DD HH:MM:SS")
        """
        try:
            print(f"{start_date} - {end_date} arasındaki barlar okunuyor...")
            total_bars, all_data_lines = self._read_metadata_and_data_lines()
            print(f"Toplam {total_bars} bar bulundu.")

            selected_lines = []
            for line in all_data_lines:
                parts = line.split(';')
                if len(parts) >= 3:
                    bar_datetime = f"{parts[1]} {parts[2]}"  # date + time
                    # Tarih aralığı kontrolü (string olarak)
                    if start_date <= bar_datetime < end_date:
                        selected_lines.append(line)

            self._parse_data_lines(selected_lines)
            print(f"✓ {len(self.bars)} bar başarıyla yüklendi! ({start_date} - {end_date})")
            return True
        except Exception as e:
            print(f"Hata: Dosya okunurken hata oluştu: {e}")
            return False

    def get_bar_count(self) -> int:
        """Toplam bar sayısını döndürür"""
        return len(self.bars)

    def get_metadata(self, key: str) -> str:
        """Belirtilen metadata değerini döndürür"""
        return self.metadata.get(key, "")

    def print_info(self):
        """Dosya bilgilerini yazdırır"""
        print("=" * 60)
        print("CSV Dosya Bilgileri:")
        print("=" * 60)
        for key, value in self.metadata.items():
            print(f"{key}: {value}")
        print(f"\nToplam Bar Sayısı: {len(self.bars)}")
        print("=" * 60)

    def print_first_bars(self, count: int = 10):
        """İlk N adet barı yazdırır"""
        print(f"\nİlk {min(count, len(self.bars))} Bar:")
        print("-" * 60)
        for i, bar in enumerate(self.bars[:count]):
            print(f"{i}: {bar}")
        print("-" * 60)

    def print_last_bars(self, count: int = 10):
        """Son N adet barı yazdırır"""
        actual_count = min(count, len(self.bars))
        start_index = max(0, len(self.bars) - actual_count)
        print(f"\nSon {actual_count} Bar:")
        print("-" * 60)
        for i, bar in enumerate(self.bars[-actual_count:], start=start_index):
            print(f"{i}: {bar}")
        print("-" * 60)

    def print_sample_bars(self, count: int = 10):
        """İlk N ve son N barı yazdırır"""
        self.print_first_bars(count)
        print("\n")
        self.print_last_bars(count)

    @property
    def ohlc(self) -> np.ndarray:
        """
        OHLC verilerini numpy array olarak döndürür.

        Returns:
            np.ndarray: Shape (N, 4) - [Open, High, Low, Close]
        """
        if len(self.bars) == 0:
            return np.array([]).reshape(0, 4)

        ohlc_data = np.zeros((len(self.bars), 4), dtype=np.float64)
        for i, bar in enumerate(self.bars):
            ohlc_data[i] = [bar.open, bar.high, bar.low, bar.close]

        return ohlc_data

    @property
    def time_data(self) -> np.ndarray:
        """
        Zaman verilerini sequential index olarak döndürür.

        Returns:
            np.ndarray: Sequential indices (0, 1, 2, ...)
        """
        return np.arange(len(self.bars), dtype=np.float64)

    @property
    def date_time_strings(self) -> np.ndarray:
        return self.datetime_data_str

    @property
    def date_strings(self) -> np.ndarray:
        """Gerçek zaman verilerini döndürür (YYYY:MM:DD)"""
        return self.date_data_str

    @property
    def time_strings(self) -> np.ndarray:
        """Gerçek zaman verilerini döndürür (HH:MM:SS)"""
        return self.time_data_str

    @property
    def epoch_times(self) -> np.ndarray:
        return self.epoch_data

    def to_dataframe(self, use_cached_numPy_arrays=True, include_date_time_as_objects=True):
        """
        Okunan tüm barları pandas DataFrame olarak döndürür.
        use_cached_numPy_arrays=True → NumPy cache kullanır (çok hızlı)
        """
        if len(self.bars) == 0:
            return pd.DataFrame()  # boş

        # --- Her iki modda da ortak kolonlar ---
        data = {
            # "id": np.arange(len(self.bars), dtype=np.int64),
            "id": [b.id for b in self.bars],  # ✔ gerçek BarData ID'si

            "epochTime": self.epoch_data if use_cached_numPy_arrays else [b.epochTime for b in self.bars],
            "dateTime": self.date_time_data_str if use_cached_numPy_arrays else [b.dateTime for b in self.bars],
            "date": self.date_data_str if use_cached_numPy_arrays else [b.date for b in self.bars],
            "time": self.time_data_str if use_cached_numPy_arrays else [b.time for b in self.bars],
        }

        # --- OHLC, Volume, Lot, Delta kolonları ---
        if use_cached_numPy_arrays:
            data.update({
                "open": self.open_data,
                "high": self.high_data,
                "low": self.low_data,
                "close": self.close_data,

                "volume": self.volume_data,
                "lot": self.lot_data,

                "delta": self.delta,
                "delta_pct": self.delta_pct,
            })
        else:
            data.update({
                "open": [b.open for b in self.bars],
                "high": [b.high for b in self.bars],
                "low": [b.low for b in self.bars],
                "close": [b.close for b in self.bars],

                "volume": [b.volume for b in self.bars],
                "lot": [b.lot for b in self.bars],

                "delta": [b.delta for b in self.bars],
                "delta_pct": [b.delta_pct for b in self.bars],
            })

        # --- dateTime, date, time kolonları ---
        if include_date_time_as_objects:
            data.update({
                "dateTimeObj": [datetime.strptime(b.dateTime, "%Y.%m.%d %H:%M:%S") for b in self.bars],
                "dateObj": [datetime.strptime(b.date, "%Y.%m.%d").date() for b in self.bars],
                "timeObj": [datetime.strptime(b.time, "%H:%M:%S").time() for b in self.bars],
            })
        else:
            data.update({
                "dateTimeObj": [None] * len(self.bars),
                "dateObj": [None] * len(self.bars),
                "timeObj": [None] * len(self.bars),
            })

        # --- DataFrame oluştur ---
        df = pd.DataFrame(data)

        return df

    def to_dataframe_indexed(self, index_by="dateTime", use_cached_numPy_arrays=True, include_date_time_as_objects=True):
        """
        DataFrame oluşturur ve istenen kolona göre index belirler.

        Args:
            index_by (str | None):
                "dateTime"  → dateTime kolonunu index yapar.
                "id"        → id kolonunu index yapar.
                "epochTime" → epochTime kolonunu index yapar.
                None        → index ayarı yapılmaz.
        """
        df = self.to_dataframe(use_cached_numPy_arrays, include_date_time_as_objects)

        if df.empty or index_by is None:
            return df

        if index_by not in df.columns:
            raise ValueError(f"Index column '{index_by}' DataFrame'de yok!")

        df = df.set_index(index_by)
        df.index.name = "timestamp" if index_by == "dateTime" else index_by

        return df

    def to_dataframe_dt64(self):
        df = self.to_dataframe()
        if df.empty:
            return df

        # dateTimeStr → localtime
        df["dateTime"] = pd.to_datetime(df["dateTime"], format="%Y.%m.%d %H:%M:%S")

        # date (only date)
        df["date"] = pd.to_datetime(df["date"], format="%Y.%m.%d")

        # time (only time)
        df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S").dt.time

        # epoch → localtime
        df["dateTimeFromEpoch"] = (
            pd.to_datetime(df["epochTime"], unit="s")
            .dt.tz_localize("UTC")
            .dt.tz_convert("Europe/Istanbul")
            .dt.tz_localize(None)
        )

        return df

    def to_dataframe_dt64_indexed(self, index_by="dateTime"):
        """
        dateTime kolonu pandas datetime64'e dönüştürülür ve index yapılır.
        Finansal analizlerde en iyi format.

        DataFrame oluşturur ve istenen kolona göre index belirler.

        Args:
            index_by (str | None):
                "dateTime"  → dateTime kolonunu index yapar.
                "id"        → id kolonunu index yapar.
                "epochTime" → epochTime kolonunu index yapar.
                None        → index ayarı yapılmaz.
        """
        df = self.to_dataframe_dt64()

        if df.empty or index_by is None:
            return df

        if index_by not in df.columns:
            raise ValueError(f"Index column '{index_by}' DataFrame'de yok!")

        df = df.set_index(index_by)
        df.index.name = "timestamp" if index_by == "dateTime" else index_by

        return df


    def to_ohlc_dataframe(self):
        """
        Sadece OHLC + dateTime + epochTime içeren hızlı bir DataFrame döndürür.
        NumPy cached array'ler kullanılarak optimize edilmiştir.
        """
        if len(self.bars) == 0:
            return pd.DataFrame()

        data = {
            "open":      self.open_data,
            "high":      self.high_data,
            "low":       self.low_data,
            "close":     self.close_data,
            "dateTime":  self.datetime_data,
            "epochTime": self.epoch_data,
        }

        df = pd.DataFrame(data)

        # Eğer datetime64 formatında istersen:
        # df["dateTime"] = pd.to_datetime(df["dateTime"], format="%Y.%m.%d %H:%M:%S")

        return df

    def to_ohlc_numpy(self) -> np.ndarray:
        """
        OHLC verilerini numpy array olarak döndürür.

        Returns:
            np.ndarray: Shape (N, 4) - [Open, High, Low, Close]
        """
        if len(self.bars) == 0:
            return np.array([]).reshape(0, 4)

        ohlc_data = np.zeros((len(self.bars), 4), dtype=np.float64)
        for i, bar in enumerate(self.bars):
            ohlc_data[i] = [bar.open, bar.high, bar.low, bar.close]

        return ohlc_data

class DataManager:
    """Data management class for reading and managing security data"""
    
    def __init__(self):
        # kolon isimleri
        self._timestamp_col = "timeStamp"
        self._date_time_col = "dateTime"
        self._date_col = "date"
        self._time_col = "time"
        self._open_col = "open"
        self._high_col = "high"
        self._low_col = "low"
        self._close_col = "close"
        self._volume_col = "volume"
        self._lot_col = "lot"
        self._delta_col = "delta"
        self._delta_pct_col = "deltaPct"
        self._bar_count = 0

        # dataframe
        self._df: pd.DataFrame | None = None

        # dosya bilgisi
        self._last_filename = None
        self._last_filesize = None

        # timing bilgisi
        self._timing_report = {}

        # data reading modes
        self._read_mode = "all_data"  # all_data, last_n, first_n, range
        self._read_params = {}  # parameters for each mode

        self.set_columns(timestamp_col="timeStamp",
                         date_time_col = "dateTime", date_col = "date", time_col = "time",
                         open_col="open", high_col="high", low_col="low", close_col="close",
                         volume_col="volume", lot_col="lot",
                         delta_col = "delta", delta_pct_col = "delta_pct")

        self.reader = CSVBarDataReader()
    
    def readSecurityData(self, data_dir: str, subdir: str, filename: str) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, int]:
        """
        Reads security data from CSV file and returns OHLCV data as pandas Series
        
        Args:
            data_dir: Base data directory (e.g., "algorithmic_trading\\data")
            subdir: Subdirectory (e.g., "01")
            filename: CSV filename (e.g., "BTCUSD.csv")
            
        Returns:
            Tuple of (Open, High, Low, Close, Volume, Lot, BarCount)
        """
        file_path = os.path.join(data_dir, subdir, filename)
        
        # Read CSV file (limit to first 10000 rows for testing)
        df = pd.read_csv(file_path, nrows=10000)
        
        # Extract series
        Open = pd.Series(df['open'].values)
        High = pd.Series(df['high'].values)
        Low = pd.Series(df['low'].values)
        Close = pd.Series(df['close'].values)
        Volume = pd.Series(df['volume'].values)
        Lot = pd.Series(df['lot'].values)  # Using lot as Lot equivalent
        BarCount = len(df)
        
        return Open, High, Low, Close, Volume, Lot, BarCount

    # --------------------------------------------------------
    # Genel zaman ölçer
    def _timeit(self, name, func, *args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        self._timing_report[name] = elapsed
        return result

    # --------------------------------------------------------
    # Timer raporu
    def reportTimes(self):
        print("\n=== Timing Report ===")
        if not self._timing_report:
            print("No timing data collected.")
            return
        for k, v in self._timing_report.items():
            print(f"{k:25s}: {v:.6f} sec")

    # --------------------------------------------------------
    # kolon isimlerini ayarla
    def set_columns(self, timestamp_col="timeStamp",
                    date_time_col = "dateTime", date_col = "date", time_col = "time",
                    open_col="open", high_col="high",
                    low_col="low", close_col="close",
                    volume_col="volume", lot_col="lot",
                    delta_col = "delta", delta_pct_col = "deltaPct"):
        self._timestamp_col = timestamp_col
        self._date_time_col = date_time_col
        self._date_col = date_col
        self._time_col = time_col
        self._open_col = open_col
        self._high_col = high_col
        self._low_col = low_col
        self._close_col = close_col
        self._volume_col = volume_col
        self._lot_col = lot_col
        self._delta_col = delta_col
        self._delta_pct_col = delta_pct_col



    # --------------------------------------------------------
    # Data reading mode configuration
    def set_read_mode_all_data(self):
        """Read all data from CSV file"""
        self._read_mode = "all_data"
        self._read_params = {}
    
    def set_read_mode_last_n(self, n: int):
        """Read last n rows from CSV file"""
        self._read_mode = "last_n"
        self._read_params = {"n": n}
    
    def set_read_mode_first_n(self, n: int):
        """Read first n rows from CSV file"""
        self._read_mode = "first_n"
        self._read_params = {"n": n}
    
    def set_read_mode_range(self, start: int, end: int):
        """Read data from start to end row (inclusive)"""
        """start dahil, end  dahil değil"""
        self._read_mode = "range"
        self._read_params = {"start": start, "end": end}

    def set_read_mode_after_date(self, start_date: str):
        """Read data after start_date (inclusive)"""
        self._read_mode = "after_date"
        self._read_params = {"start_date": start_date}

    def set_read_mode_before_date(self, end_date: str):
        """Read data before end_date (exclusive)"""
        self._read_mode = "before_date"
        self._read_params = {"end_date": end_date}

    def set_read_mode_between_dates(self, start_date: str, end_date: str):
        """Read data between start_date (inclusive) and end_date (exclusive)"""
        self._read_mode = "between_dates"
        self._read_params = {"start_date": start_date, "end_date": end_date}








    def _apply_read_mode(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply the configured read mode to the dataframe"""
        if self._read_mode == "all_data":
            return df
        elif self._read_mode == "last_n":
            n = self._read_params.get("n", 1000)
            return df.tail(n).copy()
        elif self._read_mode == "first_n":
            n = self._read_params.get("n", 1000)
            return df.head(n).copy()
        elif self._read_mode == "range":
            start = self._read_params.get("start", 0)
            end = self._read_params.get("end", len(df))
            # Ensure bounds are valid
            start = max(0, start)
            end = min(len(df), end)
            if start >= end:
                print(f"Warning: Invalid range start={start}, end={end}, returning empty dataframe")
                return df.iloc[0:0].copy()  # Empty dataframe with same columns
            return df.iloc[start:end].copy()
        else:
            print(f"Warning: Unknown read mode '{self._read_mode}', using all data")
            return df

    # --------------------------------------------------------
    # CSV oku
    # D:\Aykut\Projects\AlgoTradeWithPaythonWithGemini\data\01 altındaki csv dosyalarından okur
    def load_prices_from_csv(self, data_dir: str, subdir: str, file_name: str, auto_time=False):
        def _impl():
            self.clear_dataframe()

            file_path = os.path.join(data_dir, subdir, file_name)
            # Read full CSV file first
            df_full = pd.read_csv(file_path)
            
            # Apply read mode to filter data
            df = self._apply_read_mode(df_full)
            
            self._df = df
            self._last_filename = file_name
            self._last_filesize = os.path.getsize(file_path)
            self._bar_count = len(df)
            
            print(f"Read mode: {self._read_mode}")
            if self._read_params:
                print(f"Read params: {self._read_params}")
            print(f"Total rows in file: {len(df_full)}")
            print(f"Loaded rows: {len(df)}")
            
            if auto_time:
                self.add_time_columns()

        return self._timeit("load_prices_from_csv", _impl)

    # --------------------------------------------------------
    # CSV oku
    # D:\Aykut\Projects\AlgoTradeWithPaythonWithGemini\data\csvFiles altındaki csv dosyalarından okur
    def load_prices_from_csv_2(self, data_dir: str, subdir: str, file_name: str, auto_time=False):
        def _impl():
            self.clear_dataframe()

            file_path = os.path.join(data_dir, subdir, file_name)

            # Read CSV file, skipping header lines (first 7 lines are metadata)
            df_full = pd.read_csv(file_path, skiprows=7, sep=';')

            # Rename columns to match internal column names
            df_full.rename(columns={
                'Open': self._open_col,
                'High': self._high_col,
                'Low': self._low_col,
                'Close': self._close_col,
                'Volume': self._volume_col,
                'Lot': self._lot_col
            }, inplace=True)

            # Combine Date and Time columns to create timestamp
            df_full['datetime_str'] = df_full['Date'] + ' ' + df_full['Time']
            df_full[self._timestamp_col] = pd.to_datetime(df_full['datetime_str'], format='%Y.%m.%d %H:%M:%S').astype('int64') // 1_000_000_000

            # Drop the temporary columns
            df_full.drop(columns=['Date', 'Time', 'datetime_str'], inplace=True)

            # Reorder columns to match expected order
            expected_cols = [self._timestamp_col, self._open_col, self._high_col,
                           self._low_col, self._close_col, self._volume_col, self._lot_col]
            df_full = df_full[expected_cols]

            # Apply read mode to filter data
            df = self._apply_read_mode(df_full)

            self._df = df
            self._last_filename = file_name
            self._last_filesize = os.path.getsize(file_path)
            self._bar_count = len(df)

            print(f"Read mode: {self._read_mode}")
            if self._read_params:
                print(f"Read params: {self._read_params}")
            print(f"Total rows in file: {len(df_full)}")
            print(f"Loaded rows: {len(df)}")

            if auto_time:
                self.add_time_columns()

        return self._timeit("load_prices_from_csv_2", _impl)

    # --------------------------------------------------------
    # CSV oku
    # D:\iDeal\ChartData\_Exports altındaki csv dosyalarından okur
    def load_prices_from_csv_3(self, data_dir: str, subdir: str, file_name: str, auto_time=False):
        def _impl():
            self.clear_dataframe()

            file_path = os.path.join(data_dir, subdir, file_name)

            # Read CSV file, skipping metadata and "# Data" line (first 8 lines)
            df_full = pd.read_csv(file_path, skiprows=8, sep=';', decimal=',')

            # Remove leading/trailing whitespace from column names
            df_full.columns = df_full.columns.str.strip()

            # Remove trailing empty columns if any
            df_full = df_full.loc[:, ~df_full.columns.str.contains('^Unnamed')]

            # Parse the datetime column (format: "YYYY.MM.DD HH:MM:SS")
            df_full['datetime_parsed'] = pd.to_datetime(df_full['Date Time'].str.strip(), format='%Y.%m.%d %H:%M:%S')
            df_full[self._timestamp_col] = df_full['datetime_parsed'].astype('int64') // 1_000_000_000

            # Rename columns to match internal column names
            df_full.rename(columns={
                'Open': self._open_col,
                'High': self._high_col,
                'Low': self._low_col,
                'Close': self._close_col,
                'Volume': self._volume_col,
                'Lot': self._lot_col
            }, inplace=True)

            # Drop unnecessary columns
            df_full.drop(columns=['Id', 'Date Time', 'datetime_parsed'], inplace=True)

            # Reorder columns to match expected order
            expected_cols = [self._timestamp_col, self._open_col, self._high_col,
                           self._low_col, self._close_col, self._volume_col, self._lot_col]
            df_full = df_full[expected_cols]

            # Apply read mode to filter data
            df = self._apply_read_mode(df_full)

            self._df = df
            self._last_filename = file_name
            self._last_filesize = os.path.getsize(file_path)
            self._bar_count = len(df)

            print(f"Read mode: {self._read_mode}")
            if self._read_params:
                print(f"Read params: {self._read_params}")
            print(f"Total rows in file: {len(df_full)}")
            print(f"Loaded rows: {len(df)}")

            if auto_time:
                self.add_time_columns()

        return self._timeit("load_prices_from_csv_3", _impl)

    # --------------------------------------------------------
    # CSV oku
    # Yeni format için: header metadata + # Data satırı
    def load_prices_from_csv_4(self, data_dir: str, subdir: str, file_name: str, auto_time=False):
        def _impl():
            self.clear_dataframe()

            file_path = os.path.join(data_dir, subdir, file_name)

            # First, read the header to get column names from "# Format :" line
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Find the Format line and extract column names
            format_line = None
            data_line_index = None
            for i, line in enumerate(lines):
                if line.startswith('# Format :'):
                    format_line = line
                elif line.strip() == '# Data':
                    data_line_index = i
                    break
            
            if format_line is None or data_line_index is None:
                raise ValueError("Could not find '# Format :' or '# Data' line in file")
            
            # Parse column names from format line: "# Format : Id Date Time Open High Low Close Volume Lot"
            column_names = format_line.split(':')[1].strip().split()
            
            # Read CSV file, skipping lines up to and including "# Data"
            df_full = pd.read_csv(file_path, skiprows=data_line_index + 1, sep=';', names=column_names)

            # Rename columns to match internal column names
            df_full.rename(columns={
                'Open': self._open_col,
                'High': self._high_col,
                'Low': self._low_col,
                'Close': self._close_col,
                'Volume': self._volume_col,
                'Lot': self._lot_col
            }, inplace=True)

            # Combine Date and Time columns to create timestamp
            df_full['datetime_str'] = df_full['Date'] + ' ' + df_full['Time']
            df_full[self._timestamp_col] = pd.to_datetime(df_full['datetime_str'], format='%Y.%m.%d %H:%M:%S').astype('int64') // 1_000_000_000

            # Drop the temporary columns including Id
            df_full.drop(columns=['Id', 'Date', 'Time', 'datetime_str'], inplace=True)

            # Reorder columns to match expected order
            expected_cols = [self._timestamp_col, self._open_col, self._high_col,
                           self._low_col, self._close_col, self._volume_col, self._lot_col]
            df_full = df_full[expected_cols]

            # Apply read mode to filter data
            df = self._apply_read_mode(df_full)

            self._df = df
            self._last_filename = file_name
            self._last_filesize = os.path.getsize(file_path)
            self._bar_count = len(df)

            print(f"Read mode: {self._read_mode}")
            if self._read_params:
                print(f"Read params: {self._read_params}")
            print(f"Total rows in file: {len(df_full)}")
            print(f"Loaded rows: {len(df)}")

            if auto_time:
                self.add_time_columns()

        return self._timeit("load_prices_from_csv_4", _impl)

    # --------------------------------------------------------
    # TXT oku
    # D:\iDeal\ChartData\_Exports altındaki txt dosyalarından okur
    def load_prices_from_txt_3(self, data_dir: str, subdir: str, file_name: str, auto_time=False):
        def _impl():
            self.clear_dataframe()

            file_path = os.path.join(data_dir, subdir, file_name)

            # Read TXT file, skipping metadata and "Data" line (first 8 lines)
            df_full = pd.read_csv(file_path, skiprows=8, sep='\t', decimal=',', engine='python')

            # Remove leading/trailing whitespace from all string columns
            df_full = df_full.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

            # Remove any completely empty columns
            df_full = df_full.dropna(axis=1, how='all')

            # Assign column names manually (since TXT has no header row after line 8)
            expected_txt_cols = ['Id', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Lot']
            if len(df_full.columns) >= 9:
                df_full.columns = expected_txt_cols[:len(df_full.columns)]
            else:
                # If fewer columns, assign what we have
                df_full.columns = expected_txt_cols[:len(df_full.columns)]

            # Combine Date and Time columns to create timestamp
            df_full['datetime_parsed'] = pd.to_datetime(df_full['Date'] + ' ' + df_full['Time'], format='%Y.%m.%d %H:%M:%S')
            df_full[self._timestamp_col] = df_full['datetime_parsed'].astype('int64') // 1_000_000_000

            # Rename columns to match internal column names
            df_full.rename(columns={
                'Open': self._open_col,
                'High': self._high_col,
                'Low': self._low_col,
                'Close': self._close_col,
                'Volume': self._volume_col,
                'Lot': self._lot_col
            }, inplace=True)

            # Drop unnecessary columns
            columns_to_drop = ['Id', 'Date', 'Time', 'datetime_parsed']
            df_full.drop(columns=[col for col in columns_to_drop if col in df_full.columns], inplace=True)

            # Reorder columns to match expected order
            expected_cols = [self._timestamp_col, self._open_col, self._high_col,
                           self._low_col, self._close_col, self._volume_col, self._lot_col]
            df_full = df_full[expected_cols]

            # Apply read mode to filter data
            df = self._apply_read_mode(df_full)

            self._df = df
            self._last_filename = file_name
            self._last_filesize = os.path.getsize(file_path)
            self._bar_count = len(df)

            print(f"Read mode: {self._read_mode}")
            if self._read_params:
                print(f"Read params: {self._read_params}")
            print(f"Total rows in file: {len(df_full)}")
            print(f"Loaded rows: {len(df)}")

            if auto_time:
                self.add_time_columns()

        return self._timeit("load_prices_from_txt_3", _impl)
    # --------------------------------------------------------
    # zaman kolonlarını ekle
    def add_time_columns(self):
        def _impl():
            if self._df is None:
                print("No data loaded.")
                return

            ts = self._df[self._timestamp_col]
            print(self._timestamp_col)

            # epoch mu datetime mı kontrol
            if pd.api.types.is_integer_dtype(ts) or (ts.dtype == "object" and ts.str.isdigit().all()):
                # User provided timezone conversion: UTC epoch -> Europe/Istanbul
                dt = (pd.to_datetime(ts, unit="s", errors="coerce")
                      .dt.tz_localize("UTC")
                      .dt.tz_convert("Europe/Istanbul")
                      .dt.tz_localize(None))
                self._df["epoch_time_stamp"] = ts.astype("int64")
                print("11")
            else:
                dt = pd.to_datetime(ts, errors="coerce").dt.tz_localize(None)
                self._df["epoch_time_stamp"] = dt.astype("int64") // 1_000_000_000
                print("12")

            # ek kolonlar
            self._df["dateTimeObj"] = dt
            self._df["dateObj"] = dt.dt.date
            self._df["timeObj"] = dt.dt.time

        # print("\n flag cagrilacak")
        # print(self._df.tail())
        # name = input("Devam etmek icin tusa basiniz... ")

        return self._timeit("add_time_columns", _impl)

    # --------------------------------------------------------
    # index işlemleri
    def set_datetime_index(self, drop=False):
        if self._df is None or "date_time" not in self._df:
            print("No data to set index.")
            return
        self._df.set_index("date_time", drop=drop, inplace=True)

    def reset_datetime_index(self):
        if self._df is None:
            print("No data to reset index.")
            return
        self._df.reset_index(drop=False, inplace=True)

    # --------------------------------------------------------
    # DataFrame erişim
    def get_dataframe(self):
        return self._df

    def clear_dataframe(self):
        self._df = None
        self._last_filename = None
        self._last_filesize = None

    def summary(self, n=5):
        def _impl():
            if self._df is None:
                print("No data loaded.")
                return
            print(self._df.head(n))
            print("...")
            print(self._df.tail(n))
            print(f"Rows: {len(self._df)}")
            print(f"Columns: {list(self._df.columns)}")
        return self._timeit("summary", _impl)

    # --------------------------------------------------------
    # getter'lar (NumPy array tabanlı)
    def get_open_array(self):
        if self._df is None or self._open_col not in self._df:
            return np.array([])
        return self._df[self._open_col].to_numpy()

    def get_high_array(self):
        if self._df is None or self._high_col not in self._df:
            return np.array([])
        return self._df[self._high_col].to_numpy()

    def get_low_array(self):
        if self._df is None or self._low_col not in self._df:
            return np.array([])
        return self._df[self._low_col].to_numpy()

    def get_close_array(self):
        if self._df is None or self._close_col not in self._df:
            return np.array([])
        return self._df[self._close_col].to_numpy()

    def get_volume_array(self):
        if self._df is None or self._volume_col not in self._df:
            return np.array([])
        return self._df[self._volume_col].to_numpy()

    def get_lot_array(self):
        if self._df is None or self._lot_col not in self._df:
            return np.array([])
        return self._df[self._lot_col].to_numpy()

    def get_delta_array(self):
        if self._df is None or self._delta_col not in self._df:
            return np.array([])
        return self._df[self._delta_col].to_numpy()

    def get_delta_pct_array(self):
        if self._df is None or self._delta_pct_col not in self._df:
            return np.array([])
        return self._df[self._delta_pct_col].to_numpy()

    # --- time based ---
    def get_date_time_array(self):
        if self._df is None or "date_time" not in self._df:
            return np.array([])
        return self._df["date_time"].to_numpy()

    def get_date_time_array_as_str(self):
        """Returns dateTime string array ('YYYY.MM.DD HH:MM:SS')"""
        if self._df is None or "dateTime" not in self._df:
            return np.array([])
        return self._df["dateTime"].to_numpy()

    def get_date_array(self):
        """Returns dateObj array (date objects)"""
        if self._df is None or "dateObj" not in self._df:
            return np.array([])
        return self._df["dateObj"].to_numpy()

    def get_date_array_as_str(self):
        """Returns date string array ('YYYY.MM.DD')"""
        if self._df is None or "date" not in self._df:
            return np.array([])
        return self._df["date"].to_numpy()

    def get_time_array(self):
        """Returns timeObj array (time objects)"""
        if self._df is None or "timeObj" not in self._df:
            return np.array([])
        return self._df["timeObj"].to_numpy()

    def get_time_array_as_str(self):
        """Returns time string array ('HH:MM:SS')"""
        if self._df is None or "time" not in self._df:
            return np.array([])
        return self._df["time"].to_numpy()

    # --- timestamp / epoch ---
    def get_timestamp_array(self):
        if self._df is None or self._timestamp_col not in self._df:
            return np.array([])
        return self._df[self._timestamp_col].to_numpy()

    def get_timestamp_array_as_str(self):
        if self._df is None or self._timestamp_col not in self._df:
            return np.array([])
        if "timestamp_str" not in self._df:
            self._df["timestamp_str"] = self._df[self._timestamp_col].astype(str)
        return self._df["timestamp_str"].to_numpy()

    def get_epoch_time_array(self):
        if self._df is None or "epochTime" not in self._df:
            return np.array([])
        return self._df["epochTime"].to_numpy()

    def get_epoch_time_array_as_str(self):
        if self._df is None or "epochTime" not in self._df:
            return np.array([])
        if "epochTime_str" not in self._df:
            self._df["epochTime_str"] = self._df["epochTime"].astype(str)
        return self._df["epochTime_str"].to_numpy()

    # --- NEW: datetime/date/time object arrays ---
    def get_date_time_array_new(self):
        """Returns dateTimeObj column as numpy array (datetime objects)"""
        if self._df is None or "dateTimeObj" not in self._df:
            return np.array([])
        return self._df["dateTimeObj"].to_numpy()

    def get_date_array_new(self):
        """Returns dateObj column as numpy array (date objects)"""
        if self._df is None or "dateObj" not in self._df:
            return np.array([])
        return self._df["dateObj"].to_numpy()

    def get_time_array_new(self):
        """Returns timeObj column as numpy array (time objects)"""
        if self._df is None or "timeObj" not in self._df:
            return np.array([])
        return self._df["timeObj"].to_numpy()

    # --- NEW: datetime/date/time string arrays ---
    def get_date_time_string_array_new(self):
        """Returns dateTime column as numpy array (strings: 'YYYY.MM.DD HH:MM:SS')"""
        if self._df is None or "dateTime" not in self._df:
            return np.array([])
        return self._df["dateTime"].to_numpy()

    def get_date_string_array_new(self):
        """Returns date column as numpy array (strings: 'YYYY.MM.DD')"""
        if self._df is None or "date" not in self._df:
            return np.array([])
        return self._df["date"].to_numpy()

    def get_time_string_array_new(self):
        """Returns time column as numpy array (strings: 'HH:MM:SS')"""
        if self._df is None or "time" not in self._df:
            return np.array([])
        return self._df["time"].to_numpy()

    # --- misc ---
    def get_items_count(self):
        return len(self._df) if self._df is not None else 0

    # --------------------------------------------------------
    # Timer utilities
    def startTimer(self):
        """Başlangıç zamanını kaydeder."""
        self._t0 = time.time()

    def stopTimer(self, label="Elapsed"):
        """Başlangıçtan itibaren geçen süreyi ekrana basar ve saniye olarak döndürür."""
        if not hasattr(self, "_t0"):
            print("Timer not started.")
            return None
        elapsed = time.time() - self._t0
        print(f"{label}: {elapsed:.4f} seconds")
        return elapsed

    def print_head(self, n=5):
        """DataFrame'in ilk n satırını tüm kolonlarla birlikte yazdırır."""
        if self._df is None:
            print("No data loaded.")
            return
        with pd.option_context(
                "display.max_columns", None,
                "display.width", None,
                "display.max_colwidth", None
        ):
            print(self._df.head(n))

    def print_tail(self, n=5):
        """DataFrame'in son n satırını tüm kolonlarla birlikte yazdırır."""
        if self._df is None:
            print("No data loaded.")
            return
        with pd.option_context(
                "display.max_columns", None,
                "display.width", None,
                "display.max_colwidth", None
        ):
            print(self._df.tail(n))

    def get_bar_count(self):
        return self._bar_count
    
    # --------------------------------------------------------
    # Synthetic data creation
    def create_data(self, n_bars: int):
        """
        Create synthetic OHLCV data based on sine wave pattern.
        
        Args:
            n_bars: Number of bars to generate
        """
        def _impl():
            import math
            import random
            from datetime import datetime, timedelta
            
            self.clear_dataframe()
            
            # Set random seed for reproducible results
            random.seed(42)
            np.random.seed(42)
            
            # Generate timestamps - current time going backwards n_bars
            current_timestamp = int(datetime.now().timestamp())
            timestamps = [current_timestamp - (i * 3600) for i in range(n_bars)]  # 1 hour intervals
            timestamps.reverse()  # Make it chronological order
            
            # Generate sine-based close prices
            base_price = 5000  # Starting around 50,000
            amplitude = 1000   # Price variation amplitude
            close_prices = []
            
            for i in range(n_bars):
                # Sine wave with some noise
                sine_value = math.sin(i * 0.1)  # 0.1 controls frequency
                noise = random.uniform(-0.2, 0.2)  # Random noise
                price = base_price + (amplitude * sine_value) + (amplitude * noise * 0.1)
                close_prices.append(max(100, price))  # Ensure minimum price of 100
            
            # Generate OHLC data based on close prices
            ohlcv_data = []
            for i, close_price in enumerate(close_prices):
                # Generate realistic OHLC based on close
                volatility = random.uniform(0.005, 0.02)  # 0.5% to 2% volatility
                
                # High: close + random amount up to volatility
                high = close_price * (1 + random.uniform(0, volatility))
                
                # Low: close - random amount up to volatility  
                low = close_price * (1 - random.uniform(0, volatility))
                
                # Open: somewhere between high and low, closer to previous close
                if i > 0:
                    prev_close = close_prices[i-1]
                    open_price = prev_close + random.uniform(-volatility/2, volatility/2) * prev_close
                    open_price = max(low, min(high, open_price))  # Ensure within high/low range
                else:
                    open_price = close_price * (1 + random.uniform(-volatility/2, volatility/2))
                
                # Ensure OHLC relationships are valid
                high = max(high, open_price, close_price)
                low = min(low, open_price, close_price)
                
                # Generate volume (random but realistic)
                base_volume = random.uniform(1000, 10000)
                volume = base_volume * random.uniform(0.5, 2.0)
                
                # Generate lot (usually smaller than volume)
                lot = volume * random.uniform(0.1, 0.3)
                
                ohlcv_data.append({
                    self._timestamp_col: timestamps[i],
                    self._open_col: round(open_price, 2),
                    self._high_col: round(high, 2), 
                    self._low_col: round(low, 2),
                    self._close_col: round(close_price, 2),
                    self._volume_col: round(volume, 2),
                    self._lot_col: round(lot, 2)
                })
            
            # Create DataFrame
            self._df = pd.DataFrame(ohlcv_data)
            
            # Set the same attributes that load_prices_from_csv sets
            self._last_filename = f"synthetic_data_{n_bars}_bars.csv"
            self._last_filesize = len(str(self._df))  # Approximate size
            self._bar_count = n_bars
            
            print(f"Generated synthetic data: {n_bars} bars")
            print(f"Price range: {self._df[self._close_col].min():.2f} - {self._df[self._close_col].max():.2f}")
            print(f"Time range: {datetime.fromtimestamp(timestamps[0])} to {datetime.fromtimestamp(timestamps[-1])}")
        
        return self._timeit("create_data", _impl)

    def load_prices_from_csv_with_bar_data_reader(self, data_dir: str, subdir: str, file_name: str, auto_time=False):
        file_path = os.path.join(data_dir, subdir, file_name)
        return self.load_prices_from_csv_with_bar_data_reader(file_path, auto_time)

    def load_prices_from_csv_with_bar_data_reader(self, file_path: str, auto_time=False):
        def _impl():

            dir_path             = os.path.dirname(file_path)
            file_name            = os.path.basename(file_path)
            name_no_ext, ext     = os.path.splitext(file_name)
            drive, path_no_drive = os.path.splitdrive(file_path)
            norm                 = os.path.normpath(file_path)

            self.clear_dataframe()

            # Reader'ı hazırla
            self.reader.set_file_path(file_path)

            # Okuma moduna göre oku
            success = False
            if self._read_mode == "all_data":
                success = self.reader.read_file()
            elif self._read_mode == "last_n":
                n = self._read_params.get("n", 1000)
                success = self.reader.read_file(n)
            elif self._read_mode == "first_n":
                n = self._read_params.get("n", 1000)
                success = self.reader.read_file_first_n_data(n)
            elif self._read_mode == "range":
                start = self._read_params.get("start", 0)
                end = self._read_params.get("end", 0)
                success = self.reader.read_file(start, end)
            # --- YENİ EKLENEN KISIMLAR ---
            elif self._read_mode == "after_date":
                start_date = self._read_params.get("start_date", "")
                success = self.reader.read_file_after_date(start_date)
            elif self._read_mode == "before_date":
                end_date = self._read_params.get("end_date", "")
                success = self.reader.read_file_before_date(end_date)
            elif self._read_mode == "between_dates":
                start_date = self._read_params.get("start_date", "")
                end_date = self._read_params.get("end_date", "")
                success = self.reader.read_file_between_dates(start_date, end_date)
            # -----------------------------
            else:
                success = self.reader.read_file()

            if success:
                print("\n" + "=" * 60)
                print(f"Grafik Sembolü        : {self.reader.get_metadata('GrafikSembol')}")
                print(f"Periyot               : {self.reader.get_metadata('GrafikPeriyot')} dakika")
                print(f"Dosyadaki Toplam Veri : {self.reader.get_metadata('BarCount')} bar")
                print(f"Yüklenen Bar Sayısı   : {self.reader.get_bar_count()} bar")
                print(f"Başlangıç             : {self.reader.get_metadata('Baslangic_Tarihi')}")
                print(f"Bitiş                 : {self.reader.get_metadata('Bitis_Tarihi')}")
                print("=" * 60)

                self._last_filename = file_name
                self._last_filesize = os.path.getsize(file_path)
                self._bar_count = self.reader.get_bar_count()
            else:
                print(f"Failed to read file: {file_path}")

        return self._timeit("load_prices_from_csv_with_bar_data_reader", _impl)

    def build_data_frame(self):
        def _impl():
            # DataFrame'i oluştur ve DataManager'a set et
            self._df = self.reader.to_dataframe_indexed(index_by=None, use_cached_numPy_arrays=True) # index_by="dateTime"

            # timeStamp kolonunu ayarla
            if not self._df.empty:
                self._df[self._timestamp_col] = self._df["epochTime"]

        return self._timeit("build_data_frame", _impl)

    def print_sample_bars(self, count: int = 10):
        """İlk N ve son N barı yazdırır (reader'dan)"""
        if hasattr(self, 'reader') and self.reader is not None:
            self.reader.print_sample_bars(count)
        else:
            print("No reader available.")

    def print_first_bars(self, count: int = 10):
        if hasattr(self, 'reader') and self.reader is not None:
            self.reader.print_first_bars(count)
        else:
            print("No reader available.")

    def print_last_bars(self, count: int = 10):
        if hasattr(self, 'reader') and self.reader is not None:
            self.reader.print_last_bars(count)
        else:
            print("No reader available.")

    def get_reader(self):
        return self.reader