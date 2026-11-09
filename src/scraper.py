
import random
import re
import time
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from src import config


class LoiTruyCapBiChan(Exception):
    pass


class LoiThuThap(Exception):
    pass


def tao_phien():
    phien = requests.Session()
    phien.headers.update({
        "User-Agent": "Mozilla/5.0"
    })

    return phien


def lay_trang(phien, url):
    for lan in range(1, config.SO_LAN_THU_LAI + 1):
        try:
            phan_hoi = phien.get(
                url,
                timeout=config.THOI_GIAN_TIMEOUT
            )

            if phan_hoi.status_code in (403, 429):
                raise LoiTruyCapBiChan(
                    f"Website tra ve HTTP {phan_hoi.status_code}: {url}"
                )

            phan_hoi.raise_for_status()

            noi_dung = phan_hoi.text.lower()

            dau_hieu_captcha = [
                "captcha",
                "cf-chl-",
                "verify you are human",
                "access denied"
            ]

            if any(dau_hieu in noi_dung for dau_hieu in dau_hieu_captcha):
                raise LoiTruyCapBiChan(
                    f"Phat hien trang xac minh truy cap: {url}"
                )

            return BeautifulSoup(phan_hoi.text, "lxml")

        except LoiTruyCapBiChan:
            raise

        except requests.RequestException as loi:
            print(f"Lan thu {lan}/{config.SO_LAN_THU_LAI} that bai: {loi}")

            if lan < config.SO_LAN_THU_LAI:
                time.sleep(
                    random.uniform(
                        config.THOI_GIAN_CHO,
                        config.THOI_GIAN_CHO_TOI_DA
                    )
                )

    raise LoiThuThap(
        f"Khong the truy cap sau {config.SO_LAN_THU_LAI} lan: {url}"
    )


def lay_danh_sach_xe(phien, url):
    soup = lay_trang(phien, url)

    danh_sach = []

    for the in soup.select(".cb1"):
        tin = the.find_parent("a")

        if tin is None:
            continue

        ma_tin = tin.select_one(".car_code")
        ten_xe = tin.select_one(".cb2_02 h3")
        gia = tin.select_one(".cb3 [itemprop='price']")
        khu_vuc = tin.select_one(".cb4 b")
        nam = the.select_one("b")
        mo_ta = tin.select_one(".cb6_02")

        if ma_tin is None or ten_xe is None:
            continue

        ket_qua_ma = re.search(r"\d+", ma_tin.get_text())

        if ket_qua_ma is None:
            continue

        tinh_trang = the.contents[0].strip()

        du_lieu = {
            "ma_tin": ket_qua_ma.group(),
            "ten_xe": ten_xe.get_text(" ", strip=True),
            "tinh_trang": tinh_trang,
            "gia_ban": gia.get("content") if gia else None,
            "khu_vuc": khu_vuc.get_text(strip=True) if khu_vuc else None,
            "nam_san_xuat": nam.get_text(strip=True) if nam else None,
            "mo_ta": mo_ta.get_text(" ", strip=True) if mo_ta else None,
            "url": urljoin(config.URL_GOC, tin.get("href", ""))
        }

        if tinh_trang.lower() == "xe cũ":
            danh_sach.append(du_lieu)

    return danh_sach


def lay_thong_so_chi_tiet(phien, url):
    soup = lay_trang(phien, url)

    khu_vuc = soup.select_one(".box_car_detail")

    if khu_vuc is None:
        return {}

    thong_so = {}

    for dong in khu_vuc.select(".row, .row_last"):
        nhan = dong.select_one(".label")
        gia_tri = dong.select_one(".inp")

        if nhan is None or gia_tri is None:
            continue

        ten_thuoc_tinh = nhan.get_text(" ", strip=True).rstrip(":")
        gia_tri_thuoc_tinh = gia_tri.get_text(" ", strip=True)

        thong_so[ten_thuoc_tinh] = gia_tri_thuoc_tinh

    return thong_so


def lay_so_trang(soup):
    cac_trang = soup.select(".navpage .bbl[url]")

    so_trang = [1]

    for trang in cac_trang:
        url = trang.get("url", "")
        ket_qua = re.search(r"/page,(\d+)", url)

        if ket_qua:
            so_trang.append(int(ket_qua.group(1)))

    return max(so_trang)


def tao_url_trang(so_trang):
    if so_trang == 1:
        return f"{config.URL_GOC}/oto"

    return f"{config.URL_GOC}/oto/page,{so_trang}"
