# ──────────────────────────────────────────────────────────────
# add_log_to_park_area.py   (또는: 세대당공원면적_로그변환.py)
#
# 1. final/세대당공원면적_최신동명.csv 로부터 데이터를 읽어온다.
# 2. 세대당공원면적(㎡/세대)에 log1p 변환값(세대당공원면적_log)을 추가한다.
#    - np.log1p(x)  ↔  log(1 + x)  : 0 값도 안전하게 변환.
# 3. 원본과 로그값의 왜도(skewness)를 출력하여 분포 변화를 확인한다.
# 4. 같은 경로·파일명으로 덮어쓰기(backup 필요 시 별도 저장).
#
# 사용 방법
#   $ python add_log_to_park_area.py
# ──────────────────────────────────────────────────────────────

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import skew

# 한글 깨짐·음수 기호 세팅
plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

PARK_PATH = "final/세대당공원면적_최신동명.csv"

# 1) 파일 로드
df = pd.read_csv(PARK_PATH, encoding="utf-8-sig")

# 2) 로그 변환 컬럼 추가
df["세대당공원면적_log"] = np.log1p(df["세대당공원면적"])

# 3) 분포·왜도 확인
print("원본 왜도 :", round(skew(df["세대당공원면적"]), 2))
print("로그 왜도  :", round(skew(df["세대당공원면적_log"]), 2))

# (선택) 히스토그램 확인
# plt.hist(df["세대당공원면적"], bins=30); plt.title("원본 분포"); plt.show()
# plt.hist(df["세대당공원면적_log"], bins=30); plt.title("로그 변환 분포"); plt.show()

# 4) 덮어쓰기 저장
df.to_csv(PARK_PATH, index=False, encoding="utf-8-sig")
print(f"✅ '{PARK_PATH}'에 로그 컬럼이 추가되어 저장되었습니다.")
