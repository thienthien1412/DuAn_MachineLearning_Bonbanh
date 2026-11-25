
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request


THU_MUC_DU_AN = Path(__file__).resolve().parent.parent
THU_MUC_BAN_GIAO = THU_MUC_DU_AN / "ban_giao_chuong6"
DUONG_DAN_DU_LIEU = (
    THU_MUC_DU_AN / "data" / "processed" / "bonbanh_processed.csv"
)

sys.path.insert(0, str(THU_MUC_BAN_GIAO))

import du_doan


app = Flask(__name__)

with open(
    THU_MUC_BAN_GIAO / "lua_chon_dau_vao.json",
    encoding="utf-8"
) as tep:
    LUA_CHON = json.load(tep)

# Nap du lieu xe de phuc vu thong ke
DU_LIEU_XE = pd.read_csv(DUONG_DAN_DU_LIEU)

DU_LIEU_XE["gia_ban"] = pd.to_numeric(
    DU_LIEU_XE["gia_ban"],
    errors="coerce"
)

DU_LIEU_XE["tuoi_xe"] = pd.to_numeric(
    DU_LIEU_XE["tuoi_xe"],
    errors="coerce"
)

DU_LIEU_XE = DU_LIEU_XE.dropna(
    subset=["gia_ban"]
).copy()

# Nap mo hinh mot lan khi khoi dong website
du_doan.tai_mo_hinh()


# --------------------------------------------------
# CAC TRANG GIAO DIEN
# --------------------------------------------------

@app.route("/")
def trang_chu():
    return render_template("index.html", trang="du-doan")


@app.route("/kiem-tra-gia")
def trang_kiem_tra():
    return render_template("index.html", trang="kiem-tra")


@app.route("/thong-ke")
def trang_thong_ke():
    return render_template("index.html", trang="thong-ke")


# --------------------------------------------------
# CAC API DAU VAO
# --------------------------------------------------

@app.route("/api/options", methods=["GET"])
def lay_lua_chon():
    return jsonify({
        "cot_so": LUA_CHON["cot_so"],
        "cot_chu": LUA_CHON["cot_chu"],
        "co_the_de_trong": LUA_CHON["co_the_de_trong"],
        "dong_xe_theo_hang": LUA_CHON["dong_xe_theo_hang"],
        "dac_trung_dau_vao": du_doan.CAC_COT
    })


# --------------------------------------------------
# API DU DOAN GIA
# --------------------------------------------------

@app.route("/api/predict", methods=["POST"])
def du_doan_gia_xe():
    du_lieu = request.get_json(silent=True) or {}
    thong_tin = du_lieu.get("thong_tin", du_lieu)

    if not isinstance(thong_tin, dict):
        return jsonify({
            "loi": "Thông tin xe không hợp lệ"
        }), 400

    try:
        ket_qua = du_doan.du_doan_gia(thong_tin)

        return jsonify({
            "gia_du_doan": ket_qua["gia_du_doan"],
            "khoang_tham_khao": ket_qua["khoang_tham_khao"],
            "canh_bao": ket_qua["canh_bao"]
        })

    except ValueError as e:
        return jsonify({"loi": str(e)}), 400

    except Exception:
        app.logger.exception("Loi khi du doan gia xe")
        return jsonify({
            "loi": "Không thể thực hiện dự đoán"
        }), 500


# --------------------------------------------------
# API KIEM TRA GIA RAO
# --------------------------------------------------

@app.route("/api/check-price", methods=["POST"])
def kiem_tra_gia_rao():
    du_lieu = request.get_json(silent=True) or {}

    thong_tin = du_lieu.get("thong_tin", {})
    gia_rao = du_lieu.get("gia_rao")

    try:
        if not isinstance(thong_tin, dict):
            raise ValueError("Thông tin xe không hợp lệ")

        gia_rao = float(gia_rao)

        if not np.isfinite(gia_rao) or gia_rao <= 0:
            raise ValueError("Giá rao bán phải lớn hơn 0")

        ket_qua = du_doan.du_doan_gia(thong_tin)

        gia_du_doan = ket_qua["gia_du_doan"]
        gia_thap, gia_cao = ket_qua["khoang_tham_khao"]

        if gia_rao < gia_thap:
            danh_gia = "Thấp hơn khoảng giá tham khảo"
        elif gia_rao > gia_cao:
            danh_gia = "Cao hơn khoảng giá tham khảo"
        else:
            danh_gia = "Nằm trong khoảng giá tham khảo"

        return jsonify({
            "gia_rao": gia_rao,
            "gia_du_doan": gia_du_doan,
            "khoang_tham_khao": [gia_thap, gia_cao],
            "chenh_lech": gia_rao - gia_du_doan,
            "ty_le_chenh_lech": (
                (gia_rao - gia_du_doan) / gia_du_doan * 100
                if gia_du_doan else None
            ),
            "danh_gia": danh_gia,
            "canh_bao": ket_qua["canh_bao"]
        })

    except (ValueError, TypeError) as e:
        return jsonify({"loi": str(e)}), 400

    except Exception:
        app.logger.exception("Loi khi kiem tra gia rao")
        return jsonify({
            "loi": "Không thể kiểm tra giá rao bán"
        }), 500


# --------------------------------------------------
# CAC HAM HO TRO THONG KE
# --------------------------------------------------

def tinh_chi_so(du_lieu):
    gia = pd.to_numeric(
        du_lieu["gia_ban"],
        errors="coerce"
    ).dropna()

    if gia.empty:
        return None

    return {
        "so_xe": int(gia.count()),
        "gia_thap_nhat": float(gia.min()),
        "gia_cao_nhat": float(gia.max()),
        "gia_trung_binh": float(gia.mean()),
        "gia_trung_vi": float(gia.median()),
        "gia_p25": float(gia.quantile(0.25)),
        "gia_p75": float(gia.quantile(0.75))
    }


def tao_bieu_do_phan_bo(du_lieu, so_nhom=12):
    gia = pd.to_numeric(
        du_lieu["gia_ban"],
        errors="coerce"
    ).dropna()

    if gia.empty:
        return []

    dem, bien = np.histogram(
        gia,
        bins=so_nhom
    )

    ket_qua = []

    for i in range(len(dem)):
        ket_qua.append({
            "tu": float(bien[i]),
            "den": float(bien[i + 1]),
            "so_xe": int(dem[i])
        })

    return ket_qua


def tao_bang_theo_nhom(du_lieu, cot_nhom):
    ket_qua = []

    nhom = du_lieu.groupby(
        cot_nhom,
        dropna=True
    )

    for gia_tri, du_lieu_nhom in nhom:
        chi_so = tinh_chi_so(du_lieu_nhom)

        if chi_so is None:
            continue

        ket_qua.append({
            "gia_tri": (
                int(gia_tri)
                if cot_nhom == "tuoi_xe"
                else str(gia_tri)
            ),
            **chi_so
        })

    return ket_qua


# --------------------------------------------------
# API LUA CHON THONG KE
# --------------------------------------------------

@app.route("/api/statistics/options", methods=["GET"])
def lua_chon_thong_ke():
    hang_xe = sorted(
        DU_LIEU_XE["hang_xe"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    tuoi_xe = sorted(
        DU_LIEU_XE["tuoi_xe"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    return jsonify({
        "hang_xe": hang_xe,
        "tuoi_xe": tuoi_xe
    })


# --------------------------------------------------
# API THONG KE THI TRUONG
# --------------------------------------------------

@app.route("/api/statistics", methods=["GET"])
def thong_ke_thi_truong():
    hang = request.args.get("make", "").strip()
    tuoi_tu = request.args.get("age_min", "").strip()
    tuoi_den = request.args.get("age_max", "").strip()
    gia_tu = request.args.get("price_min", "").strip()
    gia_den = request.args.get("price_max", "").strip()

    du_lieu_loc = DU_LIEU_XE.copy()

    if hang:
        du_lieu_loc = du_lieu_loc[
            du_lieu_loc["hang_xe"].astype(str).str.contains(
                hang, case=False, na=False, regex=False
            )
        ]

    try:
        if tuoi_tu:
            du_lieu_loc = du_lieu_loc[
                du_lieu_loc["tuoi_xe"] >= int(tuoi_tu)
            ]
        if tuoi_den:
            du_lieu_loc = du_lieu_loc[
                du_lieu_loc["tuoi_xe"] <= int(tuoi_den)
            ]
        if gia_tu:
            du_lieu_loc = du_lieu_loc[
                du_lieu_loc["gia_ban"] >= float(gia_tu)
            ]
        if gia_den:
            du_lieu_loc = du_lieu_loc[
                du_lieu_loc["gia_ban"] <= float(gia_den)
            ]
    except ValueError:
        return jsonify({"loi": "Giá trị bộ lọc không hợp lệ"}), 400

    if tuoi_tu and tuoi_den and int(tuoi_tu) > int(tuoi_den):
        return jsonify({"loi": "Khoảng tuổi xe không hợp lệ"}), 400
    if gia_tu and gia_den and float(gia_tu) > float(gia_den):
        return jsonify({"loi": "Khoảng giá không hợp lệ"}), 400

    if du_lieu_loc.empty:
        return jsonify({
            "loi": "Không tìm thấy dữ liệu thống kê"
        }), 404

    tong_quan = tinh_chi_so(du_lieu_loc)

    # Top 10 hang xe theo so luong tin dang
    top_hang = (
        du_lieu_loc.groupby("hang_xe")["gia_ban"]
        .count()
        .sort_values(ascending=False)
        .head(10)
    )

    bieu_do_hang = []

    for hang, so_luong in top_hang.items():
        bieu_do_hang.append({
            "hang_xe": str(hang),
            "so_xe": int(so_luong)
        })

    # Bang so sanh theo hang xe
    bang_hang = tao_bang_theo_nhom(
        du_lieu_loc,
        "hang_xe"
    )

    bang_hang.sort(
        key=lambda x: x["so_xe"],
        reverse=True
    )

    # Bang so sanh theo tuoi xe
    bang_tuoi = tao_bang_theo_nhom(
        du_lieu_loc,
        "tuoi_xe"
    )

    bang_tuoi.sort(
        key=lambda x: x["gia_tri"]
    )

    return jsonify({
        "bo_loc": {
            "hang": hang,
            "tuoi_tu": tuoi_tu,
            "tuoi_den": tuoi_den,
            "gia_tu": gia_tu,
            "gia_den": gia_den
        },
        "tong_quan": tong_quan,
        "phan_bo_gia": tao_bieu_do_phan_bo(du_lieu_loc),
        "top_hang_xe": bieu_do_hang,
        "bang_theo_hang": bang_hang,
        "bang_theo_tuoi": bang_tuoi
    })


if __name__ == "__main__":
    app.run(debug=True)
