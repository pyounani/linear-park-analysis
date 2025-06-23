import pandas as pd
import numpy as np
import os

# ─── 1. 경로 설정 ───
CNT_PATH  = "processed/행정동별_지하철역개수.csv"   # 역 개수
AREA_PATH = "mapping/행정동면적.csv"             # 행정동 면적
OUT_PATH  = "final/행정동별_지하철밀도.csv"        # 결과 저장

# ─── 2. 데이터 불러오기 ───
cnt  = pd.read_csv(CNT_PATH,  encoding="utf-8-sig")
area = pd.read_csv(AREA_PATH, encoding="utf-8-sig")

# ─── 3. 필수 컬럼 정리 ───
cnt  = cnt.rename(columns={"행정동": "행정동명"})   # 혹시 모를 변형 대비
area = area.rename(columns={"행정동": "행정동명"})

# 문자열 'nan'·빈칸을 실제 NaN으로 변환 후 제거
cnt.replace(["nan", "NaN", ""], np.nan, inplace=True)
cnt = cnt.dropna(subset=["행정동명"]).copy()

# 공백 제거
cnt["행정동명"]  = cnt["행정동명"].str.strip()
area["행정동명"] = area["행정동명"].str.strip()

# ─── 4. 조인(행정동명 하나만 키) ───
merged = cnt.merge(
    area[["행정동명", "area_km2"]],
    on="행정동명",
    how="inner"       # 둘 다 있는 행정동만 남김
)

# ─── 5. 밀도 계산 ───
merged["subway_dens"] = (merged["subway_cnt"] / merged["area_km2"]).round(3)

# ─── 6. 저장 ───
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
merged.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
print(f"✓ 행정동별 지하철 밀도({len(merged)}행) 저장 완료 → {OUT_PATH}")
