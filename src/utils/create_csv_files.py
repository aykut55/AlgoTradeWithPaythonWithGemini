
import os
import glob
import csv
import re
from pathlib import Path

# .txt dosyalarının bulunduğu kaynak dizin
source_dir = r"D:\iDeal\ChartData\_ExportsKeepMe"

# Yeni .csv dosyalarının oluşturulacağı temel dizin
target_base_dir = r"D:\iDeal\ChartData\_csvFiles"

# Flagler - varsayılan olarak True
include_ids = False      # ID sütununu ekle/çıkar
include_header = False   # Header bilgilerini ekle/çıkar

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

def convert_files():
    """
    .txt dosyalarını bulur, içeriklerini okur ve CSV formatına dönüştürür.
    Header bilgileri de CSV'ye dahil edilir.
    """
    print(f"Dosya dönüştürme işlemi başlıyor...")
    print(f"Kaynak Dizin: {source_dir}")
    print(f"Hedef Dizin: {target_base_dir}")

    # Hedef dizini oluştur
    os.makedirs(target_base_dir, exist_ok=True)
    print(f"Hedef dizin oluşturuldu: {target_base_dir}")

    # Kaynak dizindeki tüm .txt dosyalarını bul
    txt_files = glob.glob(os.path.join(source_dir, "*.txt"))

    if not txt_files:
        print("Kaynak dizinde .txt dosyası bulunamadı.")
        return

    print(f"İşlenecek {len(txt_files)} adet .txt dosyası bulundu.")
    
    files_created = 0
    files_skipped = 0

    for i, txt_file_path in enumerate(txt_files, 1):
        file_name = Path(txt_file_path).stem

        # Progress göstergesi
        print(f"İşleniyor [{i}/{len(txt_files)}] ({(i/len(txt_files)*100):.1f}%): {file_name}")

        try:
            # TXT dosyasını okuyup parse et
            header_info, data_lines = parse_txt_file(txt_file_path)
            
            # Kaç veri satırı bulundu
            print(f"  {len(data_lines)} veri satiri bulundu")
            
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
            target_subdir = period_map.get(period_suffix)

            if not target_subdir or target_subdir == "":
                print(f"  UYARI: '{file_name}.txt' dosyasindaki '{period_suffix}' periyot soneki icin haritada eslestirme bulunamadi. Atlaniyor.")
                files_skipped += 1
                continue

            # Hedef dizinin tam yolunu oluştur
            target_dir = Path(target_base_dir) / main_dir_part / target_subdir
            
            # Dizin yapısı yoksa oluştur
            target_dir.mkdir(parents=True, exist_ok=True)

            # Hedef .csv dosyasının tam yolunu oluştur
            target_csv_path = target_dir / f"{symbol_part}.csv"

            # CSV dosyasını oluştur
            with open(target_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                
                # Header bilgilerini yaz (flag'e göre)
                if include_header:
                    csvfile.write('# Header Information\n')
                    for key, value in header_info.items():
                        csvfile.write(f'# {key}: {value}\n')
                    csvfile.write('\n')  # Boş satır
                
                # Sütun başlıklarını yaz (ID flag'ine göre)
                if include_ids:
                    csvfile.write(f'id{csv_separator}Date{csv_separator}Time{csv_separator}Open{csv_separator}High{csv_separator}Low{csv_separator}Close{csv_separator}Volume{csv_separator}Lot\n')
                else:
                    csvfile.write(f'Date{csv_separator}Time{csv_separator}Open{csv_separator}High{csv_separator}Low{csv_separator}Close{csv_separator}Volume{csv_separator}Lot\n')
                
                # Veri satırlarını yaz
                for data_line in data_lines:
                    parsed_data = parse_data_line(data_line, include_ids, data_separator)
                    if parsed_data:
                        csvfile.write(csv_separator.join(parsed_data) + '\n')
            
            print(f"  BASARILI: {target_csv_path}")
            files_created += 1

        except Exception as e:
            print(f"  HATA: '{file_name}.txt' dosyasi islenirken hata olustu: {e}. Atlaniyor.")
            files_skipped += 1

    print("\n--- Dönüştürme Özeti ---")
    print(f"Toplam bulunan .txt dosyası: {len(txt_files)}")
    print(f"Başarıyla oluşturulan .csv dosyası: {files_created}")
    print(f"Atlanan dosya sayısı (adlandırma veya eşleştirme sorunları nedeniyle): {files_skipped}")
    print("--------------------------")


if __name__ == "__main__":
    convert_files()
