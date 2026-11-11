
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Đọc dữ liệu
df = pd.read_csv("data/raw/bonbanh_raw.csv")

# Tách hãng xe từ tên xe
def lay_hang_xe(ten_xe):
    ten_xe = str(ten_xe).strip().lower()

    cac_hang = {
        "mercedes-benz": ["mercedes-benz", "mercedes"],
        "mitsubishi": ["mitsubishi"],
        "vinfast": ["vinfast"],
        "toyota": ["toyota"],
        "hyundai": ["hyundai"],
        "ford": ["ford"],
        "kia": ["kia"],
        "mazda": ["mazda"],
        "lexus": ["lexus"],
        "honda": ["honda"]
    }

    for hang, tu_khoa in cac_hang.items():
        if any(tu in ten_xe for tu in tu_khoa):
            return hang.title() if hang != "mercedes-benz" else "Mercedes-Benz"

    return "Khác"

df["hang_xe"] = df["ten_xe"].apply(lay_hang_xe)
df["gia_ban"] = pd.to_numeric(df["gia_ban"], errors="coerce")

# Lọc 10 hãng xe trong bảng thống kê
cac_hang = [
    "Toyota", "Mercedes-Benz", "Hyundai", "Ford", "Kia",
    "Mazda", "Vinfast", "Mitsubishi", "Lexus", "Honda"
]

du_lieu = df[df["hang_xe"].isin(cac_hang)].copy()

# Tính giá trung vị theo hãng
thong_ke = (
    du_lieu.groupby("hang_xe")["gia_ban"]
    .median()
    .div(1_000_000)
    .sort_values()
)

# Vẽ biểu đồ thanh ngang
plt.figure(figsize=(10, 6))

plt.barh(
    thong_ke.index,
    thong_ke.values,
    edgecolor="black",
    alpha=0.85
)

plt.title("Giá trung vị theo hãng xe", fontsize=14)
plt.xlabel("Giá trung vị (triệu đồng)", fontsize=11)
plt.ylabel("Hãng xe", fontsize=11)

plt.grid(axis="x", linestyle="--", alpha=0.3)
plt.tight_layout()

# Lưu biểu đồ
duong_dan_luu = Path("reports/charts/gia_trung_vi_theo_hang.png")
plt.savefig(duong_dan_luu, dpi=300, bbox_inches="tight")
plt.show()

print("Số hãng xe:", len(thong_ke))
print(thong_ke.round(2))
print("Đã lưu biểu đồ tại:", duong_dan_luu)
