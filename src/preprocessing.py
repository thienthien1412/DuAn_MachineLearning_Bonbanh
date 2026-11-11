
import re
import json
from pathlib import Path

import numpy as np
import pandas as pd


thu_muc = Path(__file__).resolve().parent.parent
file_goc = thu_muc / "data" / "raw" / "bonbanh_raw.csv"
thu_muc_xu_ly = thu_muc / "data" / "processed"
file_xu_ly = thu_muc_xu_ly / "bonbanh_processed.csv"
file_bao_cao = thu_muc / "reports" / "preprocessing_report.json"


# Danh sách hãng xe
danh_sach_hang = [
    "Mercedes Benz", "Rolls Royce", "Aston Martin", "Lynk & Co",
    "LandRover", "VinFast", "Ssangyong", "Dongben", "Hoa Mai",
    "Đô Thành", "Toyota", "Mercedes", "Hyundai", "Ford", "Kia",
    "Mazda", "Mitsubishi", "Lexus", "Honda", "BMW", "Porsche",
    "Chevrolet", "Suzuki", "Nissan", "Peugeot", "Audi",
    "Volkswagen", "Bentley", "Daewoo", "Volvo", "Mini", "Isuzu",
    "Thaco", "Subaru", "Cadillac", "Jeep", "Maserati", "Jaguar",
    "Infiniti", "Acura", "BYD", "Skoda", "Fiat", "Teraco",
    "Geely", "Omoda", "Iveco", "Lincoln", "Smart", "McLaren",
    "Zotye", "Kenbo", "Wuling", "Renault", "GAC", "Lamborghini",
    "Chrysler", "Haval", "RAM", "Hino", "Baic", "Scion",
    "Mekong", "Luxgen", "Pontiac", "Dodge", "Vinamotor", "Veam",
    "Jaecoo", "Bestune", "Tanda", "Samco", "Gaz", "Daihatsu",
    "Hummer", "Lifan", "SYM", "Haima", "JAC", "TMT", "VEAM", "MG"
]

danh_sach_hang = sorted(danh_sach_hang, key=len, reverse=True)


def lay_hang_xe(ten_xe):
    if pd.isna(ten_xe):
        return np.nan

    for hang in danh_sach_hang:
        if str(ten_xe).lower().startswith(hang.lower()):
            return hang

    return "Chưa xác định"


def lay_dong_xe(ten_xe, hang_xe):
    if pd.isna(ten_xe):
        return np.nan

    ten = re.sub(r"\s+-\s+\d{4}$", "", str(ten_xe)).strip()

    if pd.notna(hang_xe) and hang_xe != "Chưa xác định":
        ten = ten[len(hang_xe):].strip()

    return ten if ten else np.nan


def tach_dong_co(dong_co):
    if pd.isna(dong_co):
        return pd.Series([np.nan, np.nan])

    noi_dung = str(dong_co).strip().lower()

    # Nhận diện xe điện
    if "điện" in noi_dung:
        return pd.Series(["Điện", np.nan])

    # Nhận diện loại nhiên liệu
    if "hybrid" in noi_dung:
        nhien_lieu = "Hybrid"
    elif "xăng" in noi_dung:
        nhien_lieu = "Xăng"
    elif "dầu" in noi_dung:
        nhien_lieu = "Dầu"
    else:
        nhien_lieu = np.nan

    # Tách dung tích động cơ
    ket_qua = re.search(r"(\d+(?:[.,]\d+)?)\s*l", noi_dung)
    dung_tich = np.nan

    if ket_qua:
        dung_tich = float(ket_qua.group(1).replace(",", "."))

    return pd.Series([nhien_lieu, dung_tich])


def tien_xu_ly():
    if not file_goc.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {file_goc}")

    thu_muc_xu_ly.mkdir(parents=True, exist_ok=True)
    file_bao_cao.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(file_goc)
    so_dong_ban_dau = len(df)

    print("Số bản ghi ban đầu:", so_dong_ban_dau)

    # Loại bỏ phương tiện không thuộc phạm vi ô tô
    dieu_kien_mooc = df["ten_xe"].str.contains(
        "Mooc", case=False, na=False
    )

    so_mooc = int(dieu_kien_mooc.sum())
    df = df[~dieu_kien_mooc].copy()

    # Loại bỏ bản ghi trùng hoàn toàn
    so_trung = int(df.duplicated().sum())
    df = df.drop_duplicates()

    # Thay ký hiệu không có thông tin bằng giá trị thiếu
    cac_cot = [
        "khu_vuc", "xuat_xu", "kieu_dang", "hop_so",
        "dong_co", "mau_ngoai_that", "mau_noi_that",
        "so_cho_ngoi", "so_cua", "dan_dong"
    ]

    so_gach_ngang = 0

    for cot in cac_cot:
        if cot in df.columns:
            so_gach_ngang += int((df[cot] == "-").sum())
            df[cot] = df[cot].replace("-", np.nan)

    # Chuẩn hóa nội dung mô tả nhưng vẫn giữ lại văn bản
    df["mo_ta"] = df["mo_ta"].astype("string").str.strip()
    df["mo_ta"] = df["mo_ta"].replace("", pd.NA)

    # Chuyển giá bán và năm sản xuất sang dạng số
    df["gia_ban"] = pd.to_numeric(
        df["gia_ban"], errors="coerce"
    )

    df["nam_san_xuat_ct"] = pd.to_numeric(
        df["nam_san_xuat_ct"], errors="coerce"
    )

    # Chuẩn hóa số km đã đi
    df["so_km_da_di"] = (
        df["so_km_da_di"]
        .astype("string")
        .str.replace(",", "", regex=False)
        .str.replace(r"\s*Km$", "", regex=True, case=False)
    )

    df["so_km_da_di"] = pd.to_numeric(
        df["so_km_da_di"], errors="coerce"
    )

    # Đánh dấu số km từ 500.000 trở lên là bất thường
    so_km_bat_thuong = int(
        (df["so_km_da_di"] >= 500000).sum()
    )

    df.loc[
        df["so_km_da_di"] >= 500000,
        "so_km_da_di"
    ] = np.nan

    # Chuyển số chỗ ngồi và số cửa sang dạng số
    for cot in ["so_cho_ngoi", "so_cua"]:
        df[cot] = pd.to_numeric(
            df[cot].astype("string").str.extract(
                r"(\d+)", expand=False
            ),
            errors="coerce"
        )

    df.loc[df["so_cho_ngoi"] == 0, "so_cho_ngoi"] = np.nan
    df.loc[df["so_cua"] == 0, "so_cua"] = np.nan

    # Tách hãng xe và phần tên còn lại
    df["hang_xe"] = df["ten_xe"].apply(lay_hang_xe)

    df["dong_xe"] = df.apply(
        lambda dong: lay_dong_xe(
            dong["ten_xe"], dong["hang_xe"]
        ),
        axis=1
    )

    # Tách nhiên liệu và dung tích động cơ
    df[["nhien_lieu", "dung_tich_dong_co"]] = df[
        "dong_co"
    ].apply(tach_dong_co)

    # Tạo đặc trưng về tuổi xe và số km trung bình mỗi năm
    nam_thu_thap = 2026

    df["tuoi_xe"] = nam_thu_thap - df["nam_san_xuat_ct"]

    df["so_nam_su_dung"] = (
        nam_thu_thap - df["nam_san_xuat_ct"]
    ).clip(lower=1)

    df["km_trung_binh_nam"] = (
        df["so_km_da_di"] / df["so_nam_su_dung"]
    )

    # Loại bỏ các cột không cần thiết
    cac_cot_bo = [
        "ma_tin", "url",
        "tinh_trang", "tinh_trang_ct",
        "nam_san_xuat", "dong_co"
    ]

    df = df.drop(columns=cac_cot_bo, errors="ignore")

    # Thống kê kết quả tiền xử lý
    bao_cao = {
        "so_dong_ban_dau": int(so_dong_ban_dau),
        "so_phuong_tien_ngoai_pham_vi": so_mooc,
        "so_dong_trung_lap": so_trung,
        "so_gia_tri_gach_ngang": so_gach_ngang,
        "so_km_bat_thuong": so_km_bat_thuong,
        "so_dong_sau_xu_ly": int(len(df)),
        "so_cot_sau_xu_ly": int(len(df.columns)),
        "so_mo_ta_thieu": int(df["mo_ta"].isna().sum()),
        "gia_tri_thieu": {
            cot: int(so_luong)
            for cot, so_luong in df.isna().sum().items()
        },
        "danh_sach_cot": list(df.columns)
    }

    # Lưu dữ liệu đã xử lý
    df.to_csv(
        file_xu_ly,
        index=False,
        encoding="utf-8-sig"
    )

    # Lưu báo cáo tiền xử lý
    with open(file_bao_cao, "w", encoding="utf-8") as tep:
        json.dump(
            bao_cao,
            tep,
            ensure_ascii=False,
            indent=4
        )

    print("\nKết quả tiền xử lý")
    print("Số bản ghi sau xử lý:", len(df))
    print("Số cột sau xử lý:", len(df.columns))
    print("Số phương tiện ngoài phạm vi bị loại:", so_mooc)
    print("Số bản ghi trùng:", so_trung)
    print("Số giá trị '-' được thay thế:", so_gach_ngang)
    print("Số giá trị km bất thường:", so_km_bat_thuong)
    print("Số mô tả bị thiếu:", bao_cao["so_mo_ta_thieu"])
    print("\nĐã lưu dữ liệu:", file_xu_ly)
    print("Đã lưu báo cáo:", file_bao_cao)


if __name__ == "__main__":
    tien_xu_ly()
