import os
os.environ["OMP_NUM_THREADS"] = "1"

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import contextily as ctx

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import (
    silhouette_score, calinski_harabasz_score, davies_bouldin_score
)

# ─── 1) 데이터 로드 & 병합 ─────────────────────────────────────────────
file_info = {
    "park": {
        "path": "final/세대당공원면적.csv",
        "usecols": ["행정동명","세대당공원면적_log","green_ratio"],
        "rename": {"세대당공원면적_log":"park_area_per_hh_log"}
    },
    "bus": {
        "path": "final/행정동별_버스밀도.csv",
        "usecols": ["행정동명","bus_per_10k"]
    },
    "flow": {
        "path": "final/행정동별_유동인구.csv",
        "usecols": ["행정동명","flow_pop"]
    },
    "land": {
        "path": "final/행정동명_기준_5년평균_공시지가.csv",
        "usecols": ["행정동명","평균공시지가"],
        "rename": {"평균공시지가":"land_price_log"}
    }
}

dfs = []
for info in file_info.values():
    tmp = pd.read_csv(info["path"], usecols=info["usecols"], encoding="utf-8-sig")
    if "rename" in info:
        tmp = tmp.rename(columns=info["rename"])
    dfs.append(tmp)

df = dfs[0]
for other in dfs[1:]:
    df = df.merge(other, on="행정동명", how="inner")

# ─── 2) 최종 5개 피처 선택 & 표준화 ────────────────────────────────────
features = [
    "park_area_per_hh_log",
    "green_ratio",
    "bus_per_10k",
    "flow_pop",
    "land_price_log"
]
X = df[features].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ─── 3) Agglomerative Clustering & 평가 ───────────────────────────────
agg = AgglomerativeClustering(n_clusters=5, linkage="ward")
labels_agg = agg.fit_predict(X_scaled)
df["cluster_agg"] = labels_agg

sil = silhouette_score(X_scaled, labels_agg)
ch  = calinski_harabasz_score(X_scaled, labels_agg)
db  = davies_bouldin_score(X_scaled, labels_agg)
print(f"Agglomerative Silhouette: {sil:.3f}")
print(f"Agglomerative Calinski-Harabasz: {ch:.1f}")
print(f"Agglomerative Davies-Bouldin: {db:.3f}")

# ─── 4) PCA 2D 시각화 ────────────────────────────────────────────────
vis = PCA(n_components=2, random_state=42).fit_transform(X_scaled)
plt.figure(figsize=(8,6))
sns.scatterplot(x=vis[:,0], y=vis[:,1],
                hue=df["cluster_agg"], palette="tab10",
                s=40, alpha=0.7)
plt.title("Agglomerative Clusters (Top 5 Features)")
plt.xlabel("PC1"); plt.ylabel("PC2")
plt.legend(title="Cluster")
plt.tight_layout()
plt.show()

# ─── 5) 후보 행정동 추출 ───────────────────────────────────────────────
# park_area_per_hh_log 평균이 가장 낮은 클러스터
means = df.groupby("cluster_agg")["park_area_per_hh_log"].mean()
low_cluster = means.idxmin()
candidates = df[df["cluster_agg"] == low_cluster]["행정동명"].unique().tolist()
print("▶ Agglomerative 후보 행정동:", candidates)

# ─── 6) 지도 시각화 ────────────────────────────────────────────────
# 6-1) 중심좌표 로드
cent = pd.read_excel("mapping/adm_centroid.xlsx", engine="openpyxl")
cent.columns = cent.columns.str.strip()
cent = cent.rename(columns={"읍면동/구":"행정동명"})
cent = cent[["행정동명","위도","경도"]]

# 6-2) 후보 좌표만 필터
cent_cand = cent[cent["행정동명"].isin(candidates)].drop_duplicates()

# 6-3) GeoDataFrame 생성 & CRS 변환
gpoints = gpd.GeoDataFrame(
    cent_cand,
    geometry=gpd.points_from_xy(cent_cand["경도"], cent_cand["위도"]),
    crs="EPSG:4326"
).to_crs(epsg=3857)

# 6-4) 지도 그리기
fig, ax = plt.subplots(figsize=(8,8))
gpoints.plot(ax=ax, color="red", markersize=100, alpha=0.8, edgecolor="k", label="Candidate")
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gpoints.crs)

for x, y, name in zip(gpoints.geometry.x, gpoints.geometry.y, gpoints["행정동명"]):
    ax.text(x, y, name, ha="center", va="center",
            fontsize=9, bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.6))

ax.set_title("Agglomerative Clustering 최종 후보 행정동", fontsize=14)
ax.axis("off")
plt.legend()
plt.tight_layout()
plt.show()
