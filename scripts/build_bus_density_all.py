"""
build_bus_density_all.py
------------------------
- processed/bus_with_admdong.csv : 정류장 ↔ 행정동 매핑 결과
- mapping/행정동면적.csv         : 행정동 면적(area_km2)

→ final/행정동별_버스밀도.csv : bus_cnt=0 포함 전체 행정동
"""
import pandas as pd, os, numpy as np

# ─── 경로 설정 ───
BUS_PATH  = "processed/bus_with_admdong.csv"
AREA_PATH = "mapping/행정동면적.csv"
OUT_PATH  = "final/행정동별_버스밀도.csv"

# ─── 1. 데이터 불러오기 ───
bus  = pd.read_csv(BUS_PATH,  encoding="utf-8-sig")
area = pd.read_csv(AREA_PATH, encoding="utf-8-sig")

# ─── 2. 컬럼 정리 ───
bus  = bus.rename(columns={"행정동": "행정동명"})
area = area.rename(columns={"행정동": "행정동명"})
for df in (bus, area):
    df["행정동명"] = df["행정동명"].astype(str).str.strip()

# ─── 3. 행정동별 정류소 개수 집계 ───
bus_cnt = (
    bus.dropna(subset=["행정동명"])
       .groupby("행정동명", as_index=False)
       .size()
       .rename(columns={"size": "bus_cnt"})
)

# ─── 4. 면적(left) 기준 병합 → 없는 곳 0 보정 ───
merged = (
    area[["행정동명", "area_km2"]]          # 면적이 기준 (left)
    .merge(bus_cnt, on="행정동명", how="left")
    .assign(bus_cnt=lambda df: df["bus_cnt"].fillna(0).astype(int))
)

# ─── 5. 밀도 계산 ───
merged["bus_dens"] = (merged["bus_cnt"] / merged["area_km2"]).round(3)

# ─── 6. 저장 ───
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
merged.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
print(f"✓ 모든 행정동 포함 버스 밀도 저장 완료 → {OUT_PATH}")
