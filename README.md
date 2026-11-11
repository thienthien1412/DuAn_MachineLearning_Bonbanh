# DỰ ÁN MACHINE LEARNING: DỰ ĐOÁN GIÁ RAO BÁN Ô TÔ ĐÃ QUA SỬ DỤNG

## 1. Giới thiệu

Dự án xây dựng mô hình Machine Learning nhằm dự đoán giá rao bán ô tô đã qua sử dụng dựa trên các đặc điểm của xe.

Nguồn dữ liệu được thu thập từ website Bonbanh.com.

Dự án được thực hiện theo các giai đoạn: thu thập dữ liệu, phân tích khám phá, tiền xử lý dữ liệu, xây dựng mô hình và đánh giá kết quả.

## 2. Công nghệ sử dụng

- Python
- Requests, BeautifulSoup, lxml
- Pandas, NumPy
- SQLite
- Scikit-learn (giai đoạn xây dựng mô hình)

## 3. Cấu trúc dự án

```text
DuAn/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   └── scraper.py
├── data/
│   ├── database/
│   ├── raw/
│   └── processed/
├── logs/
└── reports/
```

**Chức năng chính:**

- `main.py`: Điều khiển quá trình thu thập dữ liệu.
- `src/config.py`: Chứa các thông số cấu hình.
- `src/database.py`: Khởi tạo và thao tác với cơ sở dữ liệu SQLite.
- `src/scraper.py`: Thực hiện truy cập website và thu thập thông tin xe.
- `data/database/`: Lưu cơ sở dữ liệu SQLite.
- `data/raw/`: Lưu dữ liệu gốc sau thu thập.
- `data/processed/`: Lưu dữ liệu sau tiền xử lý.
- `reports/`: Lưu các báo cáo kiểm tra và phân tích dữ liệu.
- `logs/`: Lưu nhật ký hoạt động của chương trình.

## 4. Cài đặt môi trường

Yêu cầu Python đã được cài đặt trên máy.

Tạo môi trường ảo:

```powershell
python -m venv venv
```

Kích hoạt môi trường trên Windows:

```powershell
venv\Scripts\activate
```

Cài đặt các thư viện:

```powershell
pip install -r requirements.txt
```

## 5. Dữ liệu

Dữ liệu được thu thập từ các tin đăng ô tô trên Bonbanh.com.

Bộ dữ liệu hiện có:

- 22.932 tin đăng.
- 20 thuộc tính trong bộ dữ liệu CSV và Excel.
- Định dạng CSV, Excel và SQLite.

Các tệp dữ liệu được chia sẻ riêng qua Google Drive, không tải trực tiếp lên GitHub.

Sau khi nhận dữ liệu, đặt các tệp vào đúng thư mục:

```text
data/
├── database/
│   └── bonbanh.db
├── raw/
│   ├── bonbanh_raw.csv
│   └── bonbanh_raw.xlsx
└── processed/
```

Lưu ý: Không chỉnh sửa hoặc ghi đè lên các tệp dữ liệu gốc. Các bước xử lý tiếp theo cần tạo dữ liệu đầu ra riêng.

## 6. Quy trình thực hiện dự án

Dự án được triển khai theo các bước:

1. Thu thập dữ liệu từ Bonbanh.com.
2. Kiểm tra chất lượng và phân tích khám phá dữ liệu (EDA).
3. Tiền xử lý và xây dựng đặc trưng.
4. Xây dựng các mô hình Machine Learning.
5. Đánh giá và so sánh kết quả mô hình.
6. Xây dựng ứng dụng dự đoán giá xe.
7. Tổng kết và đề xuất hướng phát triển.

## 7. Lưu ý khi tiếp tục dự án

- Phần thu thập dữ liệu đã hoàn thành. Các thành viên tiếp tục sử dụng bộ dữ liệu được chia sẻ, không cần thu thập lại.
- Không chạy `python main.py` trong quá trình phân tích và xây dựng mô hình vì lệnh này khởi động chương trình thu thập dữ liệu.
- Không đưa dữ liệu gốc, môi trường ảo và nhật ký hoạt động lên GitHub.
- Các báo cáo và kết quả phân tích cần được lưu trong thư mục `reports/`.
- Mọi bước tiền xử lý cần giữ nguyên dữ liệu gốc và ghi nhận những thay đổi trên dữ liệu.

## 8. Nguồn dữ liệu

Website: https://bonbanh.com