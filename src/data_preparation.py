
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


THU_MUC_DU_AN = Path(__file__).resolve().parent.parent

DUONG_DAN_DU_LIEU = (
    THU_MUC_DU_AN
    / "data"
    / "processed"
    / "bonbanh_processed.csv"
)

THU_MUC_LUU = (
    THU_MUC_DU_AN
    / "data"
    / "splits"
)


def chia_du_lieu():
    df = pd.read_csv(DUONG_DAN_DU_LIEU)

    du_lieu_train, du_lieu_con_lai = train_test_split(
        df,
        test_size=0.30,
        random_state=42
    )

    du_lieu_validation, du_lieu_test = train_test_split(
        du_lieu_con_lai,
        test_size=0.50,
        random_state=42
    )

    THU_MUC_LUU.mkdir(
        parents=True,
        exist_ok=True
    )

    du_lieu_train.to_csv(
        THU_MUC_LUU / "train.csv",
        index=False,
        encoding="utf-8-sig"
    )

    du_lieu_validation.to_csv(
        THU_MUC_LUU / "validation.csv",
        index=False,
        encoding="utf-8-sig"
    )

    du_lieu_test.to_csv(
        THU_MUC_LUU / "test.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("KET QUA PHAN CHIA DU LIEU")

    print("Tong so dong:", len(df))

    print("\nKICH THUOC CAC TAP")
    print("Train:", du_lieu_train.shape)
    print("Validation:", du_lieu_validation.shape)
    print("Test:", du_lieu_test.shape)

    print("\nTY LE PHAN CHIA")
    print(
        "Train:",
        f"{len(du_lieu_train) / len(df) * 100:.2f}%"
    )
    print(
        "Validation:",
        f"{len(du_lieu_validation) / len(df) * 100:.2f}%"
    )
    print(
        "Test:",
        f"{len(du_lieu_test) / len(df) * 100:.2f}%"
    )

    print("\nTHONG KE GIA BAN")
    print(
        "Train:",
        f"{du_lieu_train['gia_ban'].median():,.0f} VND"
    )
    print(
        "Validation:",
        f"{du_lieu_validation['gia_ban'].median():,.0f} VND"
    )
    print(
        "Test:",
        f"{du_lieu_test['gia_ban'].median():,.0f} VND"
    )

    print("\nDA LUU 3 TAP DU LIEU TAI:")
    print(THU_MUC_LUU)


if __name__ == "__main__":
    chia_du_lieu()
