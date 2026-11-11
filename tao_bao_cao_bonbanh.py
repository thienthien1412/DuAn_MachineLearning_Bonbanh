from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

# =========================================================
# TAO BAO CAO CHAT LUONG DU LIEU VA TU DIEN DU LIEU BONBANH
# Khong sua doi CSV goc.
# =========================================================

THU_MUC_GOC = Path(__file__).resolve().parent
DUONG_DAN_CSV = THU_MUC_GOC / "data" / "raw" / "bonbanh_raw.csv"
THU_MUC_BAO_CAO = THU_MUC_GOC / "reports"

FILE_CHAT_LUONG = THU_MUC_BAO_CAO / "data_quality_report.xlsx"
FILE_TU_DIEN = THU_MUC_BAO_CAO / "data_dictionary.xlsx"

if not DUONG_DAN_CSV.exists():
    raise FileNotFoundError(
        f"Khong tim thay file du lieu: {DUONG_DAN_CSV}\n"
        "Hay dat script tai thu muc goc DuAn."
    )

THU_MUC_BAO_CAO.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DUONG_DAN_CSV)

# Chuyen so km sang dang so de phuc vu thong ke, khong ghi nguoc vao CSV.
km_so = pd.to_numeric(
    df["so_km_da_di"].astype(str)
      .str.replace(" Km", "", regex=False)
      .str.replace(",", "", regex=False)
      .str.strip(),
    errors="coerce"
)

# ---------------------------------------------------------
# 1. Tong quan
# ---------------------------------------------------------
tong_quan = pd.DataFrame([
    ["Tổng số bản ghi", len(df), "Số dòng dữ liệu trong CSV"],
    ["Tổng số thuộc tính", len(df.columns), "Số cột trong CSV"],
    ["Số ô thiếu theo isna()", int(df.isna().sum().sum()), "Không bao gồm dấu '-'"],
    ["Số chuỗi rỗng", int(sum(df[c].astype(str).str.strip().eq("").sum() for c in df.columns)),
     "Kiểm tra chuỗi rỗng trên toàn bộ thuộc tính"],
    ["Số giá trị '-'", int(sum(df[c].astype(str).str.strip().eq("-").sum() for c in df.columns)),
     "Giá trị thay thế cần xem xét khi tiền xử lý"],
    ["Số mã tin trùng", int(df["ma_tin"].duplicated().sum()), "Kiểm tra trùng mã tin"],
    ["Số URL trùng", int(df["url"].duplicated().sum()), "Kiểm tra trùng URL"],
    ["Số bản ghi có số km >= 1.000.000", int((km_so >= 1_000_000).sum()),
     "Các trường hợp cần kiểm tra bất thường"],
    ["Số bản ghi năm sản xuất không thống nhất",
     int((df["nam_san_xuat"].astype(str).str.strip() !=
          df["nam_san_xuat_ct"].astype(str).str.strip()).sum()),
     "So sánh năm ở danh sách và năm ở trang chi tiết"],
], columns=["Chỉ tiêu", "Kết quả", "Diễn giải"])

# ---------------------------------------------------------
# 2. Chat luong tung cot
# ---------------------------------------------------------
chat_luong = pd.DataFrame({
    "Thuộc tính": df.columns,
    "Kiểu dữ liệu đọc vào": [str(df[c].dtype) for c in df.columns],
    "Số giá trị thiếu (NaN)": [int(df[c].isna().sum()) for c in df.columns],
    "Số chuỗi rỗng": [int(df[c].astype(str).str.strip().eq("").sum()) for c in df.columns],
    "Số giá trị '-'": [int(df[c].astype(str).str.strip().eq("-").sum()) for c in df.columns],
    "Số giá trị phân biệt": [int(df[c].nunique(dropna=True)) for c in df.columns],
})

# ---------------------------------------------------------
# 3. Thong ke gia ban
# ---------------------------------------------------------
gia = pd.to_numeric(df["gia_ban"], errors="coerce")
gia_thong_ke = pd.DataFrame([
    ["Số lượng", int(gia.count())],
    ["Trung bình (VND)", gia.mean()],
    ["Trung vị (VND)", gia.median()],
    ["Độ lệch chuẩn (VND)", gia.std()],
    ["Nhỏ nhất (VND)", gia.min()],
    ["Q1 (VND)", gia.quantile(0.25)],
    ["Q3 (VND)", gia.quantile(0.75)],
    ["Lớn nhất (VND)", gia.max()],
], columns=["Chỉ tiêu", "Giá trị"])

# Danh sach gia cao de kiem tra, khong tu dong loai bo.
gia_cao = df.loc[gia.nlargest(min(20, len(gia))).index,
                 ["ma_tin", "ten_xe", "nam_san_xuat_ct", "gia_ban", "khu_vuc", "url"]].copy()
gia_cao = gia_cao.sort_values("gia_ban", ascending=False)

# ---------------------------------------------------------
# 4. So km bat thuong
# ---------------------------------------------------------
ds_km_bat_thuong = df.loc[km_so >= 1_000_000,
                          ["ma_tin", "ten_xe", "nam_san_xuat_ct",
                           "so_km_da_di", "mo_ta", "gia_ban", "url"]].copy()
ds_km_bat_thuong.insert(4, "Số km sau khi chuyển đổi", km_so.loc[ds_km_bat_thuong.index])

km_thong_ke = pd.DataFrame([
    ["Số lượng chuyển đổi được", int(km_so.count())],
    ["Trung bình (km)", km_so.mean()],
    ["Trung vị (km)", km_so.median()],
    ["Nhỏ nhất (km)", km_so.min()],
    ["Q1 (km)", km_so.quantile(0.25)],
    ["Q3 (km)", km_so.quantile(0.75)],
    ["Lớn nhất (km)", km_so.max()],
    ["Số xe có số km bằng 0", int((km_so == 0).sum())],
    ["Số xe có số km >= 200.000", int((km_so >= 200_000).sum())],
    ["Số xe có số km >= 1.000.000", int((km_so >= 1_000_000).sum())],
], columns=["Chỉ tiêu", "Giá trị"])

# ---------------------------------------------------------
# 5. Nam san xuat khong thong nhat
# ---------------------------------------------------------
nam_ds = df["nam_san_xuat"].astype(str).str.strip()
nam_ct = df["nam_san_xuat_ct"].astype(str).str.strip()
mask_nam = nam_ds != nam_ct
nam_khac_nhau = df.loc[mask_nam, [
    "ma_tin", "ten_xe", "nam_san_xuat", "nam_san_xuat_ct", "url"
]].copy()

# ---------------------------------------------------------
# 6. Tu dien du lieu
# ---------------------------------------------------------
mo_ta = {
    "ma_tin": ("Mã tin đăng trên Bonbanh", "Mã định danh; không dùng làm biến đầu vào"),
    "ten_xe": ("Tên xe theo tin đăng", "Biến đầu vào; cần tách hãng, dòng xe, phiên bản nếu cần"),
    "tinh_trang": ("Tình trạng xe hiển thị ở trang danh sách", "Cần đánh giá; hiện tại chỉ có một giá trị"),
    "gia_ban": ("Giá rao bán của xe, đơn vị VND", "Biến mục tiêu cần dự đoán"),
    "khu_vuc": ("Khu vực đăng tin", "Biến đầu vào; có thể chuẩn hóa tỉnh/thành"),
    "nam_san_xuat": ("Năm sản xuất hiển thị ở trang danh sách", "Không ưu tiên nếu đã có năm chi tiết"),
    "mo_ta": ("Nội dung mô tả tin đăng", "Cần xử lý kỹ; tránh rò rỉ mục tiêu nếu chứa giá bán"),
    "url": ("Đường dẫn tin đăng", "Định danh/đối chiếu; không dùng làm biến đầu vào trực tiếp"),
    "nam_san_xuat_ct": ("Năm sản xuất lấy từ trang chi tiết", "Biến đầu vào; ưu tiên sử dụng thay cho nam_san_xuat"),
    "tinh_trang_ct": ("Tình trạng xe lấy từ trang chi tiết", "Cần đánh giá; hiện tại chỉ có một giá trị"),
    "so_km_da_di": ("Số km xe đã đi, đang lưu dưới dạng chuỗi có đơn vị", "Biến đầu vào; cần chuyển thành số và kiểm tra ngoại lệ"),
    "xuat_xu": ("Nguồn gốc/lắp ráp của xe", "Biến đầu vào dạng phân loại"),
    "kieu_dang": ("Kiểu dáng thân xe", "Biến đầu vào dạng phân loại"),
    "hop_so": ("Loại hộp số", "Biến đầu vào dạng phân loại; dấu '-' cần xử lý"),
    "dong_co": ("Thông tin động cơ", "Biến đầu vào; có thể trích xuất dung tích/nhiên liệu"),
    "mau_ngoai_that": ("Màu ngoại thất", "Biến đầu vào; có giá trị '-' cần xử lý"),
    "mau_noi_that": ("Màu nội thất", "Biến đầu vào; có nhiều giá trị '-' cần xử lý"),
    "so_cho_ngoi": ("Số chỗ ngồi", "Biến đầu vào; cần chuyển kiểu số nếu phù hợp"),
    "so_cua": ("Số cửa", "Biến đầu vào; cần chuyển kiểu số nếu phù hợp"),
    "dan_dong": ("Hệ dẫn động của xe", "Biến đầu vào dạng phân loại; dấu '-' cần xử lý"),
}

vai_tro = {
    "ma_tin": "Mã định danh",
    "gia_ban": "Biến mục tiêu (y)",
    "url": "Mã định danh/đối chiếu",
    "mo_ta": "Cần đánh giá nguy cơ rò rỉ dữ liệu",
    "tinh_trang": "Cần đánh giá (hiện là hằng số)",
    "tinh_trang_ct": "Cần đánh giá (hiện là hằng số)",
    "nam_san_xuat": "Không ưu tiên; trùng/khác cách biểu diễn với năm chi tiết",
}
tu_dien = pd.DataFrame([
    {
        "Tên thuộc tính": c,
        "Kiểu dữ liệu hiện tại": str(df[c].dtype),
        "Ý nghĩa": mo_ta.get(c, ("Chưa mô tả", "Cần đánh giá"))[0],
        "Vai trò dự kiến": vai_tro.get(c, mo_ta.get(c, ("", "Biến đầu vào"))[1]),
        "Ví dụ": str(df[c].dropna().iloc[0])[:120] if df[c].notna().any() else "",
    }
    for c in df.columns
])

# ---------------------------------------------------------
# Ghi file Excel
# ---------------------------------------------------------
with pd.ExcelWriter(FILE_CHAT_LUONG, engine="openpyxl") as writer:
    tong_quan.to_excel(writer, sheet_name="Tong_quan", index=False)
    chat_luong.to_excel(writer, sheet_name="Chat_luong_cot", index=False)
    gia_thong_ke.to_excel(writer, sheet_name="Thong_ke_gia", index=False)
    gia_cao.to_excel(writer, sheet_name="Top_20_gia_cao", index=False)
    km_thong_ke.to_excel(writer, sheet_name="Thong_ke_so_km", index=False)
    ds_km_bat_thuong.to_excel(writer, sheet_name="So_km_bat_thuong", index=False)
    nam_khac_nhau.to_excel(writer, sheet_name="Nam_khong_thong_nhat", index=False)

with pd.ExcelWriter(FILE_TU_DIEN, engine="openpyxl") as writer:
    tu_dien.to_excel(writer, sheet_name="Tu_dien_du_lieu", index=False)

# Dinh dang de doc de hon.
for file_excel in [FILE_CHAT_LUONG, FILE_TU_DIEN]:
    wb = load_workbook(file_excel)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="24476B")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.row_dimensions[1].height = 32

        for col_idx in range(1, ws.max_column + 1):
            values = [
                len(str(ws.cell(row=r, column=col_idx).value or ""))
                for r in range(1, min(ws.max_row, 100) + 1)
            ]
            do_rong = min(max(max(values, default=12) + 3, 12), 55)
            ws.column_dimensions[get_column_letter(col_idx)].width = do_rong

        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
    wb.save(file_excel)

print("DA TAO BAO CAO THANH CONG")
print(f"- {FILE_CHAT_LUONG}")
print(f"- {FILE_TU_DIEN}")
print(f"So dong du lieu: {len(df):,}")
print(f"So cot: {len(df.columns)}")
