
import os
import glob
import csv
import re
import json
from pathlib import Path
import shutil
import gc  # Garbage collection için

class CsvFileConverter:
    """
    TXT dosyalarını CSV formatına dönüştüren sınıf.
    """

    def __init__(self,
                 source_dir=r"D:\iDeal\ChartData\_Exports",
                 target_base_dir_csv=r"D:\Aykut\Projects\AlgoTradeWithPaythonWithGemini\data\csvFiles",
                 target_base_dir_txt=r"D:\Aykut\Projects\AlgoTradeWithPaythonWithGemini\data\txtFiles",
                 config_dir=r"D:\Aykut\Projects\AlgoTradeWithPaythonWithGemini\config",
                 include_ids=True,
                 include_header=True,
                 data_separator='auto',
                 csv_separator=';'):
        """
        Args:
            source_dir: .txt dosyalarının bulunduğu kaynak dizin
            target_base_dir_csv: .csv dosyalarının oluşturulacağı temel dizin
            target_base_dir_txt: .txt dosyalarının oluşturulacağı temel dizin
            config_dir: Sembol istatistikleri için config dizini
            include_ids: ID sütununu ekle/çıkar
            include_header: Header bilgilerini ekle/çıkar
            data_separator: Veri ayraç tipi - 'auto', 'tab', 'space', ',' vb.
            csv_separator: CSV çıktı ayraç tipi - ',', ';', '\t'
        """
        self.source_dir = source_dir
        self.target_base_dir_csv = target_base_dir_csv
        self.target_base_dir_txt = target_base_dir_txt
        self.config_dir = config_dir
        self.include_ids = include_ids
        self.include_header = include_header
        self.data_separator = data_separator
        self.csv_separator = csv_separator

        self.period_map = {
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

    def parse_txt_file_headers(self, file_path):
        """
        TXT dosyasını SADECE header bilgileri için okur (MEMORY OPTIMIZED).
        Veri satırlarını bellekte tutmaz, sadece sayar.
        """
        header_info = {}
        data_line_count = 0
        data_started = False

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('│'):
                    continue

                # Veri satırını kontrol et
                if re.match(r'^\s*\d+\s*\t', line) or re.match(r'^\s*\d+\s+\d{4}', line):
                    data_started = True
                    data_line_count += 1
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

        return header_info, data_line_count

    def parse_data_line(self, line, include_id=True, separator='auto'):
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
        lot = parts[7] if len(parts) > 7 else '0'

        if include_id:
            return [id_num, date, time, open_price, high_price, low_price, close_price, volume, lot]
        else:
            return [date, time, open_price, high_price, low_price, close_price, volume, lot]

    def write_csv_from_txt_streaming(self, txt_file_path, target_csv_path, header_info,
                                      include_header=True, include_ids=True,
                                      data_separator='auto', csv_separator=';'):
        """
        TXT dosyasını streaming olarak okuyup CSV'ye yazar (MEMORY OPTIMIZED).
        Tüm veri satırlarını bellekte tutmaz.
        """
        data_line_count = 0

        with open(target_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Header bilgilerini yaz (flag'e göre)
            if include_header:
                for key, value in header_info.items():
                    csvfile.write(f'# {key}: {value}\n')
                csvfile.write('# Format : Id Date Time Open High Low Close Volume Lot\n')
                csvfile.write('# Data\n')

            # TXT dosyasını satır satır oku ve CSV'ye yaz
            data_started = False
            with open(txt_file_path, 'r', encoding='utf-8') as txtfile:
                for line in txtfile:
                    line = line.strip()
                    if not line or line.startswith('│'):
                        continue

                    # Veri satırını kontrol et
                    if re.match(r'^\s*\d+\s*\t', line) or re.match(r'^\s*\d+\s+\d{4}', line):
                        data_started = True
                        parsed_data = self.parse_data_line(line, include_ids, data_separator)
                        if parsed_data:
                            csvfile.write(csv_separator.join(parsed_data) + '\n')
                            data_line_count += 1

        return data_line_count

    # --- Sembol İstatistikleri Helper Fonksiyonları ---

    @staticmethod
    def get_period_sort_order(period):
        """Periyotları belirli sırada sıralamak için sort key döndürür"""
        period_order = ['1', '2', '3', '4', '5', '10', '15', '20', '30', '60', '120', '240', 'G', 'H']
        try:
            return period_order.index(period)
        except ValueError:
            return 999  # Bilinmeyen periyotları sona koy

    @staticmethod
    def sort_symbol_periods(symbol_periods):
        """Sembol periyotlarını doğru sırada sıralar"""
        return sorted(symbol_periods, key=lambda x: CsvFileConverter.get_period_sort_order(x['grafik_periyot']))

    @staticmethod
    def write_symbol_statistics(symbol, symbol_periods, all_symbol_groups):
        """Bir sembolün istatistiklerini toplar ve gruplandırılmış yapıya ekler"""
        if not symbol_periods:
            return

        # Periyotları sırala
        sorted_periods = CsvFileConverter.sort_symbol_periods(symbol_periods)

        # Gruplandırılmış yapıya ekle
        all_symbol_groups[symbol] = sorted_periods

        print(f"  -> Sembol istatistikleri toplandi: {symbol} ({len(sorted_periods)} periyot)")

    @staticmethod
    def format_field(field, width):
        """Alanı belirtilen genişlikte formatlama"""
        field_str = str(field) if field else ""
        return field_str.ljust(width)[:width]

    def write_final_statistics(self, all_symbol_groups, total_files, files_created, files_skipped):
        """Tüm sembol istatistiklerini JSON ve formatlı CSV olarak yazar"""
        if not all_symbol_groups:
            print("Sembol istatistikleri bulunamadı.")
            return

        # Config dizinini oluştur
        os.makedirs(self.config_dir, exist_ok=True)

        csv_output_file = os.path.join(self.config_dir, "sembolIstatistikleri.csv")
        json_output_file = os.path.join(self.config_dir, "sembolIstatistikleri.json")

        total_records = sum(len(periods) for periods in all_symbol_groups.values())

        print(f"\n=== Sembol İstatistikleri Yazılıyor ===")
        print(f"Toplam sembol: {len(all_symbol_groups)}")
        print(f"Toplam kayıt: {total_records}")

        # JSON dosyasını oluştur
        print(f"JSON dosyası oluşturuluyor: {json_output_file}")
        json_data = {
            "metadata": {
                "description": "Sembol istatistikleri - CSV dönüştürme sırasında toplanan sembol bilgileri",
                "total_records": total_records,
                "total_symbols": len(all_symbol_groups),
                "source_files_processed": files_created,
                "source_files_total": total_files,
                "source_files_skipped": files_skipped,
                "columns": {
                    "grafik_periyot": "Grafik periyodu (01, 05, 15, 30, H, G vb.)",
                    "bar_count": "Toplam bar/mum sayısı",
                    "baslangic_tarihi": "Verinin başlangıç tarihi",
                    "bitis_tarihi": "Verinin bitiş tarihi",
                    "kayit_zamani": "Dosyanın kaydedildiği zaman",
                    "dosya_adi": "Kaynak dosya adı"
                }
            },
            "data": all_symbol_groups
        }

        with open(json_output_file, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=2)

        # Formatlı CSV dosyasını oluştur
        print(f"Formatlı CSV dosyası oluşturuluyor: {csv_output_file}")

        # Sütun genişlikleri
        col_widths = {
            'grafik_sembol': 25,
            'grafik_periyot': 8,
            'bar_count': 10,
            'baslangic_tarihi': 20,
            'bitis_tarihi': 20,
            'kayit_zamani': 20,
            'dosya_adi': 30
        }

        with open(csv_output_file, 'w', encoding='utf-8') as outfile:
            # Header açıklamaları
            outfile.write("# Sembol İstatistikleri:\n")
            outfile.write("# \n")
            outfile.write("# Bu dosya CSV dönüştürme sırasında toplanan sembol bilgilerini içerir.\n")
            outfile.write("# \n")
            outfile.write("# === SÜTUN AÇIKLAMALARI ===\n")
            outfile.write("# grafik_sembol: Finansal araç sembolü (örn: IMKBH'ADEL)\n")
            outfile.write("# grafik_periyot: Grafik periyodu (1, 5, 15, 30, H, D vb.)\n")
            outfile.write("# bar_count: Toplam bar/mum sayısı\n")
            outfile.write("# baslangic_tarihi: Verinin başlangıç tarihi\n")
            outfile.write("# bitis_tarihi: Verinin bitiş tarihi\n")
            outfile.write("# kayit_zamani: Dosyanın kaydedildiği zaman\n")
            outfile.write("# dosya_adi: Kaynak dosya adı\n")
            outfile.write("#\n")
            outfile.write("# " + "="*150 + "\n")
            outfile.write("#\n")

            # Formatlı başlık satırı
            header_line = "# " + CsvFileConverter.format_field("GRAFIK_SEMBOL", col_widths['grafik_sembol']) + \
                          CsvFileConverter.format_field("PERIYOT", col_widths['grafik_periyot']) + \
                          CsvFileConverter.format_field("BAR_COUNT", col_widths['bar_count']) + \
                          CsvFileConverter.format_field("BASLANGIC_TARIHI", col_widths['baslangic_tarihi']) + \
                          CsvFileConverter.format_field("BITIS_TARIHI", col_widths['bitis_tarihi']) + \
                          CsvFileConverter.format_field("KAYIT_ZAMANI", col_widths['kayit_zamani']) + \
                          CsvFileConverter.format_field("DOSYA_ADI", col_widths['dosya_adi']) + "\n"
            outfile.write(header_line)

            # Ayırıcı çizgi
            separator_line = "# " + "-" * col_widths['grafik_sembol'] + \
                            "-" * col_widths['grafik_periyot'] + \
                            "-" * col_widths['bar_count'] + \
                            "-" * col_widths['baslangic_tarihi'] + \
                            "-" * col_widths['bitis_tarihi'] + \
                            "-" * col_widths['kayit_zamani'] + \
                            "-" * col_widths['dosya_adi'] + "\n"
            outfile.write(separator_line)

            # Veri satırları (sıralı)
            for symbol in sorted(all_symbol_groups.keys()):
                periods = all_symbol_groups[symbol]
                for period_data in periods:
                    data_line = "  " + CsvFileConverter.format_field(symbol, col_widths['grafik_sembol']) + \
                               CsvFileConverter.format_field(period_data.get('grafik_periyot', ''), col_widths['grafik_periyot']) + \
                               CsvFileConverter.format_field(period_data.get('bar_count', ''), col_widths['bar_count']) + \
                               CsvFileConverter.format_field(period_data.get('baslangic_tarihi', ''), col_widths['baslangic_tarihi']) + \
                               CsvFileConverter.format_field(period_data.get('bitis_tarihi', ''), col_widths['bitis_tarihi']) + \
                               CsvFileConverter.format_field(period_data.get('kayit_zamani', ''), col_widths['kayit_zamani']) + \
                               CsvFileConverter.format_field(period_data.get('dosya_adi', ''), col_widths['dosya_adi']) + "\n"
                    outfile.write(data_line)

        print(f"✅ JSON dosyası oluşturuldu: {json_output_file}")
        print(f"✅ CSV dosyası oluşturuldu: {csv_output_file}")
        print(f"📊 {len(all_symbol_groups)} sembol, {total_records} kayıt işlendi")
        print("="*50)

    def convert_files(self, flagCopySrcFilesToDest=False, destDir=None):
        """
        .txt dosyalarını bulur, içeriklerini okur ve CSV formatına dönüştürür.
        Header bilgileri de CSV'ye dahil edilir.

        Args:
            flagCopySrcFilesToDest: Source txt dosyalarını kopyala
            destDir: Txt dosyalarının kopyalanacağı dizin.
                     None ise CSV'nin yanına kopyalar.
                     Dizin verilirse ayrı bir dizin yapısı oluşturur.
        """
        print(f"Dosya dönüştürme işlemi başlıyor...")
        print(f"Kaynak Dizin: {self.source_dir}")
        print(f"Hedef CSV Dizin: {self.target_base_dir_csv}")
        if flagCopySrcFilesToDest:
            if destDir:
                print(f"Hedef TXT Dizin: {destDir}")
            else:
                print(f"Hedef TXT Dizin: CSV dosyalarının yanında")

        # Hedef dizinleri oluştur
        os.makedirs(self.target_base_dir_csv, exist_ok=True)
        print(f"CSV hedef dizini oluşturuldu: {self.target_base_dir_csv}")

        if flagCopySrcFilesToDest and destDir:
            os.makedirs(destDir, exist_ok=True)
            print(f"TXT hedef dizini oluşturuldu: {destDir}")

        # Kaynak dizindeki tüm .txt dosyalarını bul ve sırala
        txt_files = glob.glob(os.path.join(self.source_dir, "*.txt"))
        txt_files.sort()  # Dosyaları sırala (sembol gruplarının birlikte gelmesi için)

        if not txt_files:
            print("Kaynak dizinde .txt dosyası bulunamadı.")
            return

        print(f"İşlenecek {len(txt_files)} adet .txt dosyası bulundu.")

        files_created = 0
        files_skipped = 0

        # Sembol istatistikleri için değişkenler
        all_symbol_groups = {}  # Tüm sembol grupları (memory'de tutulacak)
        current_symbol = None
        current_symbol_periods = []

        for i, txt_file_path in enumerate(txt_files, 1):
            file_name = Path(txt_file_path).stem

            # Progress göstergesi
            print(f"İşleniyor [{i}/{len(txt_files)}] ({(i/len(txt_files)*100):.1f}%): {file_name}")

            try:
                # TXT dosyasını okuyup SADECE header'ları parse et (MEMORY OPTIMIZED)
                header_info, data_line_count = self.parse_txt_file_headers(txt_file_path)

                # Kaç veri satırı bulundu
                print(f"  {data_line_count} veri satiri bulundu")

                # Dosya adını ayır. Örnek: "IMKBH'ACSEL_1" -> ['IMKBH', 'ACSEL', '1']
                # Tutarlı ayırma için tek tırnağı alt çizgiyle değiştirir.
                parts = file_name.replace("'", "_").split("_")

                if len(parts) < 2:
                    print(f"  UYARI: '{file_name}.txt' dosya adi beklenen formatta degil. Atlaniyor.")
                    files_skipped += 1
                    continue

                main_dir_part = parts[0]

                # Periyot sonekini ve sembolü al
                period_suffix = parts[-1]
                symbol_part = "_".join(parts[1:-1]) if len(parts) > 2 else parts[1]

                # Eşleştirme haritasından hedef alt dizini al
                target_subdir = self.period_map.get(period_suffix)

                if not target_subdir or target_subdir == "":
                    print(f"  UYARI: '{file_name}.txt' dosyasindaki '{period_suffix}' periyot soneki icin haritada eslestirme bulunamadi. Atlaniyor.")
                    files_skipped += 1
                    continue

                # Sembol istatistikleri için grafik sembolu oluştur
                grafik_sembol = header_info.get('GrafikSembol', f"{main_dir_part}'{symbol_part}")

                # Sembol değişti mi kontrol et
                if current_symbol and current_symbol != grafik_sembol:
                    # Önceki sembolün istatistiklerini yaz
                    CsvFileConverter.write_symbol_statistics(current_symbol, current_symbol_periods, all_symbol_groups)
                    current_symbol_periods.clear()

                # Yeni sembol
                current_symbol = grafik_sembol

                # Sembol istatistiklerini topla
                period_data = {
                    'grafik_periyot': period_suffix,
                    'bar_count': header_info.get('BarCount', str(data_line_count)),
                    'baslangic_tarihi': header_info.get('Baslangic_Tarihi', ''),
                    'bitis_tarihi': header_info.get('Bitis_Tarihi', ''),
                    'kayit_zamani': header_info.get('Kayit_Zamani', ''),
                    'dosya_adi': file_name + '.txt'
                }
                current_symbol_periods.append(period_data)

                # Hedef CSV dizininin tam yolunu oluştur
                target_dir = Path(self.target_base_dir_csv) / main_dir_part / target_subdir

                # Dizin yapısı yoksa oluştur
                target_dir.mkdir(parents=True, exist_ok=True)

                # Hedef .csv dosyasının tam yolunu oluştur
                target_csv_path = target_dir / f"{symbol_part}.csv"

                # CSV dosyasını streaming olarak yaz (MEMORY OPTIMIZED)
                actual_data_lines = self.write_csv_from_txt_streaming(
                    txt_file_path, target_csv_path, header_info,
                    self.include_header, self.include_ids, self.data_separator, self.csv_separator
                )

                # Source txt dosyasını kopyala
                if flagCopySrcFilesToDest and Path(target_csv_path).exists():
                    try:
                        if destDir is None:
                            # CSV'nin yanına kopyala (varsayılan davranış)
                            dest_txt_path = Path(target_csv_path).with_suffix('.txt')
                        else:
                            # Ayrı dizin yapısı oluştur (destDir/main_dir/period/symbol.txt)
                            dest_txt_dir = Path(destDir) / main_dir_part / target_subdir
                            dest_txt_dir.mkdir(parents=True, exist_ok=True)
                            dest_txt_path = dest_txt_dir / f"{symbol_part}.txt"

                        dest_txt_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(txt_file_path, dest_txt_path)
                        print(f'  -> TXT kopyalandı: {dest_txt_path}')
                    except Exception as e:
                        print(f'  UYARI: Kaynak dosya kopyalanamadı: {e}')

                # a = input("Press any key to cont...")

                print(f"  BASARILI: {target_csv_path}")
                files_created += 1

                # Garbage collection - Her 10 dosyada bir belleği temizle (MEMORY OPTIMIZED)
                if files_created % 10 == 0:
                    gc.collect()
                    print(f"  [GC] Bellek temizlendi (10 dosya işlendi)")

            except Exception as e:
                print(f"  HATA: '{file_name}.txt' dosyasi islenirken hata olustu: {e}. Atlaniyor.")
                files_skipped += 1

        # Son sembolün istatistiklerini yaz
        if current_symbol and current_symbol_periods:
            CsvFileConverter.write_symbol_statistics(current_symbol, current_symbol_periods, all_symbol_groups)

        print("\n--- Dönüştürme Özeti ---")
        print(f"Toplam bulunan .txt dosyası: {len(txt_files)}")
        print(f"Başarıyla oluşturulan .csv dosyası: {files_created}")
        print(f"Atlanan dosya sayısı (adlandırma veya eşleştirme sorunları nedeniyle): {files_skipped}")
        print("--------------------------")

        # Sembol istatistiklerini JSON ve CSV olarak yaz
        self.write_final_statistics(all_symbol_groups, len(txt_files), files_created, files_skipped)


if __name__ == "__main__":
    # Main seviyesinde path tanımları
    source_dir = r"D:\iDeal\ChartData\_Exports"
    target_base_dir_csv = r"D:\Aykut\Projects\AlgoTradeWithPaythonWithGemini\data\csvFiles"
    target_base_dir_txt = r"D:\Aykut\Projects\AlgoTradeWithPaythonWithGemini\data\txtFiles"
    config_dir = r"D:\Aykut\Projects\AlgoTradeWithPaythonWithGemini\config"

    # CsvFileConverter instance'ı oluştur - main seviyesindeki path'leri geç
    converter = CsvFileConverter(
        source_dir=source_dir,
        target_base_dir_csv=target_base_dir_csv,
        target_base_dir_txt=target_base_dir_txt,
        config_dir=config_dir
    )

    # Seçenek 1: CSV dosyalarının yanına txt kopyala (None veya parametresiz)
    # converter.convert_files(flagCopySrcFilesToDest=True)

    # Seçenek 2: Ayrı bir dizin yapısına txt kopyala
    converter.convert_files(flagCopySrcFilesToDest=True, destDir=target_base_dir_txt)

