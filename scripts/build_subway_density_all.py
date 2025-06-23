import pandas as pd, numpy as np, os

CNT_PATH  = "processed/행정동별_지하철역개수.csv"
AREA_PATH = "mapping/행정동면적.csv"
OUT_PATH  = "final/행정동별_지하철밀도.csv"

cnt  = pd.read_csv(CNT_PATH,  encoding="utf-8-sig")
area = pd.read_csv(AREA_PATH, encoding="utf-8-sig")

# ── 컬럼 정리 ───────────────────────────
cnt  = cnt.rename(columns={"행정동": "행정동명"})
area = area.rename(columns={"행정동": "행정동명"})
for df in (cnt, area):
    df["행정동명"] = df["행정동명"].astype(str).str.strip()

# ── 면적(left) 기준 병합 ────────────────
merged = (
    area[["행정동명", "area_km2"]]
    .merge(cnt[["행정동명", "subway_cnt"]], on="행정동명", how="left")
)

# 역이 없는 행정동 → subway_cnt = 0
merged["subway_cnt"] = merged["subway_cnt"].fillna(0).astype(int)

# ── 밀도 계산 ───────────────────────────
merged["subway_dens"] = (merged["subway_cnt"] / merged["area_km2"]).round(3)

# ── 저장 ───────────────────────────────
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
merged.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
print(f"✓ 모든 행정동 포함(역 0개 → 밀도 0) 저장 완료 → {OUT_PATH}")
