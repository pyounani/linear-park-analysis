import pandas as pd

# ─── 1. 경로 지정 ───
SUB_PATH = "processed/subway_with_admdong.csv"   # 입력
OUT_PATH = "processed/행정동별_역개수.csv"        # 출력(추천 파일명)

# ─── 2. 데이터 불러오기 ───
sub = pd.read_csv(SUB_PATH, encoding="utf-8-sig")

# ─── 3. 컬럼 통일 및 공백 제거 ───
sub = sub.rename(columns={"시도": "시도", "시군구": "구", "행정동": "행정동명"})
for col in ["시도", "구", "행정동명"]:
    sub[col] = sub[col].astype(str).str.strip()

# ─── 4. 행정동별 역 개수 집계 ───
cnt = (
    sub.groupby(["시도", "구", "행정동명"], as_index=False)
       .size()
       .rename(columns={"size": "subway_cnt"})
)

# ★ 4-1. 행정동명이 NaN(또는 공백)인 행 제거
cnt = cnt.dropna(subset=["행정동명"])                # NaN 제거
cnt = cnt[cnt["행정동명"].str.strip() != ""]         # 공백 문자열 제거(선택)

# ─── 5. 저장 ───
cnt.to_csv("processed/행정동별_지하철역개수.csv", index=False, encoding="utf-8-sig")
print("✓ NaN 행 제거 후 저장 완료")


##########################
import numpy as np

cnt = pd.read_csv("processed/행정동별_지하철역개수.csv", encoding="utf-8-sig")

# 1) 'nan'·빈칸 문자열을 실제 NaN으로 변환
cnt.replace(["nan", "NaN", ""], np.nan, inplace=True)

# 2) NaN 행 제거
cnt = cnt.dropna(subset=["구", "행정동명"])

# 3) 공백만 남은 셀 제거  (두 방법 중 택1)
cnt = cnt[(cnt["구"].str.strip() != "") & (cnt["행정동명"].str.strip() != "")]
# cnt = cnt[cnt["구"].str.strip().ne("") & cnt["행정동명"].str.strip().ne("")]

# 4) 저장
cnt.to_csv("processed/행정동별_지하철역개수.csv", index=False, encoding="utf-8-sig")
print("✓ 'nan' 문자열 및 공백 행 삭제 후 덮어쓰기 완료")