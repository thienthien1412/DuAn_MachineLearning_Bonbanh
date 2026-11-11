import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

df = pd.read_csv("data/raw/bonbanh_raw.csv")
df["gia_ban"] = pd.to_numeric(df["gia_ban"], errors="coerce")
df = df.dropna(subset=["gia_ban", "kieu_dang"])
df = df[df["gia_ban"] > 0]

thong_ke = (
    df.groupby("kieu_dang")["gia_ban"]
    .median()
    .div(1_000_000)
    .sort_values()
)

plt.figure(figsize=(10, 6))
plt.barh(thong_ke.index, thong_ke.values, edgecolor="black", alpha=0.85)

plt.title("Giá trung vị theo kiểu dáng ô tô", fontsize=14)
plt.xlabel("Giá trung vị (triệu đồng)")
plt.ylabel("Kiểu dáng")
plt.grid(axis="x", linestyle="--", alpha=0.3)
plt.tight_layout()

duong_dan = Path("reports/charts/gia_theo_kieu_dang.png")
plt.savefig(duong_dan, dpi=300, bbox_inches="tight")
plt.show()

print(thong_ke.round(2))
print("Đã lưu biểu đồ tại:", duong_dan)