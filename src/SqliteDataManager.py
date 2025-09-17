import os
import time
import sqlite3
import numpy as np
import pandas as pd
from typing import Tuple, Optional, List
from datetime import datetime


class SqliteDataManager:
    """SQLite database data management class for reading and managing security data"""

    def __init__(self):
        # kolon isimleri
        self._timestamp_col = "datetime"
        self._open_col = "open"
        self._high_col = "high"
        self._low_col = "low"
        self._close_col = "close"
        self._volume_col = "volume"
        self._lot_col = "lot"
        self._symbol_col = "symbol"
        self._bar_count = 0

        # dataframe
        self._df: pd.DataFrame | None = None

        # database bilgisi
        self._last_db_path = None
        self._last_table = None
        self._last_symbol = None

        # timing bilgisi
        self._timing_report = {}

        # data reading modes
        self._read_mode = "all_data"  # all_data, last_n, first_n, range
        self._read_params = {}  # parameters for each mode

        self.set_columns(timestamp_col="datetime", open_col="open", high_col="high", low_col="low",
                                close_col="close", volume_col="volume", lot_col="lot", symbol_col="symbol")

    def readSecurityData(self, db_path: str, table_name: str, symbol: str) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, int]:
        """
        Reads security data from SQLite database and returns OHLCV data as pandas Series

        Args:
            db_path: Path to SQLite database file (e.g., "D:\\iDeal\\ChartData\\_sqlLite\\IMKBH_fast.db")
            table_name: Table name (e.g., "period_05")
            symbol: Symbol name (e.g., "AEFES")

        Returns:
            Tuple of (Open, High, Low, Close, Volume, Lot, BarCount)
        """
        try:
            conn = sqlite3.connect(db_path)

            # Query to get data for specific symbol
            query = f"""
            SELECT {self._timestamp_col}, {self._open_col}, {self._high_col},
                   {self._low_col}, {self._close_col}, {self._volume_col}, {self._lot_col}
            FROM {table_name}
            WHERE {self._symbol_col} = ?
            ORDER BY {self._timestamp_col}
            LIMIT 10000
            """

            df = pd.read_sql_query(query, conn, params=(symbol,))
            conn.close()

            if df.empty:
                print(f"No data found for symbol {symbol} in {table_name}")
                empty_series = pd.Series([])
                return empty_series, empty_series, empty_series, empty_series, empty_series, empty_series, 0

            # Extract series
            Open = pd.Series(df[self._open_col].values)
            High = pd.Series(df[self._high_col].values)
            Low = pd.Series(df[self._low_col].values)
            Close = pd.Series(df[self._close_col].values)
            Volume = pd.Series(df[self._volume_col].values)
            Lot = pd.Series(df[self._lot_col].values)
            BarCount = len(df)

            return Open, High, Low, Close, Volume, Lot, BarCount

        except Exception as e:
            print(f"Error reading data from SQLite: {e}")
            empty_series = pd.Series([])
            return empty_series, empty_series, empty_series, empty_series, empty_series, empty_series, 0

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
    def set_columns(self, timestamp_col="datetime",
                    open_col="open", high_col="high",
                    low_col="low", close_col="close",
                    volume_col="volume", lot_col="lot", symbol_col="symbol"):
        self._timestamp_col = timestamp_col
        self._open_col = open_col
        self._high_col = high_col
        self._low_col = low_col
        self._close_col = close_col
        self._volume_col = volume_col
        self._lot_col = lot_col
        self._symbol_col = symbol_col

    # --------------------------------------------------------
    # Data reading mode configuration
    def set_read_mode_all_data(self):
        """Read all data from SQLite database"""
        self._read_mode = "all_data"
        self._read_params = {}

    def set_read_mode_last_n(self, n: int):
        """Read last n rows from SQLite database"""
        self._read_mode = "last_n"
        self._read_params = {"n": n}

    def set_read_mode_first_n(self, n: int):
        """Read first n rows from SQLite database"""
        self._read_mode = "first_n"
        self._read_params = {"n": n}

    def set_read_mode_range(self, start: int, end: int):
        """Read data from start to end row (inclusive)"""
        """start dahil, end dahil değil"""
        self._read_mode = "range"
        self._read_params = {"start": start, "end": end}

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
    # SQLite veritabanından veri oku
    def load_prices_from_sqlite(self, db_path: str, table_name: str, symbol: str, auto_time=False):
        """
        Load price data from SQLite database

        Args:
            db_path: Path to SQLite database file
            table_name: Table name (e.g., "period_05")
            symbol: Symbol name (e.g., "AEFES")
            auto_time: Automatically add time columns
        """
        def _impl():
            self.clear_dataframe()

            try:
                conn = sqlite3.connect(db_path)

                # Query to get data for specific symbol
                query = f"""
                SELECT * FROM {table_name}
                WHERE {self._symbol_col} = ?
                ORDER BY {self._timestamp_col}
                """

                # Read full data first
                df_full = pd.read_sql_query(query, conn, params=(symbol,))
                conn.close()

                if df_full.empty:
                    print(f"No data found for symbol {symbol} in {table_name}")
                    return

                # Apply read mode to filter data
                df = self._apply_read_mode(df_full)

                self._df = df
                self._last_db_path = db_path
                self._last_table = table_name
                self._last_symbol = symbol
                self._bar_count = len(df)

                print(f"Read mode: {self._read_mode}")
                if self._read_params:
                    print(f"Read params: {self._read_params}")
                print(f"Total rows in database: {len(df_full)}")
                print(f"Loaded rows: {len(df)}")

                if auto_time:
                    self.add_time_columns()

            except Exception as e:
                print(f"Error loading data from SQLite: {e}")

        return self._timeit("load_prices_from_sqlite", _impl)

    # --------------------------------------------------------
    # zaman kolonlarını ekle
    def add_time_columns(self):
        def _impl():
            if self._df is None:
                print("No data loaded.")
                return

            ts = self._df[self._timestamp_col]

            # datetime string'ini parse et
            try:
                dt = pd.to_datetime(ts, errors="coerce").dt.tz_localize(None)
                self._df["epoch_time_stamp"] = dt.astype("int64") // 1_000_000_000

                # ek kolonlar
                self._df["date_time"] = dt
                self._df["date"] = dt.dt.date
                self._df["time"] = dt.dt.time

            except Exception as e:
                print(f"Error adding time columns: {e}")

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
        self._last_db_path = None
        self._last_table = None
        self._last_symbol = None

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

    def get_symbol_array(self):
        if self._df is None or self._symbol_col not in self._df:
            return np.array([])
        return self._df[self._symbol_col].to_numpy()

    # --- time based ---
    def get_date_time_array(self):
        if self._df is None or "date_time" not in self._df:
            return np.array([])
        return self._df["date_time"].to_numpy()

    def get_date_time_array_as_str(self):
        if self._df is None or "date_time" not in self._df:
            return np.array([])
        if "date_time_str" not in self._df:
            self._df["date_time_str"] = self._df["date_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
        return self._df["date_time_str"].to_numpy()

    def get_date_array(self):
        if self._df is None or "date_time" not in self._df:
            return np.array([])
        return self._df["date_time"].values.astype("datetime64[D]")

    def get_date_array_as_str(self):
        if self._df is None or "date_time" not in self._df:
            return np.array([])
        if "date_str" not in self._df:
            self._df["date_str"] = self._df["date_time"].dt.strftime("%Y-%m-%d")
        return self._df["date_str"].to_numpy()

    def get_time_array(self):
        if self._df is None or "date_time" not in self._df:
            return np.array([])
        if "time_obj" not in self._df:
            self._df["time_obj"] = self._df["date_time"].dt.time
        return self._df["time_obj"].to_numpy()

    def get_time_array_as_str(self):
        if self._df is None or "date_time" not in self._df:
            return np.array([])
        if "time_str" not in self._df:
            self._df["time_str"] = self._df["date_time"].dt.strftime("%H:%M:%S")
        return self._df["time_str"].to_numpy()

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
        if self._df is None or "epoch_time_stamp" not in self._df:
            return np.array([])
        return self._df["epoch_time_stamp"].to_numpy()

    def get_epoch_time_array_as_str(self):
        if self._df is None or "epoch_time_stamp" not in self._df:
            return np.array([])
        if "epoch_time_stamp_str" not in self._df:
            self._df["epoch_time_stamp_str"] = self._df["epoch_time_stamp"].astype(str)
        return self._df["epoch_time_stamp_str"].to_numpy()

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
    # Database utilities
    def get_available_symbols(self, db_path: str, table_name: str) -> List[str]:
        """Get list of available symbols in the database table"""
        try:
            conn = sqlite3.connect(db_path)
            query = f"SELECT DISTINCT {self._symbol_col} FROM {table_name} ORDER BY {self._symbol_col}"
            result = conn.execute(query).fetchall()
            conn.close()
            return [row[0] for row in result]
        except Exception as e:
            print(f"Error getting symbols: {e}")
            return []

    def get_available_tables(self, db_path: str) -> List[str]:
        """Get list of available tables in the database"""
        try:
            conn = sqlite3.connect(db_path)
            query = "SELECT name FROM sqlite_master WHERE type='table'"
            result = conn.execute(query).fetchall()
            conn.close()
            return [row[0] for row in result]
        except Exception as e:
            print(f"Error getting tables: {e}")
            return []

    def get_symbol_data_range(self, db_path: str, table_name: str, symbol: str) -> Optional[Tuple[str, str, int]]:
        """Get data range for a specific symbol"""
        try:
            conn = sqlite3.connect(db_path)
            query = f"""
            SELECT MIN({self._timestamp_col}), MAX({self._timestamp_col}), COUNT(*)
            FROM {table_name}
            WHERE {self._symbol_col} = ?
            """
            result = conn.execute(query, (symbol,)).fetchone()
            conn.close()

            if result and result[0]:
                return result
            return None
        except Exception as e:
            print(f"Error getting data range: {e}")
            return None

    def create_synthetic_data(self, n_bars: int, symbol: str = "SYNTHETIC"):
        """
        Create synthetic OHLCV data for testing purposes.

        Args:
            n_bars: Number of bars to generate
            symbol: Symbol name for the synthetic data
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
            current_time = datetime.now()
            timestamps = []
            for i in range(n_bars):
                timestamp = current_time - timedelta(hours=i)
                timestamps.append(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            timestamps.reverse()  # Make it chronological order

            # Generate sine-based close prices
            base_price = 5000  # Starting around 5000
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
                    self._symbol_col: symbol,
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

            # Set the same attributes that load_prices_from_sqlite sets
            self._last_db_path = f"synthetic_database.db"
            self._last_table = "synthetic_table"
            self._last_symbol = symbol
            self._bar_count = n_bars

            print(f"Generated synthetic data: {n_bars} bars for {symbol}")
            print(f"Price range: {self._df[self._close_col].min():.2f} - {self._df[self._close_col].max():.2f}")
            print(f"Time range: {timestamps[0]} to {timestamps[-1]}")

        return self._timeit("create_synthetic_data", _impl)