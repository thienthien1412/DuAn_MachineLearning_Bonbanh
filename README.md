# DỰ ÁN MACHINE LEARNING: DỰ ĐOÁN GIÁ RAO BÁN Ô TÔ ĐÃ QUA SỬ DỤNG

## 1. Giới thiệu

Dự án xây dựng hệ thống dự đoán giá rao bán ô tô đã qua sử dụng dựa trên các đặc điểm của xe bằng phương pháp Machine Learning.

Nguồn dữ liệu được thu thập từ các tin đăng trên website Bonbanh.com. Dữ liệu sau khi thu thập được kiểm tra chất lượng, phân tích khám phá và tiền xử lý trước khi sử dụng để xây dựng mô hình.

Dự án hướng đến việc ứng dụng mô hình dự đoán vào một hệ thống hỗ trợ người dùng tham khảo giá xe trên thị trường.

## 2. Công nghệ sử dụng

- Python
- Requests, BeautifulSoup, lxml: thu thập dữ liệu từ website.
- SQLite: lưu trữ dữ liệu trong quá trình thu thập.
- Pandas, NumPy: xử lý và phân tích dữ liệu.
- Matplotlib, Seaborn: trực quan hóa dữ liệu.
- Scikit-learn: tiền xử lý dữ liệu, xây dựng và đánh giá mô hình.
- XGBoost: xây dựng mô hình dự đoán.
- Joblib: lưu trữ mô hình và các thành phần phục vụ dự đoán.

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
│   ├── scraper.py
│   ├── preprocessing.py
│   ├── data_preparation.py
│   └── model/
│       ├── model_training.py
│       ├── model_training_cu.py
│       ├── model_training_tu_khoa.py
│       ├── feature_experiment.py
│       ├── phan_tich_tu_khoa.py
│       ├── thu_nghiem_extra_trees.py
│       ├── final_model.py
│       └── evaluate_final.py
├── data/
│   └── processed/
│       └── bonbanh_processed.csv
├── models/
│   └── random_forest_final.joblib
├── reports/
│   ├── charts/
│   └── model/
├── logs/
└── DuDoanGiaOto_Chuong3_4_5 (1).ipynb
```

### Chức năng các thành phần chính

- `main.py`: điều khiển quá trình thu thập dữ liệu.
- `src/config.py`: lưu các thông số cấu hình.
- `src/database.py`: khởi tạo và thao tác với cơ sở dữ liệu SQLite.
- `src/scraper.py`: truy cập website và thu thập thông tin xe.
- `src/preprocessing.py`: kiểm tra, làm sạch và xây dựng đặc trưng dữ liệu.
- `src/data_preparation.py`: chuẩn bị dữ liệu phục vụ huấn luyện và đánh giá.
- `src/model/`: chứa các chương trình huấn luyện, thử nghiệm và đánh giá mô hình.
- `data/processed/`: lưu bộ dữ liệu sau tiền xử lý.
- `models/`: lưu các mô hình Machine Learning đã được huấn luyện.
- `reports/`: lưu báo cáo và kết quả thực nghiệm.
- `reports/charts/`: lưu biểu đồ phân tích dữ liệu.
- `reports/model/`: lưu báo cáo liên quan đến quá trình xây dựng và đánh giá mô hình.
- `logs/`: lưu nhật ký hoạt động của chương trình.
- `DuDoanGiaOto_Chuong3_4_5 (1).ipynb`: notebook thực nghiệm và xây dựng mô hình.

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

Dữ liệu được thu thập từ các tin đăng ô tô trên website Bonbanh.com.

### 5.1. Dữ liệu thô

- Số lượng: 22.932 tin đăng.
- Số thuộc tính: 20.
- Định dạng: CSV, Excel và SQLite.

### 5.2. Dữ liệu sau tiền xử lý

Sau quá trình kiểm tra, làm sạch và xây dựng đặc trưng, bộ dữ liệu hiện tại có:

- Số lượng: 22.728 dòng.
- Số thuộc tính: 21.
- Tệp dữ liệu: `data/processed/bonbanh_processed.csv`.

Bộ dữ liệu thô và cơ sở dữ liệu được chia sẻ riêng qua Google Drive. Bộ dữ liệu sau tiền xử lý được lưu trong thư mục `data/processed/` trên GitHub để thuận tiện cho các thành viên sử dụng.

Lưu ý:
- Không chỉnh sửa hoặc ghi đè lên dữ liệu thô.
- Các bước xử lý cần tạo dữ liệu đầu ra riêng.
- Các tệp chia tập huấn luyện, kiểm định và kiểm tra được tạo trong quá trình thực nghiệm, không lưu cố định trên GitHub.

## 6. Quy trình thực hiện dự án

Dự án được triển khai theo các giai đoạn:

1. Thu thập dữ liệu từ Bonbanh.com.
2. Kiểm tra chất lượng và phân tích khám phá dữ liệu (EDA).
3. Tiền xử lý dữ liệu và xây dựng đặc trưng.
4. Chuẩn bị dữ liệu cho quá trình huấn luyện và đánh giá.
5. Xây dựng, tối ưu và so sánh các mô hình Machine Learning.
6. Xây dựng ứng dụng hỗ trợ dự đoán và tham khảo giá xe.
7. Tổng kết và đề xuất hướng phát triển.

## 7. Lưu ý khi tiếp tục dự án

- Phần thu thập dữ liệu đã hoàn thành. Các thành viên sử dụng bộ dữ liệu đã được chia sẻ, không cần thu thập lại.
- Không chạy `python main.py` trong quá trình phân tích và xây dựng mô hình vì lệnh này khởi động chương trình thu thập dữ liệu.
- Không đưa dữ liệu thô, cơ sở dữ liệu, môi trường ảo và nhật ký hoạt động lên GitHub.
- Lưu các báo cáo và kết quả phân tích trong thư mục `reports/`.
- Giữ nguyên dữ liệu gốc trong suốt quá trình tiền xử lý.
- Khi thay đổi quy trình xử lý hoặc xây dựng mô hình, cần kiểm tra lại kết quả để bảo đảm tính nhất quán.

## 8. Nguồn dữ liệu

Website: https://bonbanh.com
