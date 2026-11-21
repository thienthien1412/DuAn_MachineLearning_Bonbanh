
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


# Danh sach hang xe
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

danh_sach_hang = sorted(
    danh_sach_hang,
    key=len,
    reverse=True
)


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

    ten = re.sub(
        r"\s+-\s+\d{4}$",
        "",
        str(ten_xe)
    ).strip()

    if pd.notna(hang_xe) and hang_xe != "Chưa xác định":
        ten = ten[len(hang_xe):].strip()

    return ten if ten else np.nan


def tach_dong_co(dong_co):
    if pd.isna(dong_co):
        return np.nan, np.nan

    noi_dung = str(dong_co).strip().lower()

    # Nhan dien xe dien
    if "điện" in noi_dung:
        return "Điện", np.nan

    # Nhan dien loai nhien lieu
    if "hybrid" in noi_dung:
        nhien_lieu = "Hybrid"
    elif "xăng" in noi_dung:
        nhien_lieu = "Xăng"
    elif "dầu" in noi_dung:
        nhien_lieu = "Dầu"
    else:
        nhien_lieu = np.nan

    # Tach dung tich dong co
    ket_qua = re.search(
        r"(\d+(?:[.,]\d+)?)\s*l",
        noi_dung
    )

    dung_tich = np.nan

    if ket_qua:
        dung_tich = float(
            ket_qua.group(1).replace(",", ".")
        )

    return nhien_lieu, dung_tich


def tien_xu_ly():
    thu_muc_xu_ly.mkdir(
        parents=True,
        exist_ok=True
    )

    file_bao_cao.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Doc du lieu goc
    df = pd.read_csv(
        file_goc,
        encoding="utf-8-sig"
    )

    so_dong_ban_dau = len(df)

    print("Số bản ghi ban đầu:", so_dong_ban_dau)

    # Loai bo phuong tien khong thuoc pham vi o to
    dieu_kien_mooc = df["ten_xe"].astype("string").str.contains(
        "Mooc",
        case=False,
        na=False
    )

    so_mooc = int(dieu_kien_mooc.sum())

    df = df[~dieu_kien_mooc].copy()

    # Chuyen gia ban sang dang so
    df["gia_ban"] = pd.to_numeric(
        df["gia_ban"],
        errors="coerce"
    )

    # Chi giu cac ban ghi xe cu
    tinh_trang = (
        df["tinh_trang"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    dieu_kien_tinh_trang = tinh_trang.eq("xe cũ")

    so_sai_tinh_trang = int(
        (~dieu_kien_tinh_trang).sum()
    )

    df = df[dieu_kien_tinh_trang].copy()

    # Loai bo ban ghi khong co gia ban hop le
    dieu_kien_gia = (
        df["gia_ban"].notna()
        & (df["gia_ban"] > 0)
    )

    so_gia_khong_hop_le = int(
        (~dieu_kien_gia).sum()
    )

    df = df[dieu_kien_gia].copy()

    # Thay ky hieu khong co thong tin bang gia tri thieu
    cac_cot = [
        "khu_vuc", "xuat_xu", "kieu_dang", "hop_so",
        "dong_co", "mau_ngoai_that", "mau_noi_that",
        "so_cho_ngoi", "so_cua", "dan_dong"
    ]

    so_gach_ngang = 0

    for cot in cac_cot:
        if cot in df.columns:
            gia_tri = (
                df[cot]
                .astype("string")
                .str.strip()
            )

            so_gach_ngang += int(
                gia_tri.eq("-").sum()
            )

            df[cot] = gia_tri.replace("-", pd.NA)

    # Chuan hoa noi dung mo ta
    df["mo_ta"] = (
        df["mo_ta"]
        .astype("string")
        .str.strip()
    )

    df["mo_ta"] = df["mo_ta"].replace(
        "",
        pd.NA
    )

    # Chuyen nam san xuat sang dang so
    df["nam_san_xuat_ct"] = pd.to_numeric(
        df["nam_san_xuat_ct"],
        errors="coerce"
    )

    nam_thu_thap = 2026

    # Kiem tra nam san xuat bat thuong
    dieu_kien_nam = (
        (df["nam_san_xuat_ct"] < 1950)
        | (df["nam_san_xuat_ct"] > nam_thu_thap)
    )

    so_nam_bat_thuong = int(
        dieu_kien_nam.sum()
    )

    df.loc[
        dieu_kien_nam,
        "nam_san_xuat_ct"
    ] = np.nan

    # Chuan hoa so km da di
    df["so_km_da_di"] = (
        df["so_km_da_di"]
        .astype("string")
        .str.replace(",", "", regex=False)
        .str.replace(
            r"\s*Km$",
            "",
            regex=True,
            case=False
        )
    )

    df["so_km_da_di"] = pd.to_numeric(
        df["so_km_da_di"],
        errors="coerce"
    )

    # Xu ly so km bat thuong va so km am
    dieu_kien_km_bat_thuong = (
        df["so_km_da_di"] >= 500000
    )

    so_km_bat_thuong = int(
        dieu_kien_km_bat_thuong.sum()
    )

    dieu_kien_km_am = (
        df["so_km_da_di"] < 0
    )

    so_km_am = int(
        dieu_kien_km_am.sum()
    )

    df.loc[
        dieu_kien_km_bat_thuong | dieu_kien_km_am,
        "so_km_da_di"
    ] = np.nan

    # Chuyen so cho ngoi va so cua sang dang so
    for cot in ["so_cho_ngoi", "so_cua"]:
        df[cot] = pd.to_numeric(
            df[cot].astype("string").str.extract(
                r"(\d+)",
                expand=False
            ),
            errors="coerce"
        )

        df.loc[
            df[cot] == 0,
            cot
        ] = np.nan

    # Tach hang xe va dong xe
    df["hang_xe"] = df["ten_xe"].apply(
        lay_hang_xe
    )

    df["dong_xe"] = df.apply(
        lambda dong: lay_dong_xe(
            dong["ten_xe"],
            dong["hang_xe"]
        ),
        axis=1
    )

    # Tach nhien lieu va dung tich dong co
    ket_qua_dong_co = pd.DataFrame(
        df["dong_co"].apply(tach_dong_co).tolist(),
        index=df.index,
        columns=["nhien_lieu", "dung_tich_dong_co"]
    )

    df[["nhien_lieu", "dung_tich_dong_co"]] = ket_qua_dong_co

    # Tao dac trung tuoi xe va so km trung binh moi nam
    df["tuoi_xe"] = (
        nam_thu_thap - df["nam_san_xuat_ct"]
    )

    df["so_nam_su_dung"] = (
        nam_thu_thap - df["nam_san_xuat_ct"]
    ).clip(lower=1)

    df["km_trung_binh_nam"] = (
        df["so_km_da_di"] / df["so_nam_su_dung"]
    )

    # Loai bo cac cot khong su dung trong mo hinh
    cac_cot_bo = [
        "ma_tin", "url",
        "tinh_trang", "tinh_trang_ct",
        "nam_san_xuat", "dong_co"
    ]

    df = df.drop(
        columns=cac_cot_bo,
        errors="ignore"
    )

    # Kiem tra va loai bo cac ban ghi trung lap
    so_dong_truoc_loai_trung = len(df)

    so_trung = int(
        df.duplicated().sum()
    )

    df = df.drop_duplicates(
        keep="first"
    ).copy()

    # Thong ke ket qua tien xu ly
    bao_cao = {
        "so_dong_ban_dau": int(so_dong_ban_dau),
        "so_phuong_tien_ngoai_pham_vi": so_mooc,
        "so_ban_ghi_sai_tinh_trang": so_sai_tinh_trang,
        "so_gia_ban_khong_hop_le": so_gia_khong_hop_le,
        "so_gia_tri_gach_ngang": so_gach_ngang,
        "so_nam_san_xuat_bat_thuong": so_nam_bat_thuong,
        "so_km_bat_thuong": so_km_bat_thuong,
        "so_km_am": so_km_am,
        "so_dong_truoc_loai_trung": int(so_dong_truoc_loai_trung),
        "so_dong_trung_lap": so_trung,
        "so_dong_sau_xu_ly": int(len(df)),
        "so_cot_sau_xu_ly": int(len(df.columns)),
        "so_mo_ta_thieu": int(df["mo_ta"].isna().sum()),
        "gia_tri_thieu": {
            cot: int(so_luong)
            for cot, so_luong in df.isna().sum().items()
        },
        "danh_sach_cot": list(df.columns)
    }

    # Luu du lieu da xu ly
    df.to_csv(
        file_xu_ly,
        index=False,
        encoding="utf-8-sig"
    )

    # Luu bao cao tien xu ly
    with open(
        file_bao_cao,
        "w",
        encoding="utf-8"
    ) as tep:
        json.dump(
            bao_cao,
            tep,
            ensure_ascii=False,
            indent=4
        )

    print("\nKET QUA TIEN XU LY")
    print("Số bản ghi ban đầu:", so_dong_ban_dau)
    print("Phương tiện ngoài phạm vi:", so_mooc)
    print("Bản ghi sai tình trạng:", so_sai_tinh_trang)
    print("Giá bán không hợp lệ:", so_gia_khong_hop_le)
    print("Giá trị dấu gạch ngang:", so_gach_ngang)
    print("Năm sản xuất bất thường:", so_nam_bat_thuong)
    print("Số km bất thường:", so_km_bat_thuong)
    print("Số km âm:", so_km_am)
    print("Số dòng trước khi loại trùng:", so_dong_truoc_loai_trung)
    print("Số dòng trùng lặp:", so_trung)
    print("Số dòng sau xử lý:", len(df))
    print("Số cột sau xử lý:", len(df.columns))
    print("Số mô tả thiếu:", bao_cao["so_mo_ta_thieu"])
    print("Tổng giá trị thiếu:", int(df.isna().sum().sum()))
    print("\nCác cột sau xử lý:")
    print(list(df.columns))

    print("\nĐã lưu dữ liệu:", file_xu_ly)
    print("Đã lưu báo cáo:", file_bao_cao)


if __name__ == "__main__":
    tien_xu_ly()
