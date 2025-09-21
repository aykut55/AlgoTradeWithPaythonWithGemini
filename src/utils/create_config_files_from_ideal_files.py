
import os
import glob
import csv
import re
import json
from pathlib import Path

# .txt dosyalarının bulunduğu kaynak dizin
source_dir = r"D:\iDeal\Config"

# Yeni .csv dosyalarının oluşturulacağı temel dizin
target_dir = r"D:\Aykut\Projects\AlgoTradeWithPaythonWithGemini\config"

"""Sembol istatistiklerini CSV formatında oluşturur"""
symbols_dir_txt_files = r"D:\iDeal\ChartData\_Exports"
symbols_dir_csv_files = r"D:\Aykut\Projects\AlgoTradeWithPaythonWithGemini\data\csvFiles"

def parse_teminatlar_txt():
    """Teminatlar.txt dosyasını parse eder ve CSV formatında kaydeder"""
    input_file = os.path.join(source_dir, "Teminatlar.txt")
    output_file = os.path.join(target_dir, "teminatlar.csv")

    # Hedef dizini oluştur
    os.makedirs(target_dir, exist_ok=True)

    print(f"Parsing {input_file}...")

    with open(input_file, 'r', encoding='utf-8-sig') as infile:  # utf-8-sig BOM karakterini handle eder
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)

            # Teminat oranları açıklamaları (header comment)
            outfile.write("# Teminat Oranları:\n")
            outfile.write("# \n")
            outfile.write("# Bu dosya finansal araçlar için gerekli teminat oranlarını içerir.\n")
            outfile.write("# Teminat oranı, o finansal araçla işlem yapmak için gereken minimum nakit miktarıdır.\n")
            outfile.write("# \n")
            outfile.write("# === HİSSE SENETLERİ ===\n")
            outfile.write("# Ana hisse senetleri için teminat oranları (TL cinsinden)\n")
            outfile.write("# Örnek: AEFES için %14.5 teminat oranı\n")
            outfile.write("# \n")
            outfile.write("# === ENDEKSLER ===\n")
            outfile.write("# D_XU030D: BIST 30 endeks türevi\n")
            outfile.write("# D_XLBNKD: BIST Banka endeks türevi\n")
            outfile.write("# D_XSD25D: BIST Sürdürülebilirlik 25 endeks türevi\n")
            outfile.write("# \n")
            outfile.write("# === DÖVİZ ===\n")
            outfile.write("# USD cinsi teminat oranları (USD cinsinden)\n")
            outfile.write("# D_EURUSD: EUR/USD paritesi\n")
            outfile.write("# D_GBPUSD: GBP/USD paritesi\n")
            outfile.write("# \n")
            outfile.write("# === EMTIA/ALTIN ===\n")
            outfile.write("# D_XAUUSD: Altın (USD/ounce)\n")
            outfile.write("# D_XAGUSD: Gümüş (USD/ounce)\n")
            outfile.write("# D_XCUUSD: Bakır (USD)\n")
            outfile.write("# D_XPTUSD: Platin (USD/ounce)\n")
            outfile.write("# D_XPDUSD: Paladyum (USD/ounce)\n")
            outfile.write("#\n")

            # CSV başlıkları
            writer.writerow(['contract', 'margin_rate', 'currency', 'related_symbol'])

            for line_num, line in enumerate(infile, 1):
                line = line.strip()

                # Başlık satırını atla
                if line.startswith('Kontrat|') or not line:
                    continue

                # | ile ayır
                parts = line.split('|')
                if len(parts) >= 4:
                    contract = parts[0].strip()
                    margin_rate = parts[1].strip()
                    currency = parts[2].strip()
                    related_symbol = parts[3].strip()

                    if contract and margin_rate:
                        writer.writerow([contract, margin_rate, currency, related_symbol])
                else:
                    print(f"Warning: Line {line_num} has insufficient columns ({len(parts)}): {line}")

    print(f"Saved to {output_file}")
    return output_file


def parse_imkb_endeks_senetler_txt():
    """ImkbEndeksSenetler.txt dosyasını parse eder ve CSV formatında kaydeder"""
    input_file = os.path.join(source_dir, "ImkbEndeksSenetler.txt")
    output_file = os.path.join(target_dir, "bistEndeksBilesenleri.csv")

    # Hedef dizini oluştur
    os.makedirs(target_dir, exist_ok=True)

    print(f"Parsing {input_file}...")

    with open(input_file, 'r', encoding='utf-8') as infile:
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)

            # Endeks bileşenleri açıklamaları (header comment)
            outfile.write("# Endeks Bileşenleri (Hisse Senedi - Endeks İlişkisi):\n")
            outfile.write("# \n")
            outfile.write("# Bu dosya her hisse senedinin hangi endekslerde yer aldığını gösterir.\n")
            outfile.write("# \n")
            outfile.write("# === TEMEL ENDEKSLER ===\n")
            outfile.write("# XU030: BIST 30 - En likit 30 hisse\n")
            outfile.write("# XU050: BIST 50 - En likit 50 hisse\n")
            outfile.write("# XU100: BIST 100 - En likit 100 hisse\n")
            outfile.write("# XU500: BIST 500 - Geniş pazar endeksi\n")
            outfile.write("# XUTUM: BIST TÜM - Tüm hisseler\n")
            outfile.write("# \n")
            outfile.write("# === ÖZEL ENDEKSLER ===\n")
            outfile.write("# XYLDZ: BIST YILDIZ - Yıldız şirketler\n")
            outfile.write("# XHARZ: BIST HALKA ARZ - Halka arz edilen şirketler\n")
            outfile.write("# XSD25: BIST SÜRDÜRÜLEBİLİRLİK 25\n")
            outfile.write("# XSRDK: BIST KATILIM SÜRDÜRÜLEBİLİRLİK\n")
            outfile.write("# \n")
            outfile.write("# === SEKTÖREL ENDEKSLER ===\n")
            outfile.write("# XBANK: BIST BANKA\n")
            outfile.write("# XBLSM: BIST BİLİŞİM\n")
            outfile.write("# XELKT: BIST ELEKTRİK\n")
            outfile.write("# XGIDA: BIST GIDA İÇECEK\n")
            outfile.write("# XGMYO: BIST GAYRİMENKUL Y.O.\n")
            outfile.write("# XHOLD: BIST HOLDİNG VE YATIRIM\n")
            outfile.write("# XTEKS: BIST TEKSTİL DERİ\n")
            outfile.write("# XTAST: BIST TAŞ TOPRAK\n")
            outfile.write("#\n")

            # CSV başlıkları
            writer.writerow(['stock_symbol', 'indices'])

            for line_num, line in enumerate(infile, 1):
                line = line.strip()

                # [List] başlık satırını atla
                if line == '[List]' or not line:
                    continue

                # = ile ayır ve ; ile bitip bitmediğini kontrol et
                if '=' in line:
                    # Satır sonundaki ; varsa kaldır
                    if line.endswith(';'):
                        line = line[:-1]

                    parts = line.split('=', 1)  # Sadece ilk = ile ayır
                    if len(parts) == 2:
                        stock_symbol = parts[0].strip()
                        indices_str = parts[1].strip()

                        # Endeksleri virgülle ayır
                        indices_list = [idx.strip() for idx in indices_str.split(',') if idx.strip()]
                        indices_joined = ','.join(indices_list)

                        if stock_symbol and indices_joined:
                            writer.writerow([stock_symbol, indices_joined])
                else:
                    print(f"Warning: Line {line_num} doesn't contain '=' separator: {line}")

    print(f"Saved to {output_file}")
    return output_file


def parse_imkb_endeksler_txt():
    """ImkbEndeksler.txt dosyasını parse eder ve CSV formatında kaydeder"""
    input_file = os.path.join(source_dir, "ImkbEndeksler.txt")
    output_file = os.path.join(target_dir, "bistEndeksleri.csv")

    # Hedef dizini oluştur
    os.makedirs(target_dir, exist_ok=True)

    print(f"Parsing {input_file}...")

    with open(input_file, 'r', encoding='utf-8') as infile:
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)

            # Endeks türleri açıklamaları (header comment)
            outfile.write("# BIST Endeksleri:\n")
            outfile.write("# \n")
            outfile.write("# === ANA ENDEKSLER ===\n")
            outfile.write("# X030: BIST 30 - En büyük 30 şirket endeksi\n")
            outfile.write("# X100: BIST 100 - En büyük 100 şirket endeksi\n")
            outfile.write("# XBANA: BIST ANA - Ana pazar endeksi\n")
            outfile.write("# \n")
            outfile.write("# === SEKTÖREL ENDEKSLER ===\n")
            outfile.write("# XBANK: BIST BANKA - Bankacılık sektörü\n")
            outfile.write("# XBLSM: BIST BILISIM - Bilişim teknolojileri\n")
            outfile.write("# XELKT: BIST ELEKTRIK - Elektrik sektörü\n")
            outfile.write("# XGIDA: BIST GIDA ICECEK - Gıda ve içecek\n")
            outfile.write("# XGMYO: BIST GAYRIMENKUL Y.O. - Gayrimenkul yatırım ortaklıkları\n")
            outfile.write("# XHOLD: BIST HOLDING VE YATIRIM - Holding şirketleri\n")
            outfile.write("# XTEKS: BIST TEKSTIL DERI - Tekstil ve deri\n")
            outfile.write("# XTAST: BIST TAS TOPRAK - Taş ve toprak ürünleri\n")
            outfile.write("# \n")
            outfile.write("# === ÖZEL ENDEKSLER ===\n")
            outfile.write("# XSD25: BIST SURDURULEBILIRLIK 25 - Sürdürülebilirlik endeksi\n")
            outfile.write("# XSRDK: BIST KATILIM SURDURULEBILIRLIK - Katılım sürdürülebilirlik\n")
            outfile.write("# XSPOR: BIST SPOR - Spor sektörü\n")
            outfile.write("# \n")
            outfile.write("# === ŞEHİR ENDEKSLERI ===\n")
            outfile.write("# XSIST: BIST ISTANBUL - İstanbul şirketleri\n")
            outfile.write("# XSIZM: BIST IZMIR - İzmir şirketleri\n")
            outfile.write("# XSBUR: BIST BURSA - Bursa şirketleri\n")
            outfile.write("# XSKON: BIST KONYA - Konya şirketleri\n")
            outfile.write("#\n")

            # CSV başlıkları
            writer.writerow(['index_code', 'index_name'])

            for line_num, line in enumerate(infile, 1):
                line = line.strip()
                if not line:
                    continue

                # = ile ayır
                if '=' in line:
                    parts = line.split('=', 1)  # Sadece ilk = ile ayır
                    if len(parts) == 2:
                        index_code = parts[0].strip()
                        index_name = parts[1].strip()

                        if index_code and index_name:
                            writer.writerow([index_code, index_name])
                else:
                    print(f"Warning: Line {line_num} doesn't contain '=' separator: {line}")

    print(f"Saved to {output_file}")
    return output_file


def parse_semboller_txt():
    """_Semboller.txt dosyasını parse eder ve CSV formatında kaydeder"""
    input_file = os.path.join(source_dir, "_Semboller.txt")
    output_file = os.path.join(target_dir, "semboller.csv")

    # Hedef dizini oluştur
    os.makedirs(target_dir, exist_ok=True)

    print(f"Parsing {input_file}...")

    with open(input_file, 'r', encoding='utf-8') as infile:
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)

            # Sembol önekleri ve piyasa türleri açıklamaları (header comment)
            outfile.write("# Sembol Önekleri ve Piyasa Türleri:\n")
            outfile.write("# \n")
            outfile.write("# === ANA PIYASALAR ===\n")
            outfile.write("# IMKBH': IMKB HISSE - Borsa İstanbul Hisse Senetleri\n")
            outfile.write("# IMKBX': IMKB ENDEKS - Borsa İstanbul Endeksleri\n")
            outfile.write("# \n")
            outfile.write("# === TÜREV ÜRÜNLER ===\n")
            outfile.write("# VIP'O_: VADELI ISLEM VE OPSIYON - Opsiyon Sözleşmeleri\n")
            outfile.write("# VIP'TM_: VADELI ISLEM VE OPSIYON - Vadeli İşlem Sözleşmeleri (TürkMen)\n")
            outfile.write("# VIP'VIP: VADELI ISLEM VE OPSIYON - VIP Vadeli İşlem Sözleşmeleri\n")
            outfile.write("# \n")
            outfile.write("# === ULUSLARARASI PIYASALAR ===\n")
            outfile.write("# WBOND': DUNYA BONOLARI - Dünya Tahvil ve Forward Kurları\n")
            outfile.write("# WINX': DUNYA ENDEKSLERI - Dünya Borsası Endeksleri (DAX, FTSE, etc.)\n")
            outfile.write("# EUREX': EUREX - Avrupa Türev Borsası\n")
            outfile.write("# \n")
            outfile.write("# === DİĞER PIYASALAR ===\n")
            outfile.write("# FX': FX - Döviz Paritesi\n")
            outfile.write("# CRP': KRIPTO PARA - Kripto Para Birimleri\n")
            outfile.write("# BNKGS': BANKA GISE KURLARI - Banka Gişe Kurları\n")
            outfile.write("# KIYM': KIYMETLI MADENLER - Altın, Gümüş, Platin vb.\n")
            outfile.write("# NFT': NFT - Non Fungible Token\n")
            outfile.write("# \n")
            outfile.write("# === BANKACILIK VE FAİZ ===\n")
            outfile.write("# LIBOR': LIBOR - Londra Bankalararası Faiz Oranları\n")
            outfile.write("# INTUSD': INTERBANK - Bankalararası Dolar Piyasası\n")
            outfile.write("# OVERN': INTERBANK OVERNIGHT - Gecelik Faiz Oranları\n")
            outfile.write("# TCMBK': TCMB KURLAR - Merkez Bankası Kurları\n")
            outfile.write("# DOVIZ': DOVIZ BUROLARI - Döviz Büro Kurları\n")
            outfile.write("# \n")
            outfile.write("# === ÇEŞİTLİ ===\n")
            outfile.write("# DFN': CESITLI PIYASALAR - Çeşitli Finansal Araçlar\n")
            outfile.write("# SERPIY': SERBEST PIYASA - Serbest Piyasa İşlemleri\n")
            outfile.write("# FUTGCK': GECIKMELI VADELILER - Gecikmeli Vadeli İşlemler\n")
            outfile.write("# THVX': TAHVIL - Tahvil İşlemleri\n")
            outfile.write("#\n")

            # CSV başlıkları
            writer.writerow(['symbol', 'market_type', 'isin_code', 'company_name', 'sector_code', 'group_code', 'market_code'])

            for line_num, line in enumerate(infile, 1):
                line = line.strip()
                if not line:
                    continue

                parts = line.split('|')
                if len(parts) < 8:
                    print(f"Warning: Line {line_num} has insufficient columns ({len(parts)})")
                    continue

                # Ana sütunları çıkar
                symbol = parts[0].strip()
                market_type = parts[1].strip()
                type_code = parts[2].strip()
                isin_code = parts[3].strip() if len(parts) > 3 else ""
                company_name = parts[4].strip() if len(parts) > 4 else ""
                sector_code = parts[5].strip() if len(parts) > 5 else ""
                group_code = parts[6].strip() if len(parts) > 6 else ""
                market_code = parts[7].strip() if len(parts) > 7 else ""

                # Tüm sembolleri dahil et
                if symbol and market_type:  # Boş olmayan sembol ve piyasa tipi
                    writer.writerow([symbol, market_type, isin_code, company_name, sector_code, group_code, market_code])

    print(f"Saved to {output_file}")
    return output_file


def build_sembol_istatiskleri_from_txt_files():
    csv_output_file = os.path.join(target_dir, "sembolIstatistikleri.csv")
    json_output_file = os.path.join(target_dir, "sembolIstatistikleri.json")

    # Hedef dizini oluştur
    os.makedirs(target_dir, exist_ok=True)

    print(f"Scanning chart data files in {symbols_dir_txt_files}...")

    # Sembol bilgilerini tutacak map
    symbol_data_map = {}

    # ChartData/_Exports dizinindeki tüm .txt dosyalarını tara
    if os.path.exists(symbols_dir_txt_files):
        txt_files = glob.glob(os.path.join(symbols_dir_txt_files, "*.txt"))
        print(f"Found {len(txt_files)} chart data files...")

        for i, file_path in enumerate(txt_files, 1):
            # Progress display
            progress_percent = (i / len(txt_files)) * 100
            filename = os.path.basename(file_path)
            print(f"Processing {i}/{len(txt_files)} ({progress_percent:.1f}%): {filename}")

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # İlk 10 satırı oku (başlık bilgileri için yeterli)
                    lines = [f.readline().strip() for _ in range(10)]

                    # Veri çıkarma
                    kayit_zamani = ""
                    grafik_sembol = ""
                    grafik_periyot = ""
                    bar_count = ""
                    baslangic_tarihi = ""
                    bitis_tarihi = ""

                    for line in lines:
                        if "Kayit Zamani" in line and ":" in line:
                            kayit_zamani = line.split(":", 1)[1].strip()
                        elif "GrafikSembol" in line and ":" in line:
                            grafik_sembol = line.split(":", 1)[1].strip()
                        elif "GrafikPeriyot" in line and ":" in line:
                            grafik_periyot = line.split(":", 1)[1].strip()
                        elif "BarCount" in line and ":" in line:
                            bar_count = line.split(":", 1)[1].strip()
                        elif ("Başlangiç Tarihi" in line or "BaÅŸlangiÃ§ Tarihi" in line) and ":" in line:
                            baslangic_tarihi = line.split(":", 1)[1].strip()
                        elif ("Bitiş Tarihi" in line or "BitiÅŸ Tarihi" in line) and ":" in line:
                            bitis_tarihi = line.split(":", 1)[1].strip()

                    # Eğer gerekli veriler varsa map'e ekle
                    if grafik_sembol and grafik_periyot:
                        # Sembol anahtarı oluştur (sembol + periyot)
                        symbol_key = f"{grafik_sembol}_{grafik_periyot}"

                        symbol_data_map[symbol_key] = {
                            'grafik_sembol': grafik_sembol,
                            'grafik_periyot': grafik_periyot,
                            'bar_count': bar_count,
                            'baslangic_tarihi': baslangic_tarihi,
                            'bitis_tarihi': bitis_tarihi,
                            'kayit_zamani': kayit_zamani,
                            'dosya_adi': os.path.basename(file_path)
                        }

            except Exception as e:
                print(f"Warning: Error processing file {file_path}: {e}")
                continue

    print(f"Processed {len(symbol_data_map)} symbol-period combinations...")

    # Periyot sıralama fonksiyonu
    def get_period_sort_order(period):
        """Periyotları belirli sırada sıralamak için sort key döndürür"""
        period_order = ['1', '2', '3', '4', '5', '10', '15', '20', '30', '60', '120', '240', 'G', 'H']
        try:
            return period_order.index(period)
        except ValueError:
            return 999  # Bilinmeyen periyotları sona koy

    def sort_symbol_key(symbol_key):
        """Sembol anahtarını sıralamak için tuple döndürür: (sembol, periyot_order)"""
        parts = symbol_key.rsplit('_', 1)
        if len(parts) == 2:
            symbol, period = parts
            return (symbol, get_period_sort_order(period))
        return (symbol_key, 999)

    # JSON dosyasını oluştur
    print(f"Creating JSON file: {json_output_file}...")

    # Sembol gruplarını oluştur
    symbol_groups = {}
    for symbol_key in sorted(symbol_data_map.keys(), key=sort_symbol_key):
        data = symbol_data_map[symbol_key]
        grafik_sembol = data['grafik_sembol']

        # Eğer bu sembol için grup yoksa oluştur
        if grafik_sembol not in symbol_groups:
            symbol_groups[grafik_sembol] = []

        # Sembol grubuna veriyi ekle (grafik_sembol alanını çıkar)
        period_data = {
            'grafik_periyot': data['grafik_periyot'],
            'bar_count': data['bar_count'],
            'baslangic_tarihi': data['baslangic_tarihi'],
            'bitis_tarihi': data['bitis_tarihi'],
            'kayit_zamani': data['kayit_zamani'],
            'dosya_adi': data['dosya_adi']
        }
        symbol_groups[grafik_sembol].append(period_data)

    json_data = {
        "metadata": {
            "description": "Sembol istatistikleri - iDeal ChartData/_Exports klasöründeki dosyalardan çıkarılan sembol bilgileri",
            "total_records": len(symbol_data_map),
            "total_symbols": len(symbol_groups),
            "columns": {
                "grafik_periyot": "Grafik periyodu (1, 5, 15, 30, H, D vb.)",
                "bar_count": "Toplam bar/mum sayısı",
                "baslangic_tarihi": "Verinin başlangıç tarihi",
                "bitis_tarihi": "Verinin bitiş tarihi",
                "kayit_zamani": "Dosyanın kaydedildiği zaman",
                "dosya_adi": "Kaynak dosya adı"
            }
        },
        "data": symbol_groups
    }

    with open(json_output_file, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=2)

    print(f"Saved JSON file with {len(symbol_data_map)} records to {json_output_file}")

    # Formatlı CSV dosyasını oluştur
    print(f"Creating formatted CSV file: {csv_output_file}...")

    # Sütun genişliklerini hesapla
    col_widths = {
        'grafik_sembol': 25,
        'grafik_periyot': 8,
        'bar_count': 10,
        'baslangic_tarihi': 20,
        'bitis_tarihi': 20,
        'kayit_zamani': 20,
        'dosya_adi': 30
    }

    def format_field(field, width):
        """Alanı belirtilen genişlikte formatlama"""
        field_str = str(field) if field else ""
        return field_str.ljust(width)[:width]

    with open(csv_output_file, 'w', encoding='utf-8') as outfile:
        # Sembol istatistikleri açıklamaları (header comment)
        outfile.write("# Sembol İstatistikleri:\n")
        outfile.write("# \n")
        outfile.write("# Bu dosya iDeal ChartData/_Exports klasöründeki dosyalardan çıkarılan\n")
        outfile.write("# sembol bilgilerini içerir.\n")
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
        header_line = "# " + format_field("GRAFIK_SEMBOL", col_widths['grafik_sembol']) + \
                      format_field("PERIYOT", col_widths['grafik_periyot']) + \
                      format_field("BAR_COUNT", col_widths['bar_count']) + \
                      format_field("BASLANGIC_TARIHI", col_widths['baslangic_tarihi']) + \
                      format_field("BITIS_TARIHI", col_widths['bitis_tarihi']) + \
                      format_field("KAYIT_ZAMANI", col_widths['kayit_zamani']) + \
                      format_field("DOSYA_ADI", col_widths['dosya_adi']) + "\n"
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

        # Veri satırları (formatlı ve sıralı)
        for symbol_key in sorted(symbol_data_map.keys(), key=sort_symbol_key):
            data = symbol_data_map[symbol_key]

            data_line = "  " + format_field(data['grafik_sembol'], col_widths['grafik_sembol']) + \
                       format_field(data['grafik_periyot'], col_widths['grafik_periyot']) + \
                       format_field(data['bar_count'], col_widths['bar_count']) + \
                       format_field(data['baslangic_tarihi'], col_widths['baslangic_tarihi']) + \
                       format_field(data['bitis_tarihi'], col_widths['bitis_tarihi']) + \
                       format_field(data['kayit_zamani'], col_widths['kayit_zamani']) + \
                       format_field(data['dosya_adi'], col_widths['dosya_adi']) + "\n"
            outfile.write(data_line)

    print(f"Saved formatted CSV with {len(symbol_data_map)} records to {csv_output_file}")
    print(f"Both files created successfully!")
    return csv_output_file, json_output_file

def build_sembol_istatiskleri_from_csv_files():
    csv_output_file = os.path.join(target_dir, "sembolIstatistikleri.csv")
    json_output_file = os.path.join(target_dir, "sembolIstatistikleri.json")

    # Hedef dizini oluştur
    os.makedirs(target_dir, exist_ok=True)

    print(f"Scanning CSV files in {symbols_dir_csv_files}...")

    # Sembol bilgilerini tutacak map
    symbol_data_map = {}

    # csvFiles dizinindeki tüm alt klasörleri ve CSV dosyalarını tara
    if os.path.exists(symbols_dir_csv_files):
        all_csv_files = []

        # Tüm CSV dosyalarını bul
        for root, dirs, files in os.walk(symbols_dir_csv_files):
            for file in files:
                if file.endswith('.csv'):
                    all_csv_files.append(os.path.join(root, file))

        print(f"Found {len(all_csv_files)} CSV files...")

        for i, file_path in enumerate(all_csv_files, 1):
            # Progress display
            progress_percent = (i / len(all_csv_files)) * 100
            relative_path = os.path.relpath(file_path, symbols_dir_csv_files)
            print(f"Processing {i}/{len(all_csv_files)} ({progress_percent:.1f}%): {relative_path}")

            try:
                # Dosya yolundan sembol ve periyot bilgilerini çıkar
                # Örnek yol: D:\...\data\csvFiles\IMKBH\01\ADEL.csv
                path_parts = os.path.normpath(file_path).split(os.sep)

                # Son 3 bölümü al: market_type, period, symbol.csv
                if len(path_parts) >= 3:
                    market_type = path_parts[-3]  # IMKBH, IMKBX, VIP
                    grafik_periyot = path_parts[-2]  # 01, 05, 15, 30, 60, 120, 240, G, H
                    symbol_file = path_parts[-1]  # ADEL.csv
                    grafik_sembol = f"{market_type}'{os.path.splitext(symbol_file)[0]}"  # IMKBH'ADEL
                else:
                    print(f"Warning: Unexpected file path structure: {file_path}")
                    continue

                # CSV dosyasını oku ve header bilgilerini çıkar
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Header bilgilerini başlat
                    kayit_zamani = ""
                    grafik_sembol_from_header = ""
                    grafik_periyot_from_header = ""
                    bar_count = ""
                    baslangic_tarihi = ""
                    bitis_tarihi = ""

                    # İlk satırları oku ve header bilgilerini çıkar
                    for line_num in range(20):  # İlk 20 satırı kontrol et
                        line = f.readline().strip()
                        if not line:
                            break

                        # Header bilgilerini çıkar
                        if line.startswith("# Kayit_Zamani:"):
                            kayit_zamani = line.split(":", 1)[1].strip()
                        elif line.startswith("# GrafikSembol:"):
                            grafik_sembol_from_header = line.split(":", 1)[1].strip()
                        elif line.startswith("# GrafikPeriyot:"):
                            grafik_periyot_from_header = line.split(":", 1)[1].strip()
                        elif line.startswith("# BarCount:"):
                            bar_count = line.split(":", 1)[1].strip()
                        elif line.startswith("# Baslangic_Tarihi:"):
                            baslangic_tarihi = line.split(":", 1)[1].strip()
                        elif line.startswith("# Bitis_Tarihi:"):
                            bitis_tarihi = line.split(":", 1)[1].strip()
                        elif line.startswith("Date;Time;Open;High;Low;Close;Volume"):
                            # CSV başlığına ulaştık, header okuma tamamlandı
                            break

                    # Header'dan alınan bilgiler varsa bunları kullan
                    if grafik_sembol_from_header and grafik_periyot_from_header:
                        # Header'dan gelen sembol ve periyot bilgisini kullan
                        grafik_sembol = grafik_sembol_from_header
                        grafik_periyot = grafik_periyot_from_header
                    else:
                        # Header bilgisi yoksa dosya yolundan çıkar
                        print(f"Warning: No header info found in {relative_path}, using path info")
                        if len(path_parts) >= 3:
                            market_type = path_parts[-3]  # IMKBH, IMKBX, VIP
                            grafik_periyot = path_parts[-2]  # 01, 05, 15, 30, 60, 120, 240, G, H
                            symbol_file = path_parts[-1]  # ADEL.csv
                            grafik_sembol = f"{market_type}'{os.path.splitext(symbol_file)[0]}"  # IMKBH'ADEL
                        else:
                            print(f"Warning: Cannot extract symbol info from {file_path}")
                            continue

                    # Eğer header'da eksik bilgiler varsa dosya değişiklik zamanını kullan
                    if not kayit_zamani:
                        file_stat = os.stat(file_path)
                        import datetime
                        kayit_zamani = datetime.datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y.%m.%d %H:%M:%S')

                # Eğer gerekli veriler varsa map'e ekle
                if grafik_sembol and grafik_periyot:
                    # Sembol anahtarı oluştur (sembol + periyot)
                    symbol_key = f"{grafik_sembol}_{grafik_periyot}"

                    symbol_data_map[symbol_key] = {
                        'grafik_sembol': grafik_sembol,
                        'grafik_periyot': grafik_periyot,
                        'bar_count': bar_count,
                        'baslangic_tarihi': baslangic_tarihi,
                        'bitis_tarihi': bitis_tarihi,
                        'kayit_zamani': kayit_zamani,
                        'dosya_adi': os.path.basename(file_path)
                    }

            except Exception as e:
                print(f"Warning: Error processing file {file_path}: {e}")
                continue

    print(f"Processed {len(symbol_data_map)} symbol-period combinations...")

    # Periyot sıralama fonksiyonu
    def get_period_sort_order(period):
        """Periyotları belirli sırada sıralamak için sort key döndürür"""
        period_order = ['1', '01', '2', '02', '3', '03', '4', '04', '5', '05', '10', '15', '20', '30', '60', '120', '240', 'G', 'H']
        try:
            return period_order.index(period)
        except ValueError:
            return 999  # Bilinmeyen periyotları sona koy

    def sort_symbol_key(symbol_key):
        """Sembol anahtarını sıralamak için tuple döndürür: (sembol, periyot_order)"""
        parts = symbol_key.rsplit('_', 1)
        if len(parts) == 2:
            symbol, period = parts
            return (symbol, get_period_sort_order(period))
        return (symbol_key, 999)

    # JSON dosyasını oluştur
    print(f"Creating JSON file: {json_output_file}...")

    # Sembol gruplarını oluştur
    symbol_groups = {}
    for symbol_key in sorted(symbol_data_map.keys(), key=sort_symbol_key):
        data = symbol_data_map[symbol_key]
        grafik_sembol = data['grafik_sembol']

        # Eğer bu sembol için grup yoksa oluştur
        if grafik_sembol not in symbol_groups:
            symbol_groups[grafik_sembol] = []

        # Sembol grubuna veriyi ekle (grafik_sembol alanını çıkar)
        period_data = {
            'grafik_periyot': data['grafik_periyot'],
            'bar_count': data['bar_count'],
            'baslangic_tarihi': data['baslangic_tarihi'],
            'bitis_tarihi': data['bitis_tarihi'],
            'kayit_zamani': data['kayit_zamani'],
            'dosya_adi': data['dosya_adi']
        }
        symbol_groups[grafik_sembol].append(period_data)

    json_data = {
        "metadata": {
            "description": "Sembol istatistikleri - CSV dosyalarından çıkarılan sembol bilgileri",
            "total_records": len(symbol_data_map),
            "total_symbols": len(symbol_groups),
            "columns": {
                "grafik_periyot": "Grafik periyodu (01, 05, 15, 30, H, G vb.)",
                "bar_count": "Toplam bar/mum sayısı",
                "baslangic_tarihi": "Verinin başlangıç tarihi",
                "bitis_tarihi": "Verinin bitiş tarihi",
                "kayit_zamani": "Dosyanın kaydedildiği zaman",
                "dosya_adi": "Kaynak dosya adı"
            }
        },
        "data": symbol_groups
    }

    with open(json_output_file, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=2)

    print(f"Saved JSON file with {len(symbol_data_map)} records to {json_output_file}")

    # Formatlı CSV dosyasını oluştur
    print(f"Creating formatted CSV file: {csv_output_file}...")

    # Sütun genişliklerini hesapla
    col_widths = {
        'grafik_sembol': 25,
        'grafik_periyot': 8,
        'bar_count': 10,
        'baslangic_tarihi': 20,
        'bitis_tarihi': 20,
        'kayit_zamani': 20,
        'dosya_adi': 30
    }

    def format_field(field, width):
        """Alanı belirtilen genişlikte formatlama"""
        field_str = str(field) if field else ""
        return field_str.ljust(width)[:width]

    with open(csv_output_file, 'w', encoding='utf-8') as outfile:
        # Sembol istatistikleri açıklamaları (header comment)
        outfile.write("# Sembol İstatistikleri (CSV Dosyalarından):\n")
        outfile.write("# \n")
        outfile.write("# Bu dosya data/csvFiles klasöründeki CSV dosyalarından çıkarılan\n")
        outfile.write("# sembol bilgilerini içerir.\n")
        outfile.write("# \n")
        outfile.write("# === SÜTUN AÇIKLAMALARI ===\n")
        outfile.write("# grafik_sembol: Finansal araç sembolü (örn: IMKBH'ADEL)\n")
        outfile.write("# grafik_periyot: Grafik periyodu (01, 05, 15, 30, H, G vb.)\n")
        outfile.write("# bar_count: Toplam bar/mum sayısı\n")
        outfile.write("# baslangic_tarihi: Verinin başlangıç tarihi\n")
        outfile.write("# bitis_tarihi: Verinin bitiş tarihi\n")
        outfile.write("# kayit_zamani: Dosyanın son değişiklik zamanı\n")
        outfile.write("# dosya_adi: Kaynak dosya adı\n")
        outfile.write("#\n")
        outfile.write("# " + "="*150 + "\n")
        outfile.write("#\n")

        # Formatlı başlık satırı
        header_line = "# " + format_field("GRAFIK_SEMBOL", col_widths['grafik_sembol']) + \
                      format_field("PERIYOT", col_widths['grafik_periyot']) + \
                      format_field("BAR_COUNT", col_widths['bar_count']) + \
                      format_field("BASLANGIC_TARIHI", col_widths['baslangic_tarihi']) + \
                      format_field("BITIS_TARIHI", col_widths['bitis_tarihi']) + \
                      format_field("KAYIT_ZAMANI", col_widths['kayit_zamani']) + \
                      format_field("DOSYA_ADI", col_widths['dosya_adi']) + "\n"
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

        # Veri satırları (formatlı ve sıralı)
        for symbol_key in sorted(symbol_data_map.keys(), key=sort_symbol_key):
            data = symbol_data_map[symbol_key]

            data_line = "  " + format_field(data['grafik_sembol'], col_widths['grafik_sembol']) + \
                       format_field(data['grafik_periyot'], col_widths['grafik_periyot']) + \
                       format_field(data['bar_count'], col_widths['bar_count']) + \
                       format_field(data['baslangic_tarihi'], col_widths['baslangic_tarihi']) + \
                       format_field(data['bitis_tarihi'], col_widths['bitis_tarihi']) + \
                       format_field(data['kayit_zamani'], col_widths['kayit_zamani']) + \
                       format_field(data['dosya_adi'], col_widths['dosya_adi']) + "\n"
            outfile.write(data_line)

    print(f"Saved formatted CSV with {len(symbol_data_map)} records to {csv_output_file}")
    print(f"Both files created successfully!")
    return csv_output_file, json_output_file

def convert_files():
    """Tüm dosyaları dönüştür"""
    print("Starting file conversion...")

    # _Semboller.txt'yi işle
    parse_semboller_txt()

    # ImkbEndeksler.txt'yi işle
    parse_imkb_endeksler_txt()

    # ImkbEndeksSenetler.txt'yi işle
    parse_imkb_endeks_senetler_txt()

    # Teminatlar.txt'yi işle
    parse_teminatlar_txt()

    ## Sembol istatistiklerini oluştur (create_csv_files icinde yapiliyor...)
    ## build_sembol_istatiskleri_from_txt_files()

    # Sembol istatistiklerini oluştur (create_csv_files icinde yapiliyor...)
    # Sayet tekrardan olusturmak istenirse asagidaki satir ENABLE edilecek.
    # Mesala config klasöründeki dosyalar tekrardan olusturuluyor diye hepsi silinirse!
    # bu aşağısı ENABLE edilerek tekrardan oluşturulabilir.
    # build_sembol_istatiskleri_from_csv_files()

    print("Conversion completed!")

if __name__ == "__main__":
    convert_files()
