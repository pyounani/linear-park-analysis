# preprocess_area.py
# ------------------
import pandas as pd
from pathlib import Path

# 0. 경로
RAW_PATH = Path("raw") / "행정구역(동별)_2025.csv"   # 실제 원본 CSV
OUT_PATH = Path("mapping") / "행정동면적.csv"       # 저장 위치

# 1. 로드 (3줄 헤더)
df_raw = pd.read_csv(RAW_PATH, header=[0, 1, 2], encoding="utf-8")

# 2. 멀티헤더 평탄화
df_raw.columns = ["_".join(col).strip() for col in df_raw.columns.values]

# ── 2-1. ***실제 컬럼명 자동 탐색*** ──────────────────────────
col_sid  = [c for c in df_raw.columns if c.startswith("동별(1)_")][0]   # 시·도
col_gu   = [c for c in df_raw.columns if c.startswith("동별(2)_")][0]   # 구
col_dong = [c for c in df_raw.columns if c.startswith("동별(3)_")][0]   # 행정동
col_area = [c for c in df_raw.columns if "면적 (k" in c][0]             # 면적(k㎡)

# 3. 필요한 열만 추출 & 리네임
df = (
    df_raw[[col_sid, col_gu, col_dong, col_area]]
    .rename(columns={
        col_sid:  "시도",
        col_gu:   "구",
        col_dong: "행정동명",
        col_area: "area_km2_raw",
    })
)

# 4. ‘소계’·NaN 행 제거
df = df[
    df["행정동명"].notna() &
    ~df["행정동명"].str.contains("소계")
]

# 5. 면적 숫자화
df["area_km2"] = (
    df["area_km2_raw"]
      .astype(str)
      .str.replace(",", "", regex=False)
      .astype(float)
)
df = df.drop(columns="area_km2_raw")

# 6. 저장
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df[["시도", "구", "행정동명", "area_km2"]].to_csv(
    OUT_PATH, index=False, encoding="utf-8-sig"
)
print(f"✅ 행정동 면적 파일 저장 완료 → {OUT_PATH}")
