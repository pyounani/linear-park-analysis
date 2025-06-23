import pandas as pd

# 1) 매출 데이터 로드
sales = pd.read_csv(
    "raw/월별_행정동_서비스매출.csv",  # 실제 파일명으로 대체
    dtype={"행정동_코드": str},
    usecols=["행정동_코드", "행정동_코드_명", "당월_매출_금액"],
    encoding="cp949"
)

# 2) 행정동 면적 로드
area = pd.read_csv(
    "mapping/행정동면적.csv",
    dtype={"행정동명": str}
)  # 컬럼: 행정동명, area_km2

# 3) 행정동별 매출 합계 계산
grouped = (
    sales
    .groupby(["행정동_코드", "행정동_코드_명"], as_index=False)
    .agg({"당월_매출_금액": "sum"})
    .rename(columns={"당월_매출_금액": "총_매출_금액"})
)

# 4) 면적과 병합
df = pd.merge(
    grouped,
    area.rename(columns={"행정동명": "행정동_코드_명"}),
    on="행정동_코드_명",
    how="left"
)

# 5) 매출 밀도 계산 (원/㎢)
df["매출_밀도"] = df["총_매출_금액"] / df["area_km2"]

# 6) 결과 저장
df = df[[
    "행정동_코드", "행정동_코드_명", "area_km2", "총_매출_금액", "매출_밀도"
]]
df.to_csv(
    "final/행정동별_매출밀도.csv",
    index=False,
    encoding="utf-8-sig"
)

print("✅ final/행정동별_매출밀도.csv 생성 완료")
