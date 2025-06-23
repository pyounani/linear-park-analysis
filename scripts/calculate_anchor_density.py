import pandas as pd

# 1) 데이터 로드
area_df = pd.read_csv(
    "mapping/행정동면적.csv",
    encoding="utf-8-sig",          # 파일 인코딩에 맞춰 조정
    dtype={"행정동명": str}
)  # 컬럼: 시도, 구, 행정동명, area_km2

fac_df = pd.read_csv(
    "processed/행정동별_집객시설수.csv",
    encoding="utf-8-sig",      # 저장할 때 utf-8-sig 사용하셨다면
    dtype={"행정동_코드": str, "행정동명": str}
)  # 컬럼: 행정동_코드, 행정동명, 집객시설_수

# 2) 병합 (행정동명 기준)
df = pd.merge(
    fac_df,
    area_df[["행정동명", "area_km2"]],
    on="행정동명",
    how="left"
)

# 3) 밀도 계산 (개수 / km²)
df["anchor_fac_dens"] = df["집객시설_수"] / df["area_km2"]

# 4) 컬럼 순서 정리 (원하는 순으로)
df = df[[
    "행정동_코드",
    "행정동명",
    "area_km2",
    "집객시설_수",
    "anchor_fac_dens"
]]

# 5) 결과 저장
df.to_csv(
    "final/행정동별_집객시설밀도.csv",
    index=False,
    encoding="utf-8-sig"
)

print("▶ 완료: final/행정동별_집객시설밀도.csv 생성")
