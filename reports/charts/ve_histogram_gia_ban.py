
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path

# Đọc dữ liệu
duong_dan = Path("data/raw/bonbanh_raw.csv")
df = pd.read_csv(duong_dan)

# Chuyển giá bán sang dạng số
gia = pd.to_numeric(df["gia_ban"], errors="coerce")
gia = gia[gia > 0] / 1_000_000

# Tạo biểu đồ Histogram
plt.figure(figsize=(10, 6))

plt.hist(
    gia,
    bins=50,
    edgecolor="black",
    alpha=0.8
)

plt.title("Phân phối giá rao bán ô tô cũ", fontsize=14)
plt.xlabel("Giá rao bán (triệu đồng)", fontsize=11)
plt.ylabel("Số lượng tin đăng", fontsize=11)

plt.grid(axis="y", linestyle="--", alpha=0.3)

# Định dạng trục giá
plt.gca().xaxis.set_major_formatter(
    FuncFormatter(lambda x, _: f"{x:,.0f}")
)

plt.tight_layout()

# Lưu biểu đồ
duong_dan_luu = Path("reports/charts/histogram_gia_ban.png")
plt.savefig(duong_dan_luu, dpi=300, bbox_inches="tight")

plt.show()

print("Số tin đăng hợp lệ:", len(gia))
print("Giá thấp nhất:", round(gia.min(), 2), "triệu đồng")
print("Giá cao nhất:", round(gia.max(), 2), "triệu đồng")
print("Đã lưu biểu đồ tại:", duong_dan_luu)
