"""
park_area_update.py
────────────────────────────────────────────────────────────────────
① 세대당공원면적 CSV(park_area.csv) 로드
② KIKmix.xlsx에서 말소되지 않은 최신 행정동 코드·명 추출
③ 코드가 존재하는 행은 최신 행정동명으로 자동 교체
④ 코드가 사라진(폐지·분동) 행은 manual_map 또는 fuzzy 검색으로 대체
   - manual_map에 없고 후보가 2개 이상이면 로그로 알려줌
⑤ ‘행정동명 (행정동코드)’ 형태의 새 컬럼 추가
⑥ 결과를 processed/세대당공원면적_최신동명.csv 로 저장
────────────────────────────────────────────────────────────────────
필요 시
    ▸ manual_map에 폐지‧분동 동 추가
    ▸ encoding 경로·파일명 수정
"""

import pandas as pd
import numpy as np
import re
import os

# ───────── 0. 경로 ─────────
PARK_PATH = "processed/park_area.csv"
KIK_PATH = "mapping/KIKmix.xlsx"
OUT_PATH = "processed/세대당공원면적_최신동명.csv"

# ───────── 1. 세대당공원면적 ─────────
park_df = pd.read_csv(
    PARK_PATH,
    dtype={"행정동코드": str, "행정동명": str, "세대당공원면적": float},
    encoding="utf-8-sig"
)
park_df["행정동코드"] = (
    pd.to_numeric(park_df["행정동코드"], errors="coerce")
    .astype("Int64")
    .astype(str)
    .str.zfill(10)
)
park_df["세대당공원면적"].replace(0, np.nan, inplace=True)
park_df["세대당공원면적"].fillna(park_df["세대당공원면적"].median(), inplace=True)

# ───────── 2. KIKmix: 살아 있는 최신 행만 ─────────
kik = pd.read_excel(KIK_PATH, dtype=str)
kik["행정동코드"] = kik["행정동코드"].str.zfill(10)
alive = kik["말소일자"].isna() | (kik["말소일자"] == "0")
kik = kik[alive].copy()
kik["생성일자"] = pd.to_numeric(kik["생성일자"], errors="coerce").fillna(0).astype(int)
kik_latest = (
    kik.sort_values(["행정동코드", "생성일자"])
    .drop_duplicates("행정동코드", keep="last")
    .rename(columns={"읍면동명": "최신행정동명"})
    [["행정동코드", "최신행정동명"]]
)

# ───────── 3. 코드 존재 행 자동 치환 ─────────
park_df = park_df.merge(kik_latest, on="행정동코드", how="left")
auto_mask = park_df["최신행정동명"].notna() & (
    park_df["행정동명"] != park_df["최신행정동명"]
)
park_df.loc[auto_mask, "행정동명"] = park_df.loc[auto_mask, "최신행정동명"]
park_df.drop(columns=["최신행정동명"], inplace=True)
print(f"코드 동일 · 이름 변경: {auto_mask.sum()}건")

# ───────── 4. 코드 누락 행 처리 ─────────
missing = ~park_df["행정동코드"].isin(kik_latest["행정동코드"])
missing_rows = park_df[missing].copy()
print(f"KIKmix에 코드 없는 행: {len(missing_rows)}건")

# 수동 매핑 dict
manual_map = {
    "일원2동": ("1168068000", "개포3동"),
    "상일동": ("1174052500", "상일제1동"),
}

def base_name(name: str) -> str:
    """‘본·제숫자동’ 접미사를 제거한 기본 이름 반환"""
    return re.sub(r"(본|제?\d+)?동$", "", name)

for idx, row in missing_rows.iterrows():
    old_name = row["행정동명"]

    # 4-1) manual_map 우선 적용
    if old_name in manual_map:
        new_code, new_name = manual_map[old_name]
        park_df.loc[idx, ["행정동코드", "행정동명"]] = [new_code, new_name]
        print(f"수동 치환: {old_name} → {new_name}")
        continue

    # 4-2) fuzzy 검색
    base = base_name(old_name)
    cand = kik_latest[kik_latest["최신행정동명"].str.contains(base)]
    if len(cand) == 1:
        new_code = cand.iloc[0]["행정동코드"]
        new_name = cand.iloc[0]["최신행정동명"]
        park_df.loc[idx, ["행정동코드", "행정동명"]] = [new_code, new_name]
        print(f"자동 치환: {old_name} → {new_name}")
    else:
        print(f"후보 {len(cand)}개: {old_name} → {list(cand['최신행정동명'])}  ▶ manual_map 추가 필요")

# ───────── 5. 행정동명+코드 컬럼 추가 ─────────
park_df["행정동명_코드"] = park_df["행정동명"] + " (" + park_df["행정동코드"] + ")"
park_df = park_df[
    ["행정동코드", "행정동명", "행정동명_코드", "세대당공원면적"]
]

# ───────── 6. 저장 ─────────
os.makedirs("processed", exist_ok=True)
park_df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
print(f"완료: '{OUT_PATH}'")
