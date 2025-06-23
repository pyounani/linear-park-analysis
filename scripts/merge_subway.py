import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree   # pip install scikit-learn

# ─── 1. 데이터 불러오기 ───
SUB_PATH = "raw/subway_coords.csv"         # 역_ID, 역명, 위도, 경도 …
ADM_PATH = "mapping/adm_centroid.xlsx"     # 시도, 시군구, 읍면동, 위도, 경도 …

sub = pd.read_csv(SUB_PATH, encoding="cp949")
adm = pd.read_excel(ADM_PATH, sheet_name=0)

# ─── 2. 좌표 컬럼 정리 ───
LAT_COL, LNG_COL = "위도", "경도"          # 필요 시 수정
adm.columns = adm.columns.str.strip()     # 헤더 앞뒤 공백 제거

# 좌표를 숫자로 강제 변환 → 변환 실패면 NaN
adm[LAT_COL] = pd.to_numeric(adm[LAT_COL], errors="coerce")
adm[LNG_COL] = pd.to_numeric(adm[LNG_COL], errors="coerce")
sub[LAT_COL] = pd.to_numeric(sub[LAT_COL], errors="coerce")
sub[LNG_COL] = pd.to_numeric(sub[LNG_COL], errors="coerce")

# NaN 좌표 행 제거
adm = adm.dropna(subset=[LAT_COL, LNG_COL]).reset_index(drop=True)
sub = sub.dropna(subset=[LAT_COL, LNG_COL]).reset_index(drop=True)

# ─── 3. 라디안 변환 ───
adm_rad = np.deg2rad(adm[[LAT_COL, LNG_COL]].to_numpy())
sub_rad = np.deg2rad(sub[[LAT_COL, LNG_COL]].to_numpy())

# ─── 4. 최근접 행정동 매칭 ───
tree = BallTree(adm_rad, metric="haversine")
dist, idx = tree.query(sub_rad, k=1)            # sub 행마다 가장 가까운 adm 1개

# ─── 5. 컬럼 추가 ───
sub["시도"]    = adm.loc[idx[:, 0], "시도"].values
sub["시군구"]  = adm.loc[idx[:, 0], "시군구"].values
sub["행정동"]  = adm.loc[idx[:, 0], "읍면동/구"].values   # 컬럼명 맞춰 조정
sub["거리_km"] = (dist[:, 0] * 6371).round(3)             # 검증용 거리

# ─── 6. 저장 ───
OUT_PATH = "processed/subway_with_admdong.csv"
sub.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
print(f"✓ XLSX 매핑·NaN 처리 완료 → {OUT_PATH}")
