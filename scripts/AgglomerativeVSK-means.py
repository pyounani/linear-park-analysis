import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

# 1) 데이터 로드 & 최종 5개 피처 추출
df = pd.read_csv("output/clustered_top5_kmeans.csv", encoding="utf-8-sig")
features = ["park_area_per_hh_log","green_ratio","bus_per_10k","flow_pop","land_price_log"]
X = StandardScaler().fit_transform(df[features])

# 2) 클러스터링 모델 정의
models = {
    "KMeans(k=5)": KMeans(n_clusters=5, random_state=42),
    "DBSCAN(eps=0.5)": DBSCAN(eps=0.5, min_samples=5),
    "Agglomerative(k=5)": AgglomerativeClustering(n_clusters=5, linkage="ward")
}

# 3) 각 모델 학습 → 평가
results = []
for name, model in models.items():
    labels = model.fit_predict(X)
    # DBSCAN의 노이즈(-1) 제외 여부
    mask = labels != -1 if name.startswith("DBSCAN") else slice(None)
    sil = silhouette_score(X[mask], labels[mask]) if np.unique(labels[mask]).size>1 else np.nan
    ch  = calinski_harabasz_score(X[mask], labels[mask]) if np.unique(labels[mask]).size>1 else np.nan
    db  = davies_bouldin_score(X[mask], labels[mask]) if np.unique(labels[mask]).size>1 else np.nan
    results.append([name, sil, ch, db])

# 4) 결과 비교표
comp_df = pd.DataFrame(results, columns=["Model","Silhouette","Calinski-Harabasz","Davies-Bouldin"])
print(comp_df)

