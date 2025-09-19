
import os
import glob
import csv
import re
from pathlib import Path

# .txt dosyalarının bulunduğu kaynak dizin
source_dir = r"D:\iDeal\Config"

# Yeni .csv dosyalarının oluşturulacağı temel dizin
target_dir = r"D:\Aykut\Projects\AlgoTradeWithPaythonWithGemini\config"

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

    print("Conversion completed!")


if __name__ == "__main__":
    convert_files()
