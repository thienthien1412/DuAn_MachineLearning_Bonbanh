
import pandas as pd
from pathlib import Path

# Đọc dữ liệu
df = pd.read_csv("data/raw/bonbanh_raw.csv")

# Chuyển giá bán về dạng số
df["gia_ban"] = pd.to_numeric(df["gia_ban"], errors="coerce")

# Chuyển năm sản xuất về dạng số
df["nam_san_xuat_ct"] = pd.to_numeric(
    df["nam_san_xuat_ct"], errors="coerce"
)

# Chuyển số kilomet đã đi về dạng số
df["so_km_da_di"] = pd.to_numeric(
    df["so_km_da_di"].astype(str).str.replace(
        r"[^\d]", "", regex=True
    ),
    errors="coerce"
)

# Chọn các thuộc tính cần phân tích
du_lieu = df[
    ["nam_san_xuat_ct", "so_km_da_di", "gia_ban"]
].dropna()

# Tính hệ số tương quan Pearson
pearson = du_lieu.corr(method="pearson")["gia_ban"]

# Tính hệ số tương quan Spearman
spearman = du_lieu.corr(method="spearman")["gia_ban"]

# Tổng hợp kết quả
ket_qua = pd.DataFrame({
    "Thuộc tính": [
        "Năm sản xuất",
        "Số kilomet đã đi"
    ],
    "Pearson": [
        pearson["nam_san_xuat_ct"],
        pearson["so_km_da_di"]
    ],
    "Spearman": [
        spearman["nam_san_xuat_ct"],
        spearman["so_km_da_di"]
    ]
})

print("\nBẢNG PHÂN TÍCH TƯƠNG QUAN")
print(ket_qua.round(3).to_string(index=False))

# Lưu kết quả
duong_dan = Path("reports/charts/bang_tuong_quan.csv")
ket_qua.to_csv(duong_dan, index=False, encoding="utf-8-sig")

print("\nĐã lưu kết quả tại:", duong_dan)
print("Số dòng được sử dụng:", len(du_lieu))
