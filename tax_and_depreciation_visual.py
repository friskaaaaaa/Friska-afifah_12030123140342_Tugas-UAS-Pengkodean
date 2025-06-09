import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Fungsi untuk membaca data dari file CSV
def load_data(filename, data_string):
    """Membaca data dari string CSV"""
    return pd.read_csv(StringIO(data_string))

# Fungsi untuk menghitung pajak tarif normal
def tarif_normal(profit, tax_rate):
    """Menghitung pajak dengan tarif normal"""
    return profit * tax_rate

# Fungsi untuk menghitung pajak dengan tax holiday
def tax_holiday(profit, year, tax_rate, holiday_start, holiday_end):
    """Menghitung pajak dengan tax holiday"""
    if holiday_start <= year <= holiday_end:
        return 0
    return tarif_normal(profit, tax_rate)

# Fungsi untuk menghitung penyusutan garis lurus
def penyusutan_garis_lurus(asset_value, useful_life):
    """Menghitung penyusutan metode garis lurus"""
    return asset_value / useful_life

# Fungsi untuk menghitung penyusutan saldo menurun
def penyusutan_saldo_menurun(asset_value, useful_life, year):
    """Menghitung penyusutan metode saldo menurun"""
    straight_line_rate = 1 / useful_life
    declining_rate = 2 * straight_line_rate
    book_value = asset_value * (1 - declining_rate) ** (year - 1)
    depreciation = book_value * declining_rate
    return depreciation if depreciation > 0 else 0

# Data dari file CSV (disimulasikan sebagai string)
transaksi_data = """tahun,pendapatan,beban_operasional,penyusutan,skenario
2023,500000000,200000000,50000000,normal
2023,600000000,250000000,60000000,tax_holiday
2024,700000000,300000000,70000000,normal
2024,800000000,350000000,80000000,tax_holiday"""

kebijakan_data = """tahun,tax_rate,tax_holiday_awal,tax_holiday_akhir
2023,0.22,2023,2027
2024,0.22,2023,2027
2025,0.22,2023,2027"""

aset_data = """aset_id,kategori,nilai_perolehan,umur_ekonomis,metode
1,Mesin Jahit,100000000,5,garis_lurus
2,Kendaraan Operasional,150000000,4,saldo_menurun"""

# Membaca data
df_transaksi = load_data("transaksi_keuangan.csv", transaksi_data)
df_kebijakan = load_data("kebijakan_fiskal.csv", kebijakan_data)
df_aset = load_data("aset_tetap.csv", aset_data)

# Menghitung pajak untuk visualisasi
tax_data = []
for _, row in df_transaksi.iterrows():
    year = int(row["tahun"])
    pendapatan = float(row["pendapatan"])
    beban_operasional = float(row["beban_operasional"])
    penyusutan = float(row["penyusutan"])
    skenario = row["skenario"]
    
    # Hitung laba kena pajak
    profit = pendapatan - beban_operasional - penyusutan
    
    # Ambil kebijakan fiskal
    kebijakan = df_kebijakan[df_kebijakan["tahun"] == year]
    if kebijakan.empty:
        continue
    tax_rate = kebijakan["tax_rate"].iloc[0]
    holiday_start = int(kebijakan["tax_holiday_awal"].iloc[0])
    holiday_end = int(kebijakan["tax_holiday_akhir"].iloc[0])
    
    # Hitung pajak
    tax = tarif_normal(profit, tax_rate) if skenario == "normal" else tax_holiday(profit, year, tax_rate, holiday_start, holiday_end)
    tax_data.append({"tahun": year, "skenario": skenario, "pajak": tax})

# Menghitung penyusutan untuk visualisasi
depreciation_data = []
for _, row in df_aset.iterrows():
    aset_id = row["aset_id"]
    kategori = row["kategori"]
    nilai_perolehan = float(row["nilai_perolehan"])
    umur_ekonomis = int(row["umur_ekonomis"])
    metode = row["metode"]
    
    # Hitung penyusutan untuk setiap tahun (2023 dan 2024 untuk contoh)
    for year in [2023, 2024]:
        if metode == "garis_lurus":
            dep = penyusutan_garis_lurus(nilai_perolehan, umur_ekonomis)
        else:
            dep = penyusutan_saldo_menurun(nilai_perolehan, umur_ekonomis, year - 2022)  # Tahun relatif dari 2023
        depreciation_data.append({"aset_id": aset_id, "kategori": kategori, "tahun": year, "penyusutan": dep})

# Visualisasi dengan Matplotlib
# Diagram 1: Pajak per Skenario
plt.figure(figsize=(10, 6))
tax_df = pd.DataFrame(tax_data)
for skenario in tax_df["skenario"].unique():
    subset = tax_df[tax_df["skenario"] == skenario]
    plt.bar(subset["tahun"].astype(str) + " (" + skenario + ")", subset["pajak"], label=skenario, alpha=0.5)
plt.xlabel("Tahun (Skenario)")
plt.ylabel("Pajak (Rp)")
plt.title("Perbandingan Pajak: Tarif Normal vs Tax Holiday")
plt.legend()
plt.tight_layout()
plt.show()

# Diagram 2: Penyusutan Aset
plt.figure(figsize=(10, 6))
dep_df = pd.DataFrame(depreciation_data)
for kategori in dep_df["kategori"].unique():
    subset = dep_df[dep_df["kategori"] == kategori]
    plt.bar(subset["tahun"].astype(str) + " (" + kategori + ")", subset["penyusutan"], label=kategori, alpha=0.5)
plt.xlabel("Tahun (Kategori Aset)")
plt.ylabel("Penyusutan (Rp)")
plt.title("Penyusutan Aset: Garis Lurus vs Saldo Menurun")
plt.legend()
plt.tight_layout()
plt.show()