import pandas as pd
from pathlib import Path

SRC = Path("mapping/KIKcd_H.xlsx")
OUT = Path("mapping/행정동코드_매핑.csv")

df = (pd.read_excel(SRC, dtype={"행정동코드": str})
        .rename(columns={"행정동코드": "adm_cd", "읍면동명": "dong"})
        .loc[:, ["adm_cd", "dong"]])

# 말소된(폐지된) 코드 제외 → '말소일자' NaN 또는 '0' → keep
if "말소일자" in df.columns:
    df = df[df["말소일자"].isna() | (df["말소일자"] == 0)]
    df = df.drop(columns=["말소일자"])

df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"저장 완료 → {OUT} (행 {len(df)})")
