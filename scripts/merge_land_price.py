"""
merge_land_price.py
-------------------------
raw/공시지가_2020.csv ~ 2024 → 법정동 단위 연도별 평균 + 5년 평균

출력: processed/공시지가_2020_2024_통합본.csv
"""

import pandas as pd
import glob, os
from functools import reduce

# ─────────────────── 0. 경로 설정 ───────────────────
RAW_DIR = "raw/공시지가"
OUT_CSV = "processed/공시지가_2020_2024_통합본.csv"

# ─────────────────── 1. 2020~2024 법정동 연도별 평균 ───────────────────
file_list = sorted(glob.glob(os.path.join(RAW_DIR, "공시지가_20*.csv")))

df_list = []
for file in file_list:
    year = os.path.basename(file).split("_")[1].split(".")[0]  # '2020'
    df   = pd.read_csv(file, encoding="cp949", dtype={'법정동코드': str})

    grp_cols = ['시도명', '시군구명', '법정동코드', '법정동명']
    df_year  = (df.groupby(grp_cols)[['공시지가(원/㎡)']]
                  .mean()
                  .reset_index()
                  .rename(columns={'공시지가(원/㎡)': year}))
    df_list.append(df_year)

key_cols = ['시도명', '시군구명', '법정동코드', '법정동명']
df_law   = reduce(lambda l, r: pd.merge(l, r, on=key_cols, how='outer'), df_list)

# ─────────────────── 2. 5개년 평균 컬럼 추가 ───────────────────
year_cols = [c for c in df_law.columns if isinstance(c, str) and c.startswith("20")]
print("연도컬럼:", year_cols)  # 디버깅용

df_law['평균_2020_2024'] = (
    df_law[year_cols]
    .mean(axis=1)
    .round(0)
    .astype('Int64')
)

# ─────────────────── 3. 저장 ───────────────────
os.makedirs("processed", exist_ok=True)
df_law.to_csv(OUT_CSV, index=False, encoding='utf-8-sig')
print("✅ 법정동 단위 + 5년 평균 저장 →", OUT_CSV)

