
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Đọc dữ liệu
df = pd.read_csv("data/raw/bonbanh_raw.csv")

# Chuyển đổi dữ liệu
df["nam_san_xuat_ct"] = pd.to_numeric(
    df["nam_san_xuat_ct"], errors="coerce"
)
df["gia_ban"] = pd.to_numeric(df["gia_ban"], errors="coerce")

df = df.dropna(subset=["nam_san_xuat_ct", "gia_ban"])
df = df[(df["gia_ban"] > 0) & (df["nam_san_xuat_ct"] >= 1990)]

# Chia nhóm năm sản xuất
cac_moc = [1990, 2005, 2010, 2015, 2020, 2027]
cac_nhom = [
    "1990–2005",
    "2006–2010",
    "2011–2015",
    "2016–2020",
    "2021–2026"
]

df["nhom_nam"] = pd.cut(
    df["nam_san_xuat_ct"],
    bins=cac_moc,
    labels=cac_nhom,
    include_lowest=True
)

# Tính giá trung vị
thong_ke = (
    df.groupby("nhom_nam", observed=False)["gia_ban"]
    .median()
    .div(1_000_000)
)

# Vẽ biểu đồ
plt.figure(figsize=(10, 6))

plt.bar(
    thong_ke.index.astype(str),
    thong_ke.values,
    edgecolor="black",
    alpha=0.85
)

plt.title("Giá trung vị theo nhóm năm sản xuất", fontsize=14)
plt.xlabel("Nhóm năm sản xuất", fontsize=11)
plt.ylabel("Giá trung vị (triệu đồng)", fontsize=11)

plt.grid(axis="y", linestyle="--", alpha=0.3)
plt.tight_layout()

# Lưu biểu đồ
duong_dan_luu = Path("reports/charts/gia_theo_nam_san_xuat.png")
plt.savefig(duong_dan_luu, dpi=300, bbox_inches="tight")
plt.show()

print("Giá trung vị theo nhóm năm (triệu đồng):")
print(thong_ke.round(2))
print("Số tin đăng mỗi nhóm:")
print(df.groupby("nhom_nam", observed=False).size())
print("Đã lưu biểu đồ tại:", duong_dan_luu)
