
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path

# 1. Đọc dữ liệu
du_lieu = pd.read_csv("data/raw/bonbanh_raw.csv")

# 2. Chuyển số kilomet sang dạng số
so_km = (
    du_lieu["so_km_da_di"]
    .astype(str)
    .str.replace(r"[^\d]", "", regex=True)
)

so_km = pd.to_numeric(so_km, errors="coerce").dropna()

# 3. Giữ lại các giá trị kilomet từ 0 trở lên
so_km = so_km[so_km >= 0]

# 4. Tính các thống kê
q1 = so_km.quantile(0.25)
q3 = so_km.quantile(0.75)
trung_vi = so_km.median()
iqr = q3 - q1

nguong_duoi = q1 - 1.5 * iqr
nguong_tren = q3 + 1.5 * iqr

so_ngoai_le = (
    (so_km < nguong_duoi) |
    (so_km > nguong_tren)
).sum()

so_tren_1_trieu = (so_km >= 1_000_000).sum()

# 5. Tạo biểu đồ Boxplot
fig, ax = plt.subplots(figsize=(11, 5))

ax.boxplot(
    so_km,
    vert=False,
    showfliers=True,
    patch_artist=True,
    widths=0.45,
    boxprops={
        "facecolor": "#A8C7E8",
        "edgecolor": "#34495E",
        "linewidth": 1.3
    },
    medianprops={
        "color": "#E67E22",
        "linewidth": 2
    },
    whiskerprops={
        "color": "#34495E",
        "linewidth": 1.2
    },
    capprops={
        "color": "#34495E",
        "linewidth": 1.2
    },
    flierprops={
        "marker": "o",
        "markerfacecolor": "#E59866",
        "markeredgecolor": "none",
        "markersize": 3,
        "alpha": 0.45
    }
)

# 6. Thiết lập trục SymLog
ax.set_xscale("symlog", linthresh=1000, linscale=1)

cac_moc = [
    0, 1_000, 10_000, 100_000,
    1_000_000, 10_000_000,
    100_000_000, 1_000_000_000
]

ax.set_xticks(cac_moc)

def dinh_dang_truc(x, pos):
    if x == 0:
        return "0"
    if x >= 1_000_000_000:
        return f"{x / 1_000_000_000:g} tỷ"
    if x >= 1_000_000:
        return f"{x / 1_000_000:g} triệu"
    if x >= 1_000:
        return f"{x / 1_000:g} nghìn"
    return f"{x:,.0f}"

ax.xaxis.set_major_formatter(
    FuncFormatter(dinh_dang_truc)
)

# 7. Thiết lập tiêu đề và nhãn
ax.set_xlabel("Số kilomet đã đi (km)", fontsize=11)

ax.set_title(
    "Phân bố số kilomet đã đi của ô tô cũ",
    fontsize=14,
    fontweight="bold",
    pad=15
)

ax.set_yticks([])

ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.35
)

ax.set_axisbelow(True)

# 8. Lưu biểu đồ
plt.tight_layout()

duong_dan = Path("reports/charts")
duong_dan.mkdir(parents=True, exist_ok=True)

plt.savefig(
    duong_dan / "boxplot_so_km.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# 9. In kết quả thống kê
print("\n===== THỐNG KÊ SỐ KILOMET ĐÃ ĐI =====")
print(f"Số bản ghi hợp lệ: {len(so_km):,}")
print(f"Giá trị nhỏ nhất: {so_km.min():,.0f} km")
print(f"Trung vị: {trung_vi:,.0f} km")
print(f"Q1: {q1:,.0f} km")
print(f"Q3: {q3:,.0f} km")
print(f"Giá trị lớn nhất: {so_km.max():,.0f} km")
print(f"Số giá trị ngoại lệ theo IQR: {so_ngoai_le:,}")
print(f"Số bản ghi từ 1.000.000 km trở lên: {so_tren_1_trieu:,}")

print("\nĐã lưu biểu đồ tại reports/charts/boxplot_so_km.png")
