
import random
import time

from src import config
from src.scraper import (
    tao_phien,
    lay_trang,
    lay_danh_sach_xe,
    lay_thong_so_chi_tiet,
    lay_so_trang,
    tao_url_trang,
    LoiTruyCapBiChan,
    LoiThuThap
)
from src.database import (
    tao_co_so_du_lieu,
    luu_danh_sach_xe,
    luu_tien_do_trang,
    kiem_tra_trang_da_cao,
    lay_xe_chua_co_chi_tiet,
    cap_nhat_thong_so_chi_tiet,
    ghi_nhan_loi_chi_tiet
)


def cho_ngau_nhien():
    time.sleep(
        random.uniform(
            config.THOI_GIAN_CHO,
            config.THOI_GIAN_CHO_TOI_DA
        )
    )


def thu_thap_danh_sach(phien):
    print("\nGIAI DOAN 1: THU THAP DANH SACH XE")

    try:
        trang_dau = lay_trang(phien, tao_url_trang(1))
        tong_so_trang = lay_so_trang(trang_dau)

    except LoiTruyCapBiChan as loi:
        print(loi)
        return False

    except LoiThuThap as loi:
        print(loi)
        return False

    if config.SO_TRANG_THU_NGHIEM:
        tong_so_trang = min(
            tong_so_trang,
            config.SO_TRANG_THU_NGHIEM
        )

    print(f"So trang se thu thap: {tong_so_trang}")

    for so_trang in range(
        config.TRANG_BAT_DAU,
        tong_so_trang + 1
    ):
        if kiem_tra_trang_da_cao(so_trang):
            print(f"Trang {so_trang} da hoan thanh, bo qua.")
            continue

        url = tao_url_trang(so_trang)

        cho_ngau_nhien()

        print(f"Dang thu thap trang {so_trang}...")

        try:
            danh_sach = lay_danh_sach_xe(phien, url)

        except LoiTruyCapBiChan as loi:
            print(loi)
            return False

        except LoiThuThap as loi:
            print(loi)
            return False

        if not danh_sach:
            print("Khong tim thay tin xe cu. Tam dung de kiem tra.")
            return False

        for xe in danh_sach:
            luu_danh_sach_xe(xe, so_trang)

        luu_tien_do_trang(so_trang, url, 1)

        print(
            f"Trang {so_trang} hoan thanh: "
            f"{len(danh_sach)} tin xe cu."
        )

    print("Ket thuc giai doan thu thap danh sach.")
    return True


def thu_thap_chi_tiet(phien):
    print("\nGIAI DOAN 2: THU THAP THONG SO CHI TIET")

    danh_sach = lay_xe_chua_co_chi_tiet()
    tong_so_tin = len(danh_sach)

    print(f"So tin cho thu thap chi tiet: {tong_so_tin}")

    if tong_so_tin == 0:
        print("Khong co tin nao can thu thap.")
        return

    thanh_cong = 0
    that_bai = 0
    chua_xu_ly = 0

    for vi_tri, (ma_tin, url) in enumerate(danh_sach, 1):
        print(f"\n[{vi_tri}/{tong_so_tin}] Ma tin: {ma_tin}")

        cho_ngau_nhien()

        try:
            thong_so = lay_thong_so_chi_tiet(phien, url)

        except LoiTruyCapBiChan as loi:
            print(loi)
            chua_xu_ly = tong_so_tin - thanh_cong - that_bai
            break

        except LoiThuThap as loi:
            ghi_nhan_loi_chi_tiet(ma_tin, loi)
            that_bai += 1
            print(loi)
            continue

        if len(thong_so) != 12:
            ghi_nhan_loi_chi_tiet(
                ma_tin,
                f"Lay duoc {len(thong_so)}/12 thong so"
            )
            that_bai += 1
            print(f"Thu thap that bai: {len(thong_so)}/12 thong so.")
            continue

        cap_nhat_thong_so_chi_tiet(ma_tin, thong_so)

        thanh_cong += 1
        print("Thu thap thanh cong: 12/12 thong so.")

    if chua_xu_ly == 0:
        chua_xu_ly = tong_so_tin - thanh_cong - that_bai

    print("\nKET QUA THU THAP CHI TIET")
    print(f"Thanh cong: {thanh_cong}")
    print(f"That bai: {that_bai}")
    print(f"Chua xu ly: {chua_xu_ly}")


def main():
    tao_co_so_du_lieu()

    phien = tao_phien()

    if not thu_thap_danh_sach(phien):
        print("\nDung chuong trinh, chua tiep tuc thu thap chi tiet.")
        return

    thu_thap_chi_tiet(phien)

    print("\nKet thuc chuong trinh.")


if __name__ == "__main__":
    main()
