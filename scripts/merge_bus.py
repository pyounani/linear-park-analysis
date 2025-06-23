import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
import os

# ─── 1. 경로 설정 ───
BUS_PATH = "raw/bus_stop_coords.csv"       # 노드ID, 정류소명, X좌표(경도), Y좌표(위도) …
ADM_PATH = "mapping/adm_centroid.xlsx"     # 시도, 시군구, 읍면동, 위도, 경도 …
OUT_PATH = "processed/bus_with_admdong.csv"

# ─── 2. 데이터 불러오기 ───
bus = pd.read_csv(BUS_PATH, encoding="cp949")      # 필요시 cp949
adm = pd.read_excel(ADM_PATH, sheet_name=0)            # 첫 시트

# ─── 3. 좌표 컬럼 정리 ───
# 버스: X좌표 = 경도(long), Y좌표 = 위도(lat)
bus = bus.rename(columns={"X좌표": "경도", "Y좌표": "위도"})
for col in ["위도", "경도"]:
    bus[col] = pd.to_numeric(bus[col], errors="coerce")
    adm[col] = pd.to_numeric(adm[col], errors="coerce")

# 결측 좌표 제거
bus = bus.dropna(subset=["위도", "경도"]).reset_index(drop=True)
adm = adm.dropna(subset=["위도", "경도"]).reset_index(drop=True)

# ─── 4. 라디안 변환 ───
bus_rad = np.deg2rad(bus[["위도", "경도"]].values)
adm_rad = np.deg2rad(adm[["위도", "경도"]].values)

# ─── 5. 최근접 행정동 매칭 ───
tree = BallTree(adm_rad, metric="haversine")
dist, idx = tree.query(bus_rad, k=1)          # 각 정류장마다 가장 가까운 행정동 1개

# ─── 6. 행정동 정보 붙이기 ───
bus["시도"]    = adm.loc[idx[:, 0], "시도"].values
bus["시군구"]  = adm.loc[idx[:, 0], "시군구"].values
bus["행정동명"] = adm.loc[idx[:, 0], "읍면동/구"].values   # 실제 컬럼명 맞춰 수정
bus["거리_km"]  = (dist[:, 0] * 6371).round(3)             # 검증용

# ─── 7. 저장 ───
os.makedirs("processed", exist_ok=True)
bus.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
print(f"✓ 버스 정류장 ↔ 행정동 매핑 완료 → {OUT_PATH}")
