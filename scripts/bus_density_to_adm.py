"""
bus_density_to_adm.py
---------------------
버스 정류장 좌표 → 행정동 매핑 + 밀도 계산

* 입력
  raw/bus_stop_coords.csv   : 노드ID, 정류소명, X좌표(경도), Y좌표(위도) …
  mapping/adm_centroid.xlsx : 시도, 시군구, 읍면동, 위도, 경도
  mapping/행정동면적.csv     : 행정동명, area_km2

* 출력
  processed/bus_with_admdong.csv  : 정류장별 매핑 결과(거리_km 포함)
  final/행정동별_버스밀도.csv       : 행정동별 bus_cnt, area_km2, bus_dens
"""
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
import os

# ──────────────────────────────────────────────────────────────
# 0. 경로 설정
BUS_PATH   = "raw/bus_stop_coords.csv"
ADM_PATH   = "mapping/adm_centroid.xlsx"
AREA_PATH  = "mapping/행정동면적.csv"

OUT_BUS    = "processed/bus_with_admdong.csv"
OUT_DENS   = "final/행정동별_버스밀도.csv"
DIST_CUT   = 2.0        # km 초과 시 매칭 무효(선택, None이면 사용 안 함)
# ──────────────────────────────────────────────────────────────

# 1. 데이터 불러오기
bus = pd.read_csv(BUS_PATH,  encoding="cp949")   # 필요시 cp949
adm = pd.read_excel(ADM_PATH, sheet_name=0)

# 2. 좌표 컬럼 통일(X좌표→경도, Y좌표→위도) + 숫자화
bus = bus.rename(columns={"X좌표": "경도", "Y좌표": "위도"})
for df in (bus, adm):
    for col in ["위도", "경도"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# 결측 좌표 제거
bus = bus.dropna(subset=["위도", "경도"]).reset_index(drop=True)
adm = adm.dropna(subset=["위도", "경도"]).reset_index(drop=True)

# 3. 라디안 변환 → BallTree(Haversine) 최근접 매핑
bus_rad = np.deg2rad(bus[["위도", "경도"]].to_numpy())
adm_rad = np.deg2rad(adm[["위도", "경도"]].to_numpy())

tree = BallTree(adm_rad, metric="haversine")
dist, idx = tree.query(bus_rad, k=1)

# 4. 행정동 정보 붙이기
bus["행정동명"] = adm.loc[idx[:, 0], "읍면동/구"].values  # 실제 컬럼명 확인
bus["거리_km"]  = (dist[:, 0] * 6371).round(3)

# 거리 컷오프 적용(선택)
if DIST_CUT is not None:
    mask_far = bus["거리_km"] > DIST_CUT
    bus.loc[mask_far, "행정동명"] = np.nan     # 너무 먼 매칭 무효화

# 5. 매핑 결과 저장
os.makedirs("processed", exist_ok=True)
bus.to_csv(OUT_BUS, index=False, encoding="utf-8-sig")
print(f"✓ 버스 매핑 완료 → {OUT_BUS}  (총 {len(bus)}행)")

# 6. 행정동별 정류소 개수 집계
bus_cnt = (
    bus.dropna(subset=["행정동명"])            # 매칭 실패 행 제외
       .groupby("행정동명", as_index=False)
       .size()
       .rename(columns={"size": "bus_cnt"})
)

# 7. 면적과 병합(모든 행정동 유지) → 없는 곳 bus_cnt=0
area = pd.read_csv(AREA_PATH, encoding="utf-8-sig")[["행정동명", "area_km2"]]
merged = (
    area.merge(bus_cnt, on="행정동명", how="left")
         .assign(bus_cnt=lambda df: df["bus_cnt"].fillna(0).astype(int))
)
merged["bus_dens"] = (merged["bus_cnt"] / merged["area_km2"]).round(3)

# 8. 결과 저장
os.makedirs("final", exist_ok=True)
merged.to_csv(OUT_DENS, index=False, encoding="utf-8-sig")
print(f"✓ 행정동별 버스 밀도({len(merged)}행) 저장 완료 → {OUT_DENS}")

# ── 상위 10개 미리보기 ─────────────────────────────────────────
print(
    merged.sort_values("bus_dens", ascending=False)
          .head(10)[["행정동명", "bus_cnt", "area_km2", "bus_dens"]]
)
