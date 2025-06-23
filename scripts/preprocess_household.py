# preprocess_household.py
# -----------------------
# 원본: raw/행정동세대수_202505.csv
# 결과: processed/행정동세대수_202505.csv  (adm_cd, 행정동명, household_cnt)

import pandas as pd
from pathlib import Path

# ── 0. 경로 ────────────────────────────────────────────────
RAW_PATH = Path("raw")       / "행정동세대수_202505.csv"
OUT_PATH = Path("processed") / "행정동세대수_202505.csv"

# ── 1. 로드 ────────────────────────────────────────────────
df_raw = pd.read_csv(RAW_PATH, encoding="cp949")    # utf-8, utf-8-sig 둘 다 시도

# ── 2. 행정동 행만 필터링 ──────────────────────────────────
#  (1) '동(' 글자가 들어간 행   예) ... 청운효자동(1111051500)
#  (2) 전국·특별시·구(區) 등 집계 행 제거

df_dong = df_raw[df_raw["행정구역"].str.contains(r"동\(")]

# ── 3. 행정동명·코드 분리 ──────────────────────────────────
df_dong[["행정동명", "adm_cd"]] = df_dong["행정구역"]\
    .str.extract(r"(.+)\((\d{10})\)")

# 행정동명에서 시·구 접두어 제거
df_dong["행정동명"] = df_dong["행정동명"].str.split().str[-1]
#   → '서울특별시 종로구 청운효자동'  →  '청운효자동'

# ── 4. 세대수 숫자 변환 ────────────────────────────────────
col_hh = "2025년05월_전체세대"
df_dong["household_cnt"] = (
    df_dong[col_hh]
      .astype(str)
      .str.replace(",", "", regex=False)
      .astype(int)
)

# ── 5. 필요한 열만 선택 & 저장 ─────────────────────────────
df_out = df_dong[["adm_cd", "행정동명", "household_cnt"]]

OUT_PATH.parent.mkdir(exist_ok=True)
df_out.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
print(f"✅ 행정동 세대수 파일 저장 완료 → {OUT_PATH}")
