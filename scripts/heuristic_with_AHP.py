import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from scipy.stats import entropy
from scipy.linalg import eig
from itertools import combinations
from geopy.distance import geodesic

# ────────────────────────────────────────────────
# 1. 데이터 로드 및 전처리
# ────────────────────────────────────────────────
df = pd.read_csv("output/clustered_top5_kmeans.csv", encoding="utf-8-sig")
feature_cols = [
    "park_area_per_hh_log", "green_ratio", "bus_per_10k", "flow_pop", "land_price_log"
]
X = df[feature_cols].copy()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ────────────────────────────────────────────────
# 2. 정통 AHP 가중치 계산
# ────────────────────────────────────────────────
cv = X.std() / X.mean()

def calculate_ig(col):
    p = (col - col.min()) / (col.max() - col.min())
    p = p + 1e-9
    return 1 - entropy(p, base=2) / np.log2(len(p))

ig = X.apply(calculate_ig)
importance = cv * ig

n = len(feature_cols)
matrix = np.ones((n, n))
for i in range(n):
    for j in range(n):
        matrix[i, j] = importance.iloc[i] / importance.iloc[j]  # ← 수정

eigvals, eigvecs = eig(matrix)
max_index = np.argmax(eigvals.real)
weights = eigvecs[:, max_index].real
weights = weights / np.sum(weights)
feature_z_cols = [f + "_z" for f in feature_cols]
weight_dict = dict(zip(feature_z_cols, weights))

# ────────────────────────────────────────────────
# 3. 후보지 불러오기 + 점수 계산
# ────────────────────────────────────────────────
cand_df = pd.read_csv("output/priority_top5_kmeans.csv", encoding="utf-8-sig")
candidates = cand_df["candidate"].unique().tolist()
df_all = df[df["행정동명"].isin(candidates)].copy()

# Z-score 계산 및 점수 부여
X_cand = df_all[feature_cols]
X_scaled_cand = scaler.transform(X_cand)
for idx, col in enumerate(feature_cols):
    df_all[col + "_z"] = X_scaled_cand[:, idx]
df_all["score"] = sum(df_all[col] * w for col, w in weight_dict.items())

# ────────────────────────────────────────────────
# 4. 중심좌표 + 도심지 정의
# ────────────────────────────────────────────────
centroids = pd.read_excel("mapping/adm_centroid.xlsx", engine="openpyxl")
centroids.columns = centroids.columns.str.strip()
centroids = centroids.rename(columns={"읍면동/구": "행정동명"})
df_all = df_all.merge(centroids[["행정동명", "위도", "경도"]], on="행정동명", how="left")

urban_cores = {"여의도동", "공덕동"}  # ← 더 간단하게 축소

# ────────────────────────────────────────────────
# 5. INTER 지수 계산 (임시 난수 사용)
# ────────────────────────────────────────────────
np.random.seed(42)
df_all["Ici"] = np.random.randint(100, 500, size=len(df_all))
df_all["Oci"] = np.random.randint(100, 500, size=len(df_all))
df_all["Iai"] = df_all["Ici"] + np.random.randint(50, 200, size=len(df_all))
df_all["Oai"] = df_all["Oci"] + np.random.randint(50, 200, size=len(df_all))
df_all["INTER"] = (df_all["Ici"] + df_all["Oci"]) / (df_all["Iai"] + df_all["Oai"])

# ────────────────────────────────────────────────
# 6. 후보지 3개 조합 탐색 (연결 + 외곽 포함)
# ────────────────────────────────────────────────
best_combo = None
best_score = -np.inf

for combo in combinations(df_all.itertuples(index=False), 3):
    names = [c.행정동명 for c in combo]
    coords = [(c.위도, c.경도) for c in combo]
    inters = [c.INTER for c in combo]
    outer_flags = [name not in urban_cores for name in names]

    connected = all(
        geodesic(coords[i], coords[j]).km <= 5  # ← 3km → 5km 완화
        for i in range(3) for j in range(i + 1, 3)
    )
    has_outer = any(outer_flags)

    if connected and has_outer:
        score = sum(inters)
        if score > best_score:
            best_score = score
            best_combo = names

# ────────────────────────────────────────────────
# 7. 최종 출력
# ────────────────────────────────────────────────
print("▶ 최적 후보지 3곳:", best_combo)
print("▶ INTER 총합:", round(best_score, 4))


