\# Dự án Machine Learning: Dự đoán giá ô tô đã qua sử dụng



\## 1. Giới thiệu



Dự án xây dựng mô hình Machine Learning nhằm dự đoán giá rao bán ô tô đã qua sử dụng dựa trên các đặc điểm của xe.



Nguồn dữ liệu: Bonbanh.com.



\## 2. Công nghệ sử dụng



\- Python

\- Requests

\- BeautifulSoup

\- Pandas

\- SQLite

\- Scikit-learn (giai đoạn xây dựng mô hình)



\## 3. Cấu trúc dự án



DuAn/

├── main.py

├── requirements.txt

├── README.md

├── src/

│   ├── config.py

│   ├── database.py

│   └── scraper.py

├── data/

│   ├── database/

│   ├── raw/

│   └── processed/

├── logs/

└── reports/



\## 4. Cài đặt môi trường



Yêu cầu Python đã được cài đặt trên máy.



Tạo môi trường ảo:



python -m venv venv



Kích hoạt môi trường trên Windows:



venv\\Scripts\\activate



Cài đặt thư viện:



pip install -r requirements.txt



\## 5. Chạy chương trình



python main.py



\## 6. Dữ liệu



Dữ liệu được thu thập từ các tin đăng ô tô đã qua sử dụng trên Bonbanh.com.



Bộ dữ liệu sau thu thập gồm:

\- 22.932 tin đăng.

\- 20 thuộc tính.

\- Định dạng CSV và Excel.

\- Cơ sở dữ liệu SQLite.



Lưu ý: Dữ liệu không được tải lên repository GitHub. Các thành viên nhận dữ liệu qua thư mục chia sẻ riêng.



\## 7. Nguồn dữ liệu



Website: https://bonbanh.com

