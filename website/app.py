
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
    cot_loc = ["hang_xe", "khu_vuc", "kieu_dang", "hop_so", "xuat_xu"]
    lua_chon = {}

    for cot in cot_loc:
        if cot in DU_LIEU_XE.columns:
            lua_chon[cot] = sorted(
                DU_LIEU_XE[cot].dropna().astype(str).unique().tolist()
            )
        else:
            lua_chon[cot] = []

    lua_chon["tuoi_xe"] = sorted(
        DU_LIEU_XE["tuoi_xe"].dropna().astype(int).unique().tolist()
    )

    return jsonify(lua_chon)


# --------------------------------------------------
# API THONG KE DASHBOARD
# --------------------------------------------------

@app.route("/api/statistics", methods=["GET"])
def thong_ke_thi_truong():
    cot_loc = ["hang_xe", "tuoi_xe", "khu_vuc", "kieu_dang", "hop_so", "xuat_xu"]
    du_lieu_loc = DU_LIEU_XE.copy()
    dieu_kien = []

    for cot in cot_loc:
        cac_gia_tri = request.args.getlist(cot)

        if not cac_gia_tri:
            continue

        if cot == "tuoi_xe":
            try:
                cac_gia_tri = [int(x) for x in cac_gia_tri]
            except ValueError:
                return jsonify({"loi": "Giá trị tuổi xe không hợp lệ"}), 400

            du_lieu_loc = du_lieu_loc[du_lieu_loc[cot].isin(cac_gia_tri)]
        else:
            du_lieu_loc = du_lieu_loc[
                du_lieu_loc[cot].astype(str).isin(cac_gia_tri)
            ]

        dieu_kien.append({
            "hang_xe": "hãng xe",
            "tuoi_xe": "tuổi xe",
            "khu_vuc": "khu vực",
            "kieu_dang": "kiểu dáng",
            "hop_so": "hộp số",
            "xuat_xu": "xuất xứ"
        }[cot])

    tong_quan = tinh_chi_so(du_lieu_loc)

    bang_hang = tao_bang_theo_nhom(du_lieu_loc, "hang_xe")
    bang_hang.sort(key=lambda x: x["so_xe"], reverse=True)

    bang_tuoi = tao_bang_theo_nhom(du_lieu_loc, "tuoi_xe")
    bang_tuoi.sort(key=lambda x: x["gia_tri"])

    cot_nhom = "kieu_dang" if request.args.getlist("hang_xe") else "hang_xe"
    ten_nhom = "kiểu dáng" if cot_nhom == "kieu_dang" else "hãng xe"

    nhom = (
        du_lieu_loc.groupby(cot_nhom)["gia_ban"]
        .count()
        .sort_values(ascending=False)
        .head(10)
    )

    phan_tich_nhom = [
        {"gia_tri": str(gia_tri), "so_xe": int(so_luong)}
        for gia_tri, so_luong in nhom.items()
    ]

    phan_bo = tao_bieu_do_phan_bo(du_lieu_loc)
    insights = []
    tong_so = len(du_lieu_loc)

    if tong_so:
        ti_le = tong_so / len(DU_LIEU_XE) * 100 if len(DU_LIEU_XE) else 0
        insights.append(
            f"Có {tong_so:,} tin đăng phù hợp, chiếm {ti_le:.1f}% tổng số tin trong tập dữ liệu."
        )

        if bang_hang:
            hang_dau = bang_hang[0]
            insights.append(
                f"{hang_dau['gia_tri']} là hãng có nhiều tin đăng nhất "
                f"({hang_dau['so_xe']:,} tin, chiếm {hang_dau['so_xe']/tong_so*100:.1f}% trong phạm vi lọc)."
            )

        if phan_bo:
            khoang = max(phan_bo, key=lambda x: x["so_xe"])
            insights.append(
                f"Khoảng giá có nhiều tin nhất là {khoang['tu']/1e9:.2f}–{khoang['den']/1e9:.2f} tỷ đồng "
                f"với {khoang['so_xe']:,} tin đăng."
            )

        nhom_tuoi = [x for x in bang_tuoi if x["so_xe"] >= 10]
        if nhom_tuoi:
            tuoi_cao = max(nhom_tuoi, key=lambda x: x["gia_trung_vi"])
            insights.append(
                f"Nhóm xe {tuoi_cao['gia_tri']} năm có giá trung vị cao nhất "
                f"trong các nhóm có ít nhất 10 tin ({tuoi_cao['gia_trung_vi']/1e9:.2f} tỷ đồng)."
            )

        if tong_quan and tong_quan["gia_trung_vi"] > 0:
            chenhlech = (
                tong_quan["gia_trung_binh"] / tong_quan["gia_trung_vi"] - 1
            ) * 100

            if abs(chenhlech) >= 10:
                huong = "cao hơn" if chenhlech > 0 else "thấp hơn"
                insights.append(
                    f"Giá trung bình {huong} giá trung vị {abs(chenhlech):.1f}%, "
                    "cho thấy một số tin có mức giá xa trung tâm có thể ảnh hưởng đến số trung bình."
                )
            else:
                insights.append(
                    "Giá trung bình và trung vị tương đối gần nhau trong phạm vi đang chọn."
                )

    return jsonify({
        "tong_quan": tong_quan,
        "phan_bo_gia": phan_bo,
        "phan_tich_nhom": phan_tich_nhom,
        "ten_nhom": ten_nhom,
        "bang_theo_hang": bang_hang,
        "bang_theo_tuoi": bang_tuoi,
        "insights": insights,
        "mo_ta_pham_vi": (
            "Toàn bộ thị trường"
            if not dieu_kien
            else "Đang lọc theo: " + ", ".join(dieu_kien)
        )
    })


if __name__ == "__main__":
    app.run(debug=True)
