import pandas as pd
import glob
import os

# 1) 각 년도 파일에서 법정동명과 공시지가 컬럼만 읽어서 리스트에 담기
dfs = []
for path in sorted(glob.glob("raw/공시지가/공시지가_*.csv")):
    df = pd.read_csv(
        path,
        encoding="cp949",
        usecols=["법정동명", "공시지가(원/㎡)"]
    ).rename(columns={"공시지가(원/㎡)": "공시지가"})
    dfs.append(df)

# 2) 5년치 연결
all_years = pd.concat(dfs, ignore_index=True)

# 3) 법정동명별 평균값 계산
result = (
    all_years
    .groupby("법정동명", as_index=False)
    .agg(평균공시지가=("공시지가", "mean"))
)

# 4) 결과 폴더 및 파일 저장
os.makedirs("final", exist_ok=True)
out_path = "final/법정동별_5년평균_공시지가.csv"
result.to_csv(out_path, index=False, encoding="utf-8-sig")

print(f"✅ {out_path} 생성 완료: {len(result)}개 법정동")

import pandas as pd


