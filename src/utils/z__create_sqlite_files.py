#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChartData SQLite Converter
Converts TXT OHLCV files to optimized SQLite databases for financial analysis.

Author: Claude Code
Date: 2025-09-17
"""

import os
import sqlite3
import glob
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time

class SQLiteConfig:
    """Configuration class for SQLite conversion"""

    # Paths
    SOURCE_DIR = r"D:\iDeal\ChartData\_ExportsKeepMe"
    SQLITE_TARGET = r"D:\iDeal\ChartData\_sqlLite"

    # Fast DB timeframes (most used for analysis)
    FAST_TIMEFRAMES = {'1', '5', '15', '60', 'G'}

    # SQLite options
    BATCH_SIZE = 10000
    ENABLE_WAL_MODE = True  # Write-Ahead Logging for better performance
    ENABLE_PRAGMAS = True   # Performance pragmas

    # Data validation
    VALIDATE_OHLC = True
    SKIP_DUPLICATES = True

class SQLiteConverter:
    """Main converter class for TXT to SQLite conversion"""

    def __init__(self, config: SQLiteConfig = None):
        self.config = config or SQLiteConfig()
        self.connections: Dict[str, sqlite3.Connection] = {}
        self.stats = {
            'files_processed': 0,
            'records_inserted': 0,
            'errors': 0,
            'skipped_duplicates': 0
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all_connections()

    def parse_filename(self, filename: str) -> Optional[Tuple[str, str, str]]:
        """Parse filename to extract exchange, symbol, period"""
        # Example: IMKBH'AEFES_5.txt -> ('IMKBH', 'AEFES', '5')
        pattern = r"([A-Z]+)'([A-Z0-9]+)_([A-Z0-9]+)\.txt"
        match = re.match(pattern, filename)

        if match:
            exchange, symbol, period = match.groups()
            return exchange, symbol, period
        return None

    def get_db_path(self, exchange: str, period: str) -> str:
        """Determine which database file to use"""
        db_type = 'fast' if period in self.config.FAST_TIMEFRAMES else 'complete'
        db_filename = f"{exchange}_{db_type}.db"
        return os.path.join(self.config.SQLITE_TARGET, db_filename)

    def get_table_name(self, period: str) -> str:
        """Generate table name from period"""
        if period.isdigit():
            return f"period_{period.zfill(2)}"
        else:
            return f"period_{period}"

    def get_connection(self, db_path: str) -> sqlite3.Connection:
        """Get or create database connection with optimizations"""
        if db_path not in self.connections:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            conn = sqlite3.connect(db_path)

            if self.config.ENABLE_PRAGMAS:
                # Performance optimizations
                conn.execute("PRAGMA journal_mode = WAL" if self.config.ENABLE_WAL_MODE else "PRAGMA journal_mode = MEMORY")
                conn.execute("PRAGMA synchronous = NORMAL")
                conn.execute("PRAGMA cache_size = 10000")
                conn.execute("PRAGMA temp_store = MEMORY")
                conn.execute("PRAGMA mmap_size = 268435456")  # 256MB

            self.connections[db_path] = conn

        return self.connections[db_path]

    def create_table_if_not_exists(self, conn: sqlite3.Connection, table_name: str):
        """Create table with optimized schema for analysis"""

        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            datetime TEXT NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER NOT NULL,
            lot INTEGER DEFAULT 0,

            -- Calculated columns for analysis
            price_change REAL GENERATED ALWAYS AS (close - open) STORED,
            price_change_pct REAL GENERATED ALWAYS AS (
                CASE WHEN open > 0 THEN ((close - open) / open * 100) ELSE 0 END
            ) STORED,

            UNIQUE(symbol, datetime)
        )
        """

        conn.execute(create_sql)

        # Create indexes for fast queries
        indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_symbol_datetime ON {table_name}(symbol, datetime)",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_datetime ON {table_name}(datetime)",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_symbol_volume ON {table_name}(symbol, volume)",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_close_range ON {table_name}(close, datetime)"
        ]

        for index_sql in indexes:
            conn.execute(index_sql)

        conn.commit()

    def validate_ohlc_data(self, open_price: float, high: float, low: float, close: float) -> bool:
        """Validate OHLC data consistency"""
        if not self.config.VALIDATE_OHLC:
            return True

        # Basic validation rules
        if high < max(open_price, close) or low > min(open_price, close):
            return False
        if high < low:
            return False
        if any(x <= 0 for x in [open_price, high, low, close]):
            return False

        return True

    def parse_txt_file(self, file_path: str) -> List[Tuple]:
        """Parse TXT file and return list of data tuples"""
        records = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # Split by tab or multiple spaces
                    parts = re.split(r'\t+|\s{2,}', line)

                    if len(parts) < 7:
                        continue

                    try:
                        # Parse fields (assuming: Date, Time, Open, High, Low, Close, Volume)
                        date_str = parts[0]
                        time_str = parts[1]
                        open_price = float(parts[2].replace(',', '.'))
                        high = float(parts[3].replace(',', '.'))
                        low = float(parts[4].replace(',', '.'))
                        close = float(parts[5].replace(',', '.'))
                        volume = int(parts[6])
                        lot = int(parts[7]) if len(parts) > 7 else 0

                        # Combine date and time
                        datetime_str = f"{date_str} {time_str}"

                        # Validate OHLC
                        if not self.validate_ohlc_data(open_price, high, low, close):
                            print(f"  Warning: Invalid OHLC data at line {line_num}: {line[:50]}...")
                            continue

                        records.append((datetime_str, open_price, high, low, close, volume, lot))

                    except (ValueError, IndexError) as e:
                        print(f"  Warning: Parse error at line {line_num}: {e}")
                        continue

        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            self.stats['errors'] += 1

        return records

    def insert_records_batch(self, conn: sqlite3.Connection, table_name: str,
                           symbol: str, records: List[Tuple]):
        """Insert records in batches with duplicate handling"""

        if not records:
            return

        # Prepare insert statement
        insert_sql = f"""
        INSERT OR IGNORE INTO {table_name}
        (symbol, datetime, open, high, low, close, volume, lot)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Process in batches
        for i in range(0, len(records), self.config.BATCH_SIZE):
            batch = records[i:i + self.config.BATCH_SIZE]

            # Add symbol to each record
            batch_with_symbol = [(symbol,) + record for record in batch]

            try:
                cursor = conn.cursor()
                cursor.executemany(insert_sql, batch_with_symbol)

                inserted_count = cursor.rowcount
                self.stats['records_inserted'] += inserted_count

                if self.config.SKIP_DUPLICATES and inserted_count < len(batch):
                    self.stats['skipped_duplicates'] += len(batch) - inserted_count

                conn.commit()

            except Exception as e:
                print(f"  Error inserting batch: {e}")
                self.stats['errors'] += 1
                conn.rollback()

    def process_file(self, file_path: str):
        """Process single TXT file"""
        filename = os.path.basename(file_path)

        # Parse filename
        parsed = self.parse_filename(filename)
        if not parsed:
            print(f"Skipping file with invalid name format: {filename}")
            return

        exchange, symbol, period = parsed

        print(f"Processing: {filename} -> {exchange}.{symbol}.{period}")

        # Determine target database and table
        db_path = self.get_db_path(exchange, period)
        table_name = self.get_table_name(period)

        # Get connection and create table
        conn = self.get_connection(db_path)
        self.create_table_if_not_exists(conn, table_name)

        # Parse and insert data
        records = self.parse_txt_file(file_path)

        if records:
            self.insert_records_batch(conn, table_name, symbol, records)
            print(f"  Inserted {len(records)} records into {os.path.basename(db_path)}.{table_name}")
        else:
            print(f"  No valid records found in {filename}")

        self.stats['files_processed'] += 1

    def close_all_connections(self):
        """Close all database connections"""
        for db_path, conn in self.connections.items():
            try:
                conn.close()
                print(f"Closed connection to {os.path.basename(db_path)}")
            except Exception as e:
                print(f"Error closing connection to {db_path}: {e}")

        self.connections.clear()

    def print_stats(self):
        """Print conversion statistics"""
        print("\n" + "="*60)
        print("CONVERSION STATISTICS")
        print("="*60)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Records inserted: {self.stats['records_inserted']:,}")
        print(f"Skipped duplicates: {self.stats['skipped_duplicates']:,}")
        print(f"Errors: {self.stats['errors']}")

        # Database file info
        if os.path.exists(self.config.SQLITE_TARGET):
            print(f"\nDatabase files created in: {self.config.SQLITE_TARGET}")
            for db_file in glob.glob(os.path.join(self.config.SQLITE_TARGET, "*.db")):
                size_mb = os.path.getsize(db_file) / (1024 * 1024)
                print(f"  {os.path.basename(db_file)}: {size_mb:.1f} MB")

def main():
    """Main conversion function"""
    print("ChartData SQLite Converter")
    print("=" * 40)

    config = SQLiteConfig()

    # Find all TXT files
    pattern = os.path.join(config.SOURCE_DIR, "*.txt")
    txt_files = glob.glob(pattern)

    if not txt_files:
        print(f"No TXT files found in: {config.SOURCE_DIR}")
        return

    print(f"Found {len(txt_files)} TXT files to process")
    print(f"Target directory: {config.SQLITE_TARGET}")
    print(f"Fast timeframes: {', '.join(sorted(config.FAST_TIMEFRAMES))}")
    print()

    start_time = time.time()

    # Process files
    with SQLiteConverter(config) as converter:
        for i, file_path in enumerate(txt_files, 1):
            print(f"[{i:4}/{len(txt_files)}] ", end="")
            converter.process_file(file_path)

            # Progress update every 100 files
            if i % 100 == 0:
                elapsed = time.time() - start_time
                print(f"  Progress: {i}/{len(txt_files)} files ({elapsed:.1f}s)")

    # Final statistics
    elapsed_total = time.time() - start_time
    print(f"\nTotal processing time: {elapsed_total:.1f} seconds")

    with SQLiteConverter(config) as converter:
        converter.print_stats()

if __name__ == "__main__":
    main()