import os
os.environ["OMP_NUM_THREADS"] = "1"  # Windows + MKL 메모리 누수 우회

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples

# 1) 데이터 로드 & 병합
file_info = {
    "park":   {
        "path": "final/세대당공원면적.csv",
        "usecols": ["행정동명","세대당공원면적_log","green_ratio"],
        "rename": {"세대당공원면적_log":"park_area_per_hh_log"}
    },
    "bus":    {
        "path": "final/행정동별_버스밀도.csv",
        "usecols": ["행정동명","bus_per_10k"]
    },
    "flow":   {
        "path": "final/행정동별_유동인구.csv",
        "usecols": ["행정동명","flow_pop"]
    },
    "land":   {
        "path": "final/행정동명_기준_5년평균_공시지가.csv",
        "usecols": ["행정동명","평균공시지가"],
        "rename": {"평균공시지가":"land_price_log"}
    }
}

dfs = []
for info in file_info.values():
    df_tmp = pd.read_csv(info["path"],
                         usecols=info["usecols"],
                         encoding="utf-8-sig")
    if "rename" in info:
        df_tmp = df_tmp.rename(columns=info["rename"])
    dfs.append(df_tmp)

df = dfs[0]
for df_other in dfs[1:]:
    df = df.merge(df_other, on="행정동명", how="inner")

# 2) 최종 5개 피처 선택
final_feats = [
    "park_area_per_hh_log",
    "green_ratio",
    "bus_per_10k",
    "flow_pop",
    "land_price_log"
]
X = df[final_feats].values

# 3) Z-score 표준화
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4) Elbow Plot (관성)
inertias = []
K_range = range(2, 11)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42).fit(X_scaled)
    inertias.append(km.inertia_)

plt.figure(figsize=(6,4))
plt.plot(list(K_range), inertias, '-o')
plt.axvline(5, color='red', linestyle='--', label='Elbow k=5')
plt.title("Elbow Plot (Inertia vs K)")
plt.xlabel("n_clusters")
plt.ylabel("Inertia")
plt.legend()
plt.tight_layout()
plt.show()

# 5) Silhouette Score vs K
sil_scores = []
for k in K_range:
    labels = KMeans(n_clusters=k, random_state=42).fit_predict(X_scaled)
    sil_scores.append(silhouette_score(X_scaled, labels))

plt.figure(figsize=(6,4))
plt.plot(list(K_range), sil_scores, '-o')
plt.axvline(5, color='red', linestyle='--', label='Best k≈5')
plt.title("Silhouette Score vs K")
plt.xlabel("n_clusters")
plt.ylabel("Silhouette Score")
plt.legend()
plt.tight_layout()
plt.show()

# 6) 최적 k로 K-Means 실행
best_k = 5
kmeans = KMeans(n_clusters=best_k, random_state=42)
df["km"] = kmeans.fit_predict(X_scaled)

# 7) 클러스터별 park_area_per_hh_log 평균 확인 & 후보 클러스터 지정
km_means = df.groupby("km")["park_area_per_hh_log"].mean()
low_km = km_means.idxmin()
candidates = df[df["km"] == low_km]["행정동명"].tolist()
print("▶ 최종 후보 행정동 (cluster_km == {}):".format(low_km), candidates)

# 8) 결과 저장
df.to_csv("output/clustered_top5_kmeans.csv",
          index=False, encoding="utf-8-sig")
pd.Series(candidates, name="candidate") \
  .to_csv("output/priority_top5_kmeans.csv",
          index=False, encoding="utf-8-sig")

# 9) PCA 2D 산점도 (전체 + 후보 하이라이트)
pca2 = PCA(n_components=2, random_state=42)
vis = pca2.fit_transform(X_scaled)

plt.figure(figsize=(8,6))
# 전체 점은 연회색
plt.scatter(vis[:,0], vis[:,1], c='lightgray', s=30, alpha=0.6, label='Other')
# 후보만 파란색
mask = df["km"] == low_km
plt.scatter(vis[mask,0], vis[mask,1],
            c='C0', s=80, edgecolor='k', label='Candidates')
for x,y,name in zip(vis[mask,0], vis[mask,1], df.loc[mask,"행정동명"]):
    plt.text(x+0.1, y+0.1, name, fontsize=8)
plt.title("PCA 2D (K-Means Candidates)")
plt.xlabel("PC1"); plt.ylabel("PC2")
plt.legend()
plt.tight_layout()
plt.show()

# 10) Silhouette Plot for k-means
labels = df["km"].values
sil_vals = silhouette_samples(X_scaled, labels)
n_clusters = best_k
y_lower = 10

plt.figure(figsize=(8,6))
for i in range(n_clusters):
    vals = sil_vals[labels == i]
    vals.sort()
    y_upper = y_lower + len(vals)
    plt.fill_betweenx(np.arange(y_lower, y_upper), 0, vals, alpha=0.7)
    plt.text(-0.02, y_lower + 0.5*len(vals), str(i))
    y_lower = y_upper + 10

plt.axvline(np.mean(sil_vals), color="red", linestyle="--")
plt.title("Silhouette Plot (K-Means, k={})".format(best_k))
plt.xlabel("Silhouette Coefficient")
plt.ylabel("Cluster")
plt.yticks([])
plt.tight_layout()
plt.show()


##########시각화
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# 1) 후보 행정동명 리스트 로드
cand_df = pd.read_csv("output/priority_top5_kmeans.csv", encoding="utf-8-sig")
candidates = cand_df["candidate"].tolist()

# 2) 중심좌표 엑셀 로드
centroids = pd.read_excel("mapping/adm_centroid.xlsx", engine="openpyxl")
# 컬럼 공백 제거
centroids.columns = centroids.columns.str.strip()
# '읍면동/구' 컬럼을 행정동명으로 통일
centroids = centroids.rename(columns={"읍면동/구":"행정동명"})
# 필요한 컬럼만
centroids = centroids[["행정동명","위도","경도"]]

# 3) 후보 행정동만 필터링
cent_cand = centroids[centroids["행정동명"].isin(candidates)].drop_duplicates()

# 4) GeoDataFrame 생성 (WGS84)
gpoints = gpd.GeoDataFrame(
    cent_cand,
    geometry=gpd.points_from_xy(cent_cand["경도"], cent_cand["위도"]),
    crs="EPSG:4326"
)

# 5) Web Mercator (EPSG:3857)으로 변환
gpoints = gpoints.to_crs(epsg=3857)

# 6) 지도 그리기
fig, ax = plt.subplots(figsize=(8,8))

# 후보지 포인트 찍기
gpoints.plot(
    ax=ax,
    color="red",
    markersize=100,
    alpha=0.8,
    edgecolor="k",
    label="Candidate"
)

# OSM 배경 타일 추가
ctx.add_basemap(
    ax,
    source=ctx.providers.OpenStreetMap.Mapnik,
    crs=gpoints.crs
)

# 7) 레이블 추가
for x, y, name in zip(gpoints.geometry.x, gpoints.geometry.y, gpoints["행정동명"]):
    ax.text(
        x, y, name,
        ha="center", va="center",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.6)
    )

# 8) 최종 옵션
ax.set_title("K-Means 최종 후보 행정동 (Centroid 기반)", fontsize=14)
ax.axis("off")
plt.legend()
plt.tight_layout()
plt.show()
