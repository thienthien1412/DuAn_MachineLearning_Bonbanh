
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Đọc dữ liệu
df = pd.read_csv("data/raw/bonbanh_raw.csv")

# Chuyển đổi giá bán
df["gia_ban"] = pd.to_numeric(df["gia_ban"], errors="coerce")

# Chuyển số kilomet từ văn bản sang số
df["so_km"] = (
    df["so_km_da_di"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.extract(r"(\d+)", expand=False)
)

df["so_km"] = pd.to_numeric(df["so_km"], errors="coerce")

# Lọc các giá trị hợp lệ
df = df.dropna(subset=["gia_ban", "so_km"])
df = df[(df["gia_ban"] > 0) & (df["so_km"] >= 0)]

# Chuyển giá sang triệu đồng
df["gia_trieu"] = df["gia_ban"] / 1_000_000

# Giới hạn hiển thị để tránh các giá trị cực lớn làm méo biểu đồ
df_ve = df[
    (df["so_km"] <= 500_000) &
    (df["gia_trieu"] <= 5_000)
]

# Vẽ biểu đồ phân tán
plt.figure(figsize=(10, 6))

plt.scatter(
    df_ve["so_km"],
    df_ve["gia_trieu"],
    alpha=0.25,
    s=12
)

plt.title("Mối quan hệ giữa số kilomet đã đi và giá rao bán", fontsize=13)
plt.xlabel("Số kilomet đã đi (km)", fontsize=11)
plt.ylabel("Giá rao bán (triệu đồng)", fontsize=11)

plt.grid(linestyle="--", alpha=0.3)
plt.tight_layout()

# Lưu biểu đồ
duong_dan_luu = Path("reports/charts/km_va_gia_ban.png")
plt.savefig(duong_dan_luu, dpi=300, bbox_inches="tight")
plt.show()

print("Tổng số tin đăng hợp lệ:", len(df))
print("Số tin đăng được hiển thị:", len(df_ve))
print("Số tin đăng không hiển thị:", len(df) - len(df_ve))
print("Đã lưu biểu đồ tại:", duong_dan_luu)
