# Ban giao mo hinh cho Chuong 6

1. Cai thu vien: pip install -r requirements.txt (dung dung phien ban de nap duoc mo hinh).
2. Giu NGUYEN cac tep trong thu muc nay cung nhau (model_final.joblib can tien_xu_ly_xe.py).
3. Dung thu:

    import du_doan
    kq = du_doan.du_doan_gia({...})      # dict gom cac cot trong thong_tin_mo_hinh.json -> dac_trung_dau_vao
    print(kq["gia_du_doan"], kq["khoang_tham_khao"])

4. Cac lua chon cho o nhap: lua_chon_dau_vao.json. Cot nao nam trong co_the_de_trong thi cho phep bo trong.
5. Kiem tra (muc 6.4.2): chay du_doan_gia tren cac dong cua mau_kiem_tra.csv, ket qua phai khop cot gia_du_doan_mong_doi.
6. Gia du doan la gia RAO BAN tham khao tren Bonbanh, khong phai gia giao dich; khoang tham khao chua khoang 80% xe trong tap Test.
