import numpy as np

NGUONG_TUOI_KM0 = 3   # xe tu 3 tuoi tro len ma km = 0 duoc coi la chua nhap so km


def sua_km(d):
    """Dat km = 0 cua xe tu 3 tuoi tro len thanh thieu va them cot co km_khong_ro."""
    d = d.copy()
    nghi_van = (d["so_km_da_di"] == 0) & (d["tuoi_xe"] >= NGUONG_TUOI_KM0)
    d["km_khong_ro"] = nghi_van.astype(int)
    d.loc[nghi_van, "so_km_da_di"] = np.nan
    return d
