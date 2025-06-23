# add_green_ratio.py
# ------------------
# ① 세대당공원면적   ② 행정동세대수   ③ 행정동면적  →  녹지율 계산
# 결과: processed/세대당공원면적_with_green.csv

import pandas as pd
import numpy as np
from pathlib import Path

# ────── 0. 경로 ─────────────────────────────
ROOT = Path.cwd()                 # 프로젝트 루트
PARK  = ROOT / "final" / "세대당공원면적_최신동명.csv"
HH    = ROOT / "processed" / "행정동세대수_202505.csv"
AREA  = ROOT / "mapping"   / "행정동면적.csv"
OUT   = ROOT / "processed" / "세대당공원면적_with_green.csv"

# ────── 1. 로드 (adm_cd 반드시 str) ─────────
park = pd.read_csv(PARK, dtype={"행정동코드": str})\
        .rename(columns={"행정동코드":"adm_cd"})

hh   = pd.read_csv(HH,   dtype={"adm_cd": str})
area = pd.read_csv(AREA, dtype={"area_km2": float})

# ────── 2. 머지 ────────────────────────────
df = (park
      .merge(hh[["adm_cd", "household_cnt"]], on="adm_cd", how="left")
      .merge(area[["행정동명", "area_km2"]],   on="행정동명", how="left"))

# ────── 3. 파생 변수 ───────────────────────
# 총 공원 면적(㎡)
df["park_area_total"] = df["세대당공원면적"] * df["household_cnt"]

# 행정동 면적 ㎢ → ㎡
df["area_m2"] = df["area_km2"] * 1_000_000

# 녹지율(%) = 총 공원 면적 ÷ 행정동 면적 × 100
df["green_ratio"] = (df["park_area_total"] / df["area_m2"]) * 100

# ────── 4. 컬럼 순서 재배치 ────────────────
base_cols = ["adm_cd", "행정동명",
             "세대당공원면적", "세대당공원면적_log"]
new_cols  = ["park_area_total", "green_ratio"]

df = df[base_cols + new_cols +
        [c for c in df.columns if c not in (base_cols + new_cols)]]

# ────── 5. 저장 ───────────────────────────
OUT.parent.mkdir(exist_ok=True)
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"✅ 녹지율 추가 완료 → {OUT.relative_to(ROOT)}")
