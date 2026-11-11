
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Đọc dữ liệu
df = pd.read_csv("data/raw/bonbanh_raw.csv")

# Làm sạch dữ liệu
df["gia_ban"] = pd.to_numeric(df["gia_ban"], errors="coerce")

df = df.dropna(subset=["gia_ban", "khu_vuc"])
df = df[
    (df["gia_ban"] > 0) &
    (df["khu_vuc"].astype(str).str.strip() != "-")
]

# Chọn 10 khu vực có nhiều tin đăng nhất
top_khu_vuc = df["khu_vuc"].value_counts().head(10).index
du_lieu = df[df["khu_vuc"].isin(top_khu_vuc)].copy()

# Tính số tin đăng và giá trung vị
thong_ke = du_lieu.groupby("khu_vuc").agg(
    so_tin=("gia_ban", "count"),
    gia_trung_vi=("gia_ban", "median")
)

thong_ke["gia_trung_vi"] /= 1_000_000
thong_ke = thong_ke.sort_values("gia_trung_vi")

# Tạo biểu đồ
fig, ax = plt.subplots(figsize=(12, 7))

cac_cot = ax.barh(
    thong_ke.index,
    thong_ke["gia_trung_vi"],
    height=0.6,
    edgecolor="black",
    alpha=0.85
)

ax.set_title(
    "Giá trung vị theo 10 khu vực có nhiều tin đăng nhất",
    fontsize=14,
    pad=20
)
ax.set_xlabel("Giá trung vị (triệu đồng)", fontsize=11)
ax.set_ylabel("Khu vực", fontsize=11)

ax.tick_params(axis="y", labelsize=10, pad=10)
ax.grid(axis="x", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)

# Hiển thị giá trị trên từng thanh
for cot in cac_cot:
    gia = cot.get_width()
    ax.text(
        gia + thong_ke["gia_trung_vi"].max() * 0.01,
        cot.get_y() + cot.get_height() / 2,
        f"{gia:,.0f}",
        va="center",
        fontsize=9
    )

# Tăng khoảng trống bên phải
ax.set_xlim(0, thong_ke["gia_trung_vi"].max() * 1.18)

plt.tight_layout()

# Lưu biểu đồ
thu_muc = Path("reports/charts")
thu_muc.mkdir(parents=True, exist_ok=True)

duong_dan = thu_muc / "bieu_do_khu_vuc.png"

plt.savefig(
    duong_dan,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# In kết quả
print("\nTHỐNG KÊ GIÁ THEO KHU VỰC")
print(thong_ke.round(2))
print("\nĐã lưu biểu đồ tại:", duong_dan)
