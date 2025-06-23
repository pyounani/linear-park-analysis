import pandas as pd

# 1) 파일 로드 (CP949 인코딩 지정)
area_df = pd.read_csv(
    "raw/seoul_anchor_area.csv",
    encoding="cp949",
    dtype={"상권_코드": str, "행정동_코드": str}
)
fac_df = pd.read_csv(
    "raw/seoul_anchor_facilities.csv",
    encoding="cp949",
    dtype={"상권_코드": str}
)

# 2) 상권 ↔ 행정동 코드·명 매핑 추출
area_map = (
    area_df[["상권_코드", "행정동_코드", "행정동_코드_명"]]
    .drop_duplicates(subset=["상권_코드", "행정동_코드"])
)

# 3) (필요시) 집객시설 수 계산
# fac_df["집객시설_수"] = fac_df[[
#     "관공서_수","은행_수","종합병원ㆍ일반_병원","약국_수",
#     "유치원_수","초등학교_수","중학교_수","고등학교_수",
#     "대학교_수","백화점_수","슈퍼마켓_수","극장_수",
#     "숙박_시설_공항_수","철도_역_수","버스_터미널_수","지하철_역_버스_정거장_수"
# ]].sum(axis=1)

# 4) 상권코드 기준으로 병합
merged = pd.merge(
    area_map,
    fac_df[["상권_코드", "집객시설_수"]],
    on="상권_코드",
    how="left"
)

# 5) 행정동별로 집객시설 수 합계 + 컬럼명 변경
dong_fac = (
    merged
    .groupby(["행정동_코드", "행정동_코드_명"], as_index=False)
    .agg({"집객시설_수": "sum"})
    .rename(columns={"행정동_코드_명": "행정동명"})
)

# 6) 결과 확인 및 저장
print(dong_fac.head())
dong_fac.to_csv(
    "processed/행정동별_집객시설수.csv",
    index=False,
    encoding="utf-8-sig"
)
