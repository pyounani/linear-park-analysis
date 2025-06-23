import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import contextily as ctx

from sklearn.preprocessing import StandardScaler

# 1) 저장해둔 전체 데이터 로드
df_all = pd.read_csv("output/clustered_top5_kmeans.csv", encoding="utf-8-sig")

# 2) 최종 5개 피처와 스케일러 불러오기 & 표준화
feature_cols = [
    "park_area_per_hh_log",
    "green_ratio",
    "bus_per_10k",
    "flow_pop",
    "land_price_log"
]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_all[feature_cols].values)
df_scaled = pd.DataFrame(X_scaled, columns=[f + "_z" for f in feature_cols])
df_all = pd.concat([df_all, df_scaled], axis=1)

# 3) 후보 행정동 필터링
cand_df = pd.read_csv("output/priority_top5_kmeans.csv", encoding="utf-8-sig")
candidates = cand_df["candidate"].unique().tolist()
df_cand = df_all[df_all["행정동명"].isin(candidates)].copy()

# 4) 가중치 정의 (예시)
# park_area_per_hh_log은 작을수록 우선 → 음수 가중치
w = {
    "park_area_per_hh_log_z": -1.0,
    "green_ratio_z":         -0.8,
    "bus_per_10k_z":          0.6,
    "flow_pop_z":             0.7,
    "land_price_log_z":      -1.2
}

# 5) Score 계산
df_cand["score"] = sum(
    df_cand[col] * weight for col, weight in w.items()
)

# 6) 최적 지역 추출
df_cand = df_cand.sort_values("score")
best = df_cand.iloc[0]
print("▶ 최적 위치:", best["행정동명"])
print(best[["score"] + feature_cols])

# 7) 최적 위치 지도 시각화 (중심좌표 엑셀 활용)
# 7-1) 중심좌표 읽기
centroids = pd.read_excel("mapping/adm_centroid.xlsx", engine="openpyxl")
centroids.columns = centroids.columns.str.strip()
centroids = centroids.rename(columns={"읍면동/구":"행정동명"})
centroids = centroids[["행정동명","위도","경도"]]

# 7-2) GeoDataFrame 생성 & 후보 전체 + 최적 강조
cent_cand = centroids[centroids["행정동명"].isin(candidates)].drop_duplicates()
gpoints = gpd.GeoDataFrame(
    cent_cand,
    geometry=gpd.points_from_xy(cent_cand["경도"], cent_cand["위도"]),
    crs="EPSG:4326"
).to_crs(epsg=3857)

fig, ax = plt.subplots(figsize=(8,8))
# 모든 후보지는 연회색
gpoints.plot(ax=ax, color="lightgray", markersize=80, alpha=0.6)
# 최적 위치만 빨간색
best_point = gpoints[gpoints["행정동명"] == best["행정동명"]]
best_point.plot(ax=ax, color="red", markersize=150, edgecolor="k", label="Best")

# OSM 배경
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gpoints.crs)

# 레이블
for x, y, name in zip(best_point.geometry.x, best_point.geometry.y, best_point["행정동명"]):
    ax.text(x, y, name, ha="center", va="center",
            fontsize=12, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))

ax.set_title("최적 위치 선정: {}".format(best["행정동명"]), fontsize=16)
ax.axis("off")
plt.legend()
plt.tight_layout()
plt.show()
