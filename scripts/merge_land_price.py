"""
merge_land_price.py

2020~2025년 공시지가 CSV 파일을 통합하여
법정동 단위 평균값을 계산한 뒤 processed/ 폴더에 저장하는 스크립트

입력: raw/공시지가_2020.csv ~ 공시지가_2025.csv
출력: processed/공시지가_2020_2025_통합본.csv
"""

import pandas as pd
import glob
import os
from functools import reduce

# 1. 공시지가 CSV 파일 목록 가져오기 (raw 폴더 기준)
file_list = sorted(glob.glob("raw/공시지가_20*.csv"))

df_list = []

for file in file_list:
    year = os.path.basename(file).split("_")[1].split(".")[0]  # '2020' ~ '2025'
    df = pd.read_csv(file, encoding='cp949')  # 한글 인코딩 대응
    
    # 2. 법정동 기준으로 평균 공시지가 계산
    df_grouped = df.groupby(['시도명', '시군구명', '법정동명'])[['공시지가(원/㎡)']].mean().reset_index()
    df_grouped.rename(columns={'공시지가(원/㎡)': year}, inplace=True)
    
    df_list.append(df_grouped)

# 3. 병합: 시도명, 시군구명, 법정동명 기준
df_merged = reduce(lambda left, right: pd.merge(left, right, on=['시도명', '시군구명', '법정동명'], how='outer'), df_list)

# 4. 결과 확인
print(df_merged.head())

# 5. processed 폴더에 저장
df_merged.to_csv("processed/공시지가_2020_2025_통합본.csv", index=False, encoding='utf-8-sig')
