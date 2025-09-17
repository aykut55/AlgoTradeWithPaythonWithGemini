import os
import glob
import csv
import re
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# .txt dosyalarının bulunduğu kaynak dizin
source_dir = r"D:\iDeal\ChartData\_ExportsKeepMe"

# Yeni .sqlite dosyalarının oluşturulacağı temel dizin
target_base_dir = r"D:\Aykut\Projects\AlgoTradeWithPaythonWithGemini\data\sqlLite"

# Flagler - varsayılan olarak True
include_ids = False      # ID sütununu ekle/çıkar
include_header = False   # Header bilgilerini ekle/çıkar

# Progress flagleri
show_file_progress = True    # Dosyaların progress'ini göster
show_line_progress = False   # Her dosyadaki satırların progress'ini göster

# Test modu - sadece belirli semboller için (daha sonra silinecek)
TEST_MODE = False  # Test modu - sadece AKBNK sembolleri işle
TEST_SYMBOLS = ['AKBNK', 'YKBNK']  # Test edilecek semboller listesi

# Temizlik modu - mevcut db dosyalarını sil
CLEAN_DB_FILES = True  # Başlamadan önce mevcut .db dosyalarını sil

# Veri ayraç tipi - 'auto' (otomatik tespit), 'tab', 'space', ',' vb.
'''
  Kullanım seçenekleri:

  - 'auto' (varsayılan): TAB varsa TAB kullan, yoksa boşluk
  - 'tab': TAB karakteri zorunlu
  - 'space': Boşluk karakteri zorunlu
  - ',': Virgül ayraçlı
  - ';': Noktalı virgül ayraçlı
  - Herhangi başka karakter

  Bu şekilde dosya formatını biliyorsan manuel olarak ayarlayabilirsin:
  - TAB ayrılmış dosyalar için: data_separator = 'tab'
  - Virgülle ayrılmış için: data_separator = ','
  - Boşlukla ayrılmış için: data_separator = 'space'
'''
data_separator = 'auto'

# CSV çıktı ayraç tipi - ',' (virgül), ';' (noktalı virgül), '\t' (TAB)
csv_separator = ';'  # Ondalık virgüllerle uyumlu olması için

period_map = {
    "1": "01",
    "2": "02",
    "3": "03",
    "4": "04",
    "5": "05",
    "10": "10",
    "15": "15",
    "20": "20",
    "30": "30",
    "60": "60",
    "120": "120",
    "240": "240",
    "G": "G",
    "H": "H",
    "A": "A",
    "Y": "Y"
}

# SQLite configuration
BATCH_SIZE = 50000  # Daha büyük batch size
ENABLE_WAL_MODE = False  # WAL mode yerine MEMORY journal
ENABLE_PRAGMAS = True
VALIDATE_OHLC = False  # OHLC validation devre dışı (hız için)
SKIP_DUPLICATES = False  # Duplicate check devre dışı (hız için)

# Fast timeframes for separate databases
FAST_TIMEFRAMES = {'1', '5', '15', '60', 'G'}

# --- SQLite Helper Functions ---

def parse_filename(filename: str) -> Optional[Tuple[str, str, str]]:
    """Parse filename to extract exchange, symbol, period"""
    # Example: IMKBH'AEFES_5.txt -> ('IMKBH', 'AEFES', '5')
    pattern = r"([A-Z]+)'([A-Z0-9]+)_([A-Z0-9]+)\.txt"
    match = re.match(pattern, filename)

    if match:
        exchange, symbol, period = match.groups()
        return exchange, symbol, period
    return None

def get_db_path(exchange: str, period: str) -> str:
    """Determine which database file to use"""
    # Tüm dosyalar complete db'ye gidecek
    db_filename = f"{exchange}_complete.db"
    return os.path.join(target_base_dir, db_filename)

def get_table_name(period: str) -> str:
    """Generate table name from period"""
    mapped_period = period_map.get(period, period)
    if mapped_period.isdigit():
        return f"period_{mapped_period.zfill(2)}"
    else:
        return f"period_{mapped_period}"

def get_connection(db_path: str) -> sqlite3.Connection:
    """Get or create database connection with optimizations"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)

    if ENABLE_PRAGMAS:
        # Maximum performance optimizations
        conn.execute("PRAGMA journal_mode = MEMORY")  # En hızlı mode
        conn.execute("PRAGMA synchronous = OFF")  # Tamamen güvensiz ama hızlı
        conn.execute("PRAGMA cache_size = 100000")  # Daha büyük cache
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA mmap_size = 1073741824")  # 1GB memory map
        conn.execute("PRAGMA page_size = 65536")  # Büyük page size
        conn.execute("PRAGMA locking_mode = EXCLUSIVE")  # Exclusive lock

    return conn

def create_table_if_not_exists(conn: sqlite3.Connection, table_name: str):
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

def validate_ohlc_data(open_price: float, high: float, low: float, close: float) -> bool:
    """Validate OHLC data consistency"""
    if not VALIDATE_OHLC:
        return True

    # Basic validation rules
    if high < max(open_price, close) or low > min(open_price, close):
        return False
    if high < low:
        return False
    if any(x <= 0 for x in [open_price, high, low, close]):
        return False

    return True

def insert_records_batch(conn: sqlite3.Connection, table_name: str, symbol: str, records: List[Tuple]):
    """Insert records in batches with duplicate handling"""

    if not records:
        return 0

    # Prepare insert statement - daha hızlı INSERT
    if SKIP_DUPLICATES:
        insert_sql = f"""
        INSERT OR IGNORE INTO {table_name}
        (symbol, datetime, open, high, low, close, volume, lot)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
    else:
        insert_sql = f"""
        INSERT INTO {table_name}
        (symbol, datetime, open, high, low, close, volume, lot)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

    inserted_count = 0

    # Process in batches
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]

        # Add symbol to each record
        batch_with_symbol = [(symbol,) + record for record in batch]

        try:
            cursor = conn.cursor()
            cursor.executemany(insert_sql, batch_with_symbol)

            batch_inserted = cursor.rowcount
            inserted_count += batch_inserted

            conn.commit()

        except Exception as e:
            print(f"  Error inserting batch: {e}")
            conn.rollback()

    return inserted_count

# --- Betik ---

def parse_txt_file(file_path):
    """
    TXT dosyasını okur ve header bilgileri ile veri satırlarını ayrıştırır.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    lines = content.strip().split('\n')

    # Header bilgilerini parse et
    header_info = {}
    data_lines = []
    data_started = False

    for line in lines:
        line = line.strip()
        if not line or line.startswith('│'):
            continue

        # Önce veri satırını kontrol et (daha kesin)
        if re.match(r'^\s*\d+\s*\t', line) or re.match(r'^\s*\d+\s+\d{4}', line):
            data_started = True
            data_lines.append(line)
        # Header bilgilerini ayıkla (sadece veri başlamamışsa)
        elif ':' in line and not data_started:
            if 'Kayit Zamani' in line:
                header_info['Kayit_Zamani'] = line.split(':', 1)[1].strip()
            elif 'GrafikSembol' in line:
                header_info['GrafikSembol'] = line.split(':', 1)[1].strip()
            elif 'GrafikPeriyot' in line:
                header_info['GrafikPeriyot'] = line.split(':', 1)[1].strip()
            elif 'BarCount' in line:
                header_info['BarCount'] = line.split(':', 1)[1].strip()
            elif 'Başlangiç Tarihi' in line:
                header_info['Baslangic_Tarihi'] = line.split(':', 1)[1].strip()
            elif 'Bitiş Tarihi' in line:
                header_info['Bitis_Tarihi'] = line.split(':', 1)[1].strip()

    return header_info, data_lines

def parse_data_line(line, include_id=True, separator='auto'):
    """
    Veri satırını ayrıştırır ve sütunlara böler.
    Örnek: "0      2015.07.02 09:30:00    1,82   1,82   1,82   1,82        2769"
    veya TAB ayrılmış: "0 \t 2011.02.22 10:00:00 \t 0,43 \t 0,43 \t 0,42 \t 0,42 \t 265803 \t"

    separator: 'auto', 'tab', 'space', ',' vb.
    """
    # Ayraç tipine göre ayrıştır
    if separator == 'auto':
        # Otomatik tespit: TAB varsa TAB kullan, yoksa boşluk
        if '\t' in line:
            parts = [part.strip() for part in line.split('\t') if part.strip()]
        else:
            parts = line.strip().split()
    elif separator == 'tab':
        parts = [part.strip() for part in line.split('\t') if part.strip()]
    elif separator == 'space':
        parts = line.strip().split()
    else:
        # Özel ayraç (virgül, noktalı virgül vb.)
        parts = [part.strip() for part in line.split(separator) if part.strip()]

    if len(parts) < 6:
        return None

    id_num = parts[0]
    datetime_full = parts[1]  # '2011.02.22 10:00:00' formatında

    # Tarih ve zamanı ayır
    if ' ' in datetime_full:
        date, time = datetime_full.split(' ', 1)
    else:
        date, time = datetime_full, ''

    # Ondalık ayracı virgülden noktaya çevir (senin tercihin)
    open_price = parts[2].replace(',', '.')
    high_price = parts[3].replace(',', '.')
    low_price = parts[4].replace(',', '.')
    close_price = parts[5].replace(',', '.')
    volume = parts[6] if len(parts) > 6 else '0'
    lot = '0'  # Şu an için 0, daha sonra gerçek lot değeri eklenecek

    if include_id:
        return [id_num, date, time, open_price, high_price, low_price, close_price, volume, lot]
    else:
        return [date, time, open_price, high_price, low_price, close_price, volume, lot]

def clean_existing_db_files():
    """Mevcut .db dosyalarını sil"""
    if not CLEAN_DB_FILES:
        return

    if not os.path.exists(target_base_dir):
        print("Hedef dizin mevcut değil, temizlenecek dosya yok.")
        return

    # Mevcut .db dosyalarını bul
    db_files = glob.glob(os.path.join(target_base_dir, "*.db"))

    if not db_files:
        print("Silinecek .db dosyası bulunamadı.")
        return

    print(f"TEMIZLIK MODU: {len(db_files)} adet .db dosyası siliniyor...")

    deleted_count = 0
    for db_file in db_files:
        try:
            os.remove(db_file)
            print(f"  Silindi: {os.path.basename(db_file)}")
            deleted_count += 1
        except Exception as e:
            print(f"  HATA: {os.path.basename(db_file)} silinemedi: {e}")

    print(f"Toplam {deleted_count} dosya silindi.")

def convert_files():
    """
    .txt dosyalarını bulur, içeriklerini okur ve SQLite formatına dönüştürür.
    """
    print(f"SQLite dönüştürme işlemi başlıyor...")
    print(f"Kaynak Dizin: {source_dir}")
    print(f"Hedef Dizin: {target_base_dir}")

    # Hedef dizini oluştur
    os.makedirs(target_base_dir, exist_ok=True)
    print(f"Hedef dizin oluşturuldu: {target_base_dir}")

    # Mevcut DB dosyalarını temizle
    clean_existing_db_files()

    # Test modu bilgisi
    if TEST_MODE:
        print(f"TEST MODU AKTIF: Sadece {TEST_SYMBOLS} sembolleri işlenecek")
    else:
        print("NORMAL MOD: Tüm semboller işlenecek")

    # Kaynak dizindeki tüm .txt dosyalarını bul
    txt_files = glob.glob(os.path.join(source_dir, "*.txt"))

    if not txt_files:
        print("Kaynak dizinde .txt dosyası bulunamadı.")
        return

    print(f"İşlenecek {len(txt_files)} adet .txt dosyası bulundu.")

    # Statistics
    stats = {
        'files_processed': 0,
        'files_skipped': 0,
        'records_inserted': 0,
        'errors': 0
    }

    # Track database connections
    connections = {}

    start_time = time.time()

    try:
        for i, txt_file_path in enumerate(txt_files, 1):
            filename = os.path.basename(txt_file_path)

            # Progress göstergesi - dosyalar
            if show_file_progress:
                print(f"İşleniyor [{i}/{len(txt_files)}] ({(i/len(txt_files)*100):.1f}%): {filename}")
            else:
                print(f"İşleniyor: {filename}")

            try:
                # Parse filename
                parsed = parse_filename(filename)
                if not parsed:
                    print(f"  UYARI: '{filename}' dosya adı beklenen formatta değil. Atlanıyor.")
                    stats['files_skipped'] += 1
                    continue

                exchange, symbol, period = parsed

                # TEST MODE kontrolü - sadece TEST_SYMBOLS'daki sembolleri işle
                if TEST_MODE and symbol not in TEST_SYMBOLS:
                    print(f"  TEST MODE: '{symbol}' sembolu atlanıyor (TEST_SYMBOLS listesinde değil)")
                    stats['files_skipped'] += 1
                    continue

                print(f"  {exchange}.{symbol}.{period}")

                # Determine target database and table
                db_path = get_db_path(exchange, period)
                table_name = get_table_name(period)

                # Get or create connection
                if db_path not in connections:
                    connections[db_path] = get_connection(db_path)
                    print(f"  Veritabanı bağlantısı: {os.path.basename(db_path)}")

                conn = connections[db_path]

                # Create table if not exists
                create_table_if_not_exists(conn, table_name)

                # Parse TXT file
                header_info, data_lines = parse_txt_file(txt_file_path)
                print(f"  {len(data_lines)} veri satırı bulundu")

                if not data_lines:
                    print(f"  UYARI: '{filename}' dosyasında veri satırı bulunamadı.")
                    stats['files_skipped'] += 1
                    continue

                # Convert data lines to records
                records = []
                total_lines = len(data_lines)

                if show_line_progress:
                    print(f"  Veri satırları işleniyor...")

                for line_idx, data_line in enumerate(data_lines, 1):
                    # Progress göster sadece flag açıksa
                    if show_line_progress and (line_idx % 1000 == 0 or line_idx == total_lines):
                        progress_pct = (line_idx / total_lines) * 100
                        print(f"    Satır [{line_idx}/{total_lines}] ({progress_pct:.1f}%)")

                    parsed_data = parse_data_line(data_line, include_ids, data_separator)
                    if parsed_data:
                        # Create datetime string and extract values
                        if include_ids:
                            _, date, time_str, open_price, high_price, low_price, close_price, volume, lot = parsed_data
                        else:
                            date, time_str, open_price, high_price, low_price, close_price, volume, lot = parsed_data

                        # Combine date and time
                        datetime_str = f"{date} {time_str}"

                        # Convert to proper types
                        try:
                            open_val = float(open_price)
                            high_val = float(high_price)
                            low_val = float(low_price)
                            close_val = float(close_price)
                            volume_val = int(volume)
                            lot_val = int(lot)

                            # Validate OHLC
                            if not validate_ohlc_data(open_val, high_val, low_val, close_val):
                                continue

                            records.append((datetime_str, open_val, high_val, low_val, close_val, volume_val, lot_val))

                        except (ValueError, TypeError):
                            continue

                # Insert records
                if records:
                    inserted = insert_records_batch(conn, table_name, symbol, records)
                    stats['records_inserted'] += inserted
                    print(f"  BAŞARILI: {inserted} kayıt eklendi -> {os.path.basename(db_path)}.{table_name}")
                else:
                    print(f"  UYARI: '{filename}' dosyasında geçerli veri kaydı bulunamadı.")

                stats['files_processed'] += 1

                # Progress update every 100 files
                if i % 100 == 0:
                    elapsed = time.time() - start_time
                    print(f"  İlerleme: {i}/{len(txt_files)} dosya ({elapsed:.1f}s)")

            except Exception as e:
                print(f"  HATA: '{filename}' dosyası işlenirken hata oluştu: {e}")
                stats['errors'] += 1

    finally:
        # Close all connections
        for db_path, conn in connections.items():
            try:
                conn.close()
                print(f"Bağlantı kapatıldı: {os.path.basename(db_path)}")
            except Exception as e:
                print(f"Bağlantı kapatma hatası {db_path}: {e}")

    # Final statistics
    elapsed_total = time.time() - start_time
    print(f"\nToplam işlem süresi: {elapsed_total:.1f} saniye")

    print("\n=== DÖNÜŞTÜRME ÖZETİ ===")
    print(f"İşlenen dosya sayısı: {stats['files_processed']}")
    print(f"Eklenen kayıt sayısı: {stats['records_inserted']:,}")
    print(f"Atlanan dosya sayısı: {stats['files_skipped']}")
    print(f"Hata sayısı: {stats['errors']}")

    # Database file info
    if os.path.exists(target_base_dir):
        print(f"\nOluşturulan veritabanı dosyaları: {target_base_dir}")
        for db_file in glob.glob(os.path.join(target_base_dir, "*.db")):
            size_mb = os.path.getsize(db_file) / (1024 * 1024)
            print(f"  {os.path.basename(db_file)}: {size_mb:.1f} MB")

    print("=" * 30)


if __name__ == "__main__":
    convert_files()