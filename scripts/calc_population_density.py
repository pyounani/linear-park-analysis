import pandas as pd
from pathlib import Path

# ── 0. 경로 설정 ─────────────────────────────────────────────
MAP_DIR   = Path("mapping")
FINAL_DIR = Path("final")          # ← 저장 위치

AREA_PATH = MAP_DIR / "행정동면적.csv"             # 면적
POP_PATH  = MAP_DIR / "population_202505_행정동.csv"  # 인구
OUT_PATH  = FINAL_DIR / "행정동별_인구밀도.csv"     # 결과 → final/

# ── 1. 면적 로드 ─────────────────────────────────────────────
area = (
    pd.read_csv(AREA_PATH, encoding="utf-8-sig")
      .rename(columns={"행정동명": "dong", "area_km2": "area_km2"})
      .loc[:, ["dong", "area_km2"]]
)
area["area_km2"] = pd.to_numeric(area["area_km2"], errors="coerce")

# ── 2. 인구 로드 ─────────────────────────────────────────────
pop = (
    pd.read_csv(POP_PATH, encoding="utf-8-sig", thousands=",")   # 콤마 제거
      .rename(columns={"행정동": "dong",
                       "2025년05월_총인구수": "population"})
      .loc[:, ["dong", "population"]]
)
pop["population"] = pd.to_numeric(pop["population"], errors="coerce")

# ── 3. 병합 및 인구밀도 계산 ────────────────────────────────
df = area.merge(pop, on="dong", how="left")
df["pop_per_km2"] = df["population"] / df["area_km2"]

# ── 4. 저장 ────────────────────────────────────────────────
df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
print(f"저장 완료 → {OUT_PATH}")
