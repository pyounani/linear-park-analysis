import pandas as pd
from pathlib import Path

# ── 0. 경로 설정 ──────────────────────────────────────────────
ROOT_MAP  = Path("mapping")
ROOT_FIN  = Path("final")

POP_PATH  = ROOT_MAP / "population_202505_행정동.csv"      # ① 인구수
BUS_PATH  = ROOT_FIN / "행정동별_버스밀도.csv"             # ② 버스·면적
OUT_PATH  = ROOT_FIN / "행정동별_버스밀도.csv"             # 덮어쓰기

# ── 1. 인구수 로드 ────────────────────────────────────────────
pop = (
    pd.read_csv(POP_PATH, encoding="utf-8-sig", thousands=",")  # 콤마 제거
      .rename(columns={"행정동": "dong",
                       "2025년05월_총인구수": "population"})
      .loc[:, ["dong", "population"]]
)
pop["population"] = pop["population"].fillna(0).astype(int)

# ── 2. 버스·면적 로드 ────────────────────────────────────────
bus = (
    pd.read_csv(BUS_PATH, encoding="utf-8-sig")
      .rename(columns={"행정동명": "dong"})
)
bus["bus_cnt"] = pd.to_numeric(bus["bus_cnt"], errors="coerce").fillna(0).astype(int)

# ── 3. 병합 ──────────────────────────────────────────────────
df = bus.merge(pop, on="dong", how="left")

# ── 4. bus_per_10k 계산 ─────────────────────────────────────
df["bus_per_10k"] = df["bus_cnt"] / (df["population"] / 10_000)

# ── 5. 저장 ─────────────────────────────────────────────────
df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
print(f"저장 완료 → {OUT_PATH}")
