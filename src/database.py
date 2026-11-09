
import os
import sqlite3

from src import config


def ket_noi_database():
    thu_muc = os.path.dirname(config.TEN_DATABASE)
    os.makedirs(thu_muc, exist_ok=True)

    ket_noi = sqlite3.connect(config.TEN_DATABASE)
    ket_noi.execute("PRAGMA foreign_keys = ON")

    return ket_noi


def tao_co_so_du_lieu():
    ket_noi = ket_noi_database()

    ket_noi.execute("""
        CREATE TABLE IF NOT EXISTS danh_sach_xe (
            ma_tin TEXT PRIMARY KEY,
            ten_xe TEXT,
            tinh_trang TEXT,
            gia_ban TEXT,
            khu_vuc TEXT,
            nam_san_xuat TEXT,
            mo_ta TEXT,
            url TEXT,
            trang_danh_sach INTEGER,
            nam_san_xuat_ct TEXT,
            tinh_trang_ct TEXT,
            so_km_da_di TEXT,
            xuat_xu TEXT,
            kieu_dang TEXT,
            hop_so TEXT,
            dong_co TEXT,
            mau_ngoai_that TEXT,
            mau_noi_that TEXT,
            so_cho_ngoi TEXT,
            so_cua TEXT,
            dan_dong TEXT,
            chi_tiet_da_cao INTEGER DEFAULT 0,
            loi_chi_tiet TEXT
        )
    """)

    ket_noi.execute("""
        CREATE TABLE IF NOT EXISTS trang_da_cao (
            so_trang INTEGER PRIMARY KEY,
            url TEXT,
            da_hoan_thanh INTEGER DEFAULT 0
        )
    """)

    ket_noi.commit()
    ket_noi.close()


def luu_danh_sach_xe(xe, so_trang=None):
    du_lieu = (
        xe.get("ma_tin"),
        xe.get("ten_xe"),
        xe.get("tinh_trang"),
        xe.get("gia_ban"),
        xe.get("khu_vuc"),
        xe.get("nam_san_xuat"),
        xe.get("mo_ta"),
        xe.get("url"),
        so_trang
    )

    ket_noi = ket_noi_database()

    ket_noi.execute("""
        INSERT INTO danh_sach_xe (
            ma_tin, ten_xe, tinh_trang, gia_ban, khu_vuc,
            nam_san_xuat, mo_ta, url, trang_danh_sach
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(ma_tin) DO UPDATE SET
            ten_xe = excluded.ten_xe,
            tinh_trang = excluded.tinh_trang,
            gia_ban = excluded.gia_ban,
            khu_vuc = excluded.khu_vuc,
            nam_san_xuat = excluded.nam_san_xuat,
            mo_ta = excluded.mo_ta,
            url = excluded.url,
            trang_danh_sach = excluded.trang_danh_sach
    """, du_lieu)

    ket_noi.commit()
    ket_noi.close()


def cap_nhat_thong_so_chi_tiet(ma_tin, thong_so):
    if not thong_so:
        return

    du_lieu = (
        thong_so.get("Năm sản xuất"),
        thong_so.get("Tình trạng"),
        thong_so.get("Số Km đã đi"),
        thong_so.get("Xuất xứ"),
        thong_so.get("Kiểu dáng"),
        thong_so.get("Hộp số"),
        thong_so.get("Động cơ"),
        thong_so.get("Màu ngoại thất"),
        thong_so.get("Màu nội thất"),
        thong_so.get("Số chỗ ngồi"),
        thong_so.get("Số cửa"),
        thong_so.get("Dẫn động"),
        ma_tin
    )

    ket_noi = ket_noi_database()

    ket_noi.execute("""
        UPDATE danh_sach_xe SET
            nam_san_xuat_ct = ?,
            tinh_trang_ct = ?,
            so_km_da_di = ?,
            xuat_xu = ?,
            kieu_dang = ?,
            hop_so = ?,
            dong_co = ?,
            mau_ngoai_that = ?,
            mau_noi_that = ?,
            so_cho_ngoi = ?,
            so_cua = ?,
            dan_dong = ?,
            chi_tiet_da_cao = 1,
            loi_chi_tiet = NULL
        WHERE ma_tin = ?
    """, du_lieu)

    ket_noi.commit()
    ket_noi.close()


def ghi_nhan_loi_chi_tiet(ma_tin, loi):
    ket_noi = ket_noi_database()

    ket_noi.execute("""
        UPDATE danh_sach_xe
        SET loi_chi_tiet = ?
        WHERE ma_tin = ?
    """, (str(loi), ma_tin))

    ket_noi.commit()
    ket_noi.close()


def lay_xe_chua_co_chi_tiet():
    ket_noi = ket_noi_database()

    ket_qua = ket_noi.execute("""
        SELECT ma_tin, url
        FROM danh_sach_xe
        WHERE chi_tiet_da_cao = 0
        ORDER BY ma_tin
    """).fetchall()

    ket_noi.close()

    return ket_qua


def luu_tien_do_trang(so_trang, url, da_hoan_thanh=0):
    ket_noi = ket_noi_database()

    ket_noi.execute("""
        INSERT INTO trang_da_cao (so_trang, url, da_hoan_thanh)
        VALUES (?, ?, ?)
        ON CONFLICT(so_trang) DO UPDATE SET
            url = excluded.url,
            da_hoan_thanh = excluded.da_hoan_thanh
    """, (so_trang, url, da_hoan_thanh))

    ket_noi.commit()
    ket_noi.close()


def kiem_tra_trang_da_cao(so_trang):
    ket_noi = ket_noi_database()

    ket_qua = ket_noi.execute("""
        SELECT da_hoan_thanh
        FROM trang_da_cao
        WHERE so_trang = ?
    """, (so_trang,)).fetchone()

    ket_noi.close()

    return bool(ket_qua and ket_qua[0] == 1)


def lay_trang_chua_hoan_thanh():
    ket_noi = ket_noi_database()

    ket_qua = ket_noi.execute("""
        SELECT so_trang
        FROM trang_da_cao
        WHERE da_hoan_thanh = 0
        ORDER BY so_trang
    """).fetchall()

    ket_noi.close()

    return [dong[0] for dong in ket_qua]
