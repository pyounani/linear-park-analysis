import pandas as pd
from pathlib import Path

# ── 0. 경로 설정 ──────────────────────────────────────────────
ROOT_MAP  = Path("mapping")
ROOT_FIN  = Path("final")

POP_PATH  = ROOT_MAP / "population_202505_행정동.csv"      # ① 인구수
SUB_PATH  = ROOT_FIN / "행정동별_지하철밀도.csv"           # ② 지하철·면적
OUT_PATH  = ROOT_FIN / "행정동별_지하철밀도.csv"           # 덮어쓰기

# ── 1. 인구수 로드 ────────────────────────────────────────────
pop = (
    pd.read_csv(POP_PATH, encoding="utf-8-sig", thousands=",")  # ← 콤마 제거
      .rename(columns={"행정동": "dong",
                       "2025년05월_총인구수": "population"})
      .loc[:, ["dong", "population"]]
)

# population이 누락되면 NaN → 0 처리(원하면 dropna로 제거)
pop["population"] = pop["population"].fillna(0).astype(int)

# ── 2. 지하철·면적 로드 ───────────────────────────────────────
sub = (
    pd.read_csv(SUB_PATH, encoding="utf-8-sig")
      .rename(columns={"행정동명": "dong"})
)

# subway_cnt가 문자열이라면 숫자로 변환
sub["subway_cnt"] = pd.to_numeric(sub["subway_cnt"], errors="coerce").fillna(0).astype(int)

# ── 3. 병합 ──────────────────────────────────────────────────
df = sub.merge(pop, on="dong", how="left")

# ── 4. subway_per_10k 계산 ──────────────────────────────────
df["subway_per_10k"] = df["subway_cnt"] / (df["population"] / 10_000)

# ── 5. 저장 ─────────────────────────────────────────────────
df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
print(f"저장 완료 → {OUT_PATH}")
