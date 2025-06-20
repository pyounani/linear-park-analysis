"""
merge_estimated_sales.py

2020~2024년 서울시 행정동별 추정매출액 데이터를 통합하여
행정동 단위 평균 매출액을 구하고, processed/ 폴더에 저장합니다.

입력: raw/서울시_상권분석서비스(추정매출-행정동)_2020년.csv ~ 2024년.csv
출력: processed/추정매출_2020_2024_통합본.csv
"""

import pandas as pd
import glob
import os
from functools import reduce

# 1. 추정매출 CSV 파일 목록 가져오기
file_list = sorted(glob.glob("raw/서울시_상권분석서비스(추정매출-행정동)_20*년.csv"))

df_list = []

for file in file_list:
    year = os.path.basename(file).split("_")[-1].split("년")[0]  # '2020' ~ '2024'
    df = pd.read_csv(file, encoding='cp949')
    
    # 2. 컬럼명: '행정동_코드_명', '당월_매출_금액' 기준
    df_grouped = df.groupby(['행정동_코드_명'])[['당월_매출_금액']].mean().reset_index()
    df_grouped.rename(columns={'당월_매출_금액': year}, inplace=True)
    
    df_list.append(df_grouped)

# 3. 병합 (행정동명 기준)
df_merged = reduce(lambda left, right: pd.merge(left, right, on='행정동_코드_명', how='outer'), df_list)

# 4. 저장
df_merged.to_csv("processed/추정매출_2020_2024_통합본.csv", index=False, encoding='utf-8-sig')
print("✅ 추정매출 통합 완료: processed/추정매출_2020_2024_통합본.csv")
