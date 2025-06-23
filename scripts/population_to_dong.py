import pandas as pd

FILE_IN  = "raw/population_202505.csv"        # 원본 파일
FILE_OUT = "mapping/population_202505_행정동.csv"   # 결과 파일

# ── 1. CSV 불러오기 ───────────────────────────────────────────
df = pd.read_csv(FILE_IN, encoding="cp949")   # ↖ 인코딩 확인

# ── 2. (코드) 제거 + 마지막에 ‘동’으로 끝나는 토큰만 추출 ─────────
#  2-1) 괄호와 숫자 코드 삭제 → 공백 기준 분할
clean = (df['행정구역']                         # 원본 열
         .str.replace(r'\s*\([^)]+\)', '', regex=True)  # (1111051500) 없애기
         .str.strip()
         .str.split()                           # 공백 단위 분할
         .str[-1])                              # 마지막 토큰만

#  2-2) ‘동’으로 끝나는 행만 남기기
df['행정동'] = clean
df_dong      = df[df['행정동'].str.endswith('동')].copy()

# ── 3. 필요 열만 남기고 저장 ────────────────────────────────────
#   ▸ 총인구수 열이 있다면 함께 남기고, 없으면 행정동만 남겨도 OK
cols_to_keep = ['행정동']
# 예: 인구 열이 '2025년05월_총인구수' 라면 함께 추가
for c in df.columns:
    if '총인구' in c:
        cols_to_keep.append(c)

out = df_dong[cols_to_keep].reset_index(drop=True)
out.to_csv(FILE_OUT, index=False, encoding="utf-8-sig")

print(out.head())

