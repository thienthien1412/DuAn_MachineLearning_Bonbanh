import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

THU_MUC = Path(__file__).resolve().parent
sys.path.insert(0, str(THU_MUC))          # de joblib tim thay tien_xu_ly_xe.py khi nap mo hinh

with open(THU_MUC / "thong_tin_mo_hinh.json", encoding="utf-8") as f:
    THONG_TIN = json.load(f)
with open(THU_MUC / "lua_chon_dau_vao.json", encoding="utf-8") as f:
    LUA_CHON = json.load(f)

CAC_COT = THONG_TIN["dac_trung_dau_vao"]
_MO_HINH = None


def tai_mo_hinh():
    # Nap mo hinh mot lan duy nhat (nen goi luc khoi dong ung dung)
    global _MO_HINH
    if _MO_HINH is None:
        _MO_HINH = joblib.load(THU_MUC / "model_final.joblib")
    return _MO_HINH


def _trong(v):
    return v is None or (isinstance(v, str) and v.strip() == "") or (isinstance(v, float) and v != v)


def kiem_tra_dau_vao(thong_tin):
    # Tra ve (danh sach loi, danh sach canh bao). Danh sach loi rong thi du lieu hop le.
    loi, canh_bao = [], []
    for cot in CAC_COT:
        v = thong_tin.get(cot)
        if _trong(v):
            if cot not in LUA_CHON["co_the_de_trong"]:
                loi.append(f"Thieu thong tin bat buoc: {cot}")
            continue
        if cot in LUA_CHON["cot_so"]:
            try:
                x = float(v)
            except (TypeError, ValueError):
                loi.append(f"{cot} phai la so")
                continue
            kv = LUA_CHON["cot_so"][cot]
            if not (kv["min"] <= x <= kv["max"]):
                loi.append(f"{cot}={x:g} nam ngoai pham vi du lieu huan luyen [{kv['min']:g}; {kv['max']:g}]")
        elif str(v) not in LUA_CHON["cot_chu"][cot]:
            canh_bao.append(f"{cot}='{v}' chua tung xuat hien trong du lieu huan luyen, du doan co the kem chinh xac")
    return loi, canh_bao


def du_doan_gia(thong_tin):
    # thong_tin: dict gom cac dac trung dau vao. Tra ve gia du doan (VND) va khoang tham khao.
    loi, canh_bao = kiem_tra_dau_vao(thong_tin)
    if loi:
        raise ValueError("; ".join(loi))
    dong = {}
    for cot in CAC_COT:
        v = thong_tin.get(cot)
        if cot in LUA_CHON["cot_so"]:
            dong[cot] = np.nan if _trong(v) else float(v)
        else:
            dong[cot] = np.nan if _trong(v) else str(v)
    gia = float(tai_mo_hinh().predict(pd.DataFrame([dong], columns=CAC_COT))[0])
    t = THONG_TIN["ti_le_gia_thuc_tren_du_doan"]
    return {"gia_du_doan": gia, "khoang_tham_khao": [gia * t["p10"], gia * t["p90"]], "canh_bao": canh_bao}
