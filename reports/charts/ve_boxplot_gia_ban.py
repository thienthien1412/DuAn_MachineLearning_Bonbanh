
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path

# 1. Đọc dữ liệu
du_lieu = pd.read_csv("data/raw/bonbanh_raw.csv")

# 2. Làm sạch cột giá bán để phục vụ biểu đồ
gia_ban = pd.to_numeric(
    du_lieu["gia_ban"],
    errors="coerce"
).dropna()

# Chỉ giữ giá bán lớn hơn 0 để sử dụng thang logarit
gia_ban = gia_ban[gia_ban > 0]

# Chuyển đơn vị từ đồng sang triệu đồng
gia_ban = gia_ban / 1_000_000

# 3. Tính các thống kê cơ bản
q1 = gia_ban.quantile(0.25)
q3 = gia_ban.quantile(0.75)
trung_vi = gia_ban.median()
iqr = q3 - q1
nguong_tren = q3 + 1.5 * iqr
so_ngoai_le = (gia_ban > nguong_tren).sum()

# 4. Tạo biểu đồ Boxplot
fig, ax = plt.subplots(figsize=(11, 5))

ax.boxplot(
    gia_ban,
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

# 5. Thiết lập trục và tiêu đề
ax.set_xscale("log")

ax.xaxis.set_major_formatter(
    FuncFormatter(lambda x, pos: f"{x:,.0f}")
)

ax.set_xlabel(
    "Giá bán (triệu đồng)",
    fontsize=11
)

ax.set_title(
    "Phân bố giá bán ô tô cũ",
    fontsize=14,
    fontweight="bold",
    pad=15
)

# Ẩn trục dọc vì chỉ có một nhóm dữ liệu
ax.set_yticks([])

# Định dạng lưới
ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.35
)

ax.set_axisbelow(True)

# 6. Hoàn thiện bố cục
plt.tight_layout()

# 7. Lưu biểu đồ
duong_dan = Path("reports/charts")
duong_dan.mkdir(parents=True, exist_ok=True)

plt.savefig(
    duong_dan / "boxplot_gia_ban.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# 8. In kết quả kiểm tra
print("\n===== THỐNG KÊ GIÁ BÁN =====")
print(f"Số bản ghi hợp lệ: {len(gia_ban):,}")
print(f"Q1: {q1:,.2f} triệu đồng")
print(f"Trung vị: {trung_vi:,.2f} triệu đồng")
print(f"Q3: {q3:,.2f} triệu đồng")
print(f"IQR: {iqr:,.2f} triệu đồng")
print(f"Ngưỡng ngoại lệ phía trên: {nguong_tren:,.2f} triệu đồng")
print(f"Số giá trị vượt ngưỡng trên: {so_ngoai_le:,}")
print("\nĐã lưu biểu đồ tại reports/charts/boxplot_gia_ban.png")
