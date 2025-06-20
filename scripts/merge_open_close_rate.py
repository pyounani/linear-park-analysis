"""
merge_open_close_rate.py

2020~2024년 서울시 행정동별 개업률 및 폐업률 데이터를 통합하여
행정동 단위 평균 개폐업률을 구하고, processed/ 폴더에 저장합니다.

입력: raw/서울시_상권분석서비스(점포-행정동)_2020년.csv ~ 2024년.csv
출력: processed/개폐업률_2020_2024_통합본.csv
"""

import pandas as pd
import glob
import os
from functools import reduce

# 1. 점포 데이터 CSV 목록
file_list = sorted(glob.glob("raw/서울시_상권분석서비스(점포-행정동)_20*년.csv"))

open_rate_list = []
close_rate_list = []

for file in file_list:
    year = os.path.basename(file).split("_")[-1].split("년")[0]  # '2020' ~ '2024'
    df = pd.read_csv(file, encoding='cp949')
    
    # 개폐업률 평균 계산 (행정동 기준)
    df_grouped = df.groupby(['행정동_코드_명'])[['개업_율', '폐업_률']].mean().reset_index()
    df_grouped_open = df_grouped[['행정동_코드_명', '개업_율']].copy()
    df_grouped_close = df_grouped[['행정동_코드_명', '폐업_률']].copy()

    df_grouped_open.rename(columns={'개업_율': f'개업률_{year}'}, inplace=True)
    df_grouped_close.rename(columns={'폐업_률': f'폐업률_{year}'}, inplace=True)

    open_rate_list.append(df_grouped_open)
    close_rate_list.append(df_grouped_close)

# 병합 (개업률 + 폐업률)
df_open = reduce(lambda left, right: pd.merge(left, right, on='행정동_코드_명', how='outer'), open_rate_list)
df_close = reduce(lambda left, right: pd.merge(left, right, on='행정동_코드_명', how='outer'), close_rate_list)

# 통합
df_merged = pd.merge(df_open, df_close, on='행정동_코드_명', how='inner')

# 저장
df_merged.to_csv("processed/개폐업률_2020_2024_통합본.csv", index=False, encoding='utf-8-sig')
print("개폐업률 통합 완료: processed/개폐업률_2020_2024_통합본.csv")
