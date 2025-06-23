import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import VarianceThreshold
from statsmodels.stats.outliers_influence import variance_inflation_factor

# 1) 데이터 로드 & 병합
file_info = {
    "park":   {"path": "final/세대당공원면적.csv",    "usecols": ["행정동명","세대당공원면적_log","green_ratio"], "rename": {"세대당공원면적_log": "park_area_per_hh_log"}},
    "subway": {"path": "final/행정동별_지하철밀도.csv","usecols": ["행정동명","subway_dens","subway_per_10k"]},
    "bus":    {"path": "final/행정동별_버스밀도.csv",  "usecols": ["행정동명","bus_dens","bus_per_10k"]},
    "pop":    {"path": "final/행정동별_인구밀도.csv",  "usecols": ["행정동명","pop_density"]},
    "flow":   {"path": "final/행정동별_유동인구.csv",  "usecols": ["행정동명","flow_pop"]},
    "anchor": {"path": "final/행정동별_집객시설밀도.csv","usecols": ["행정동명","anchor_fac_dens"]},
    "land":   {"path": "final/행정동명_기준_5년평균_공시지가.csv",
               "usecols": ["행정동명","평균공시지가"],
               "rename": {"평균공시지가":"land_price_log"}},
    "sales":  {"path": "final/행정동별_매출밀도.csv",
               "usecols": ["행정동명","매출_밀도"],
               "rename": {"매출_밀도":"sales_est_dens"}}
}

# 읽어와서 merge
dfs = []
for info in file_info.values():
    df = pd.read_csv(info["path"], usecols=info["usecols"], encoding="utf-8-sig")
    if "rename" in info:
        df = df.rename(columns=info["rename"])
    dfs.append(df)
df_all = dfs[0]
for df_other in dfs[1:]:
    df_all = df_all.merge(df_other, on="행정동명", how="inner")

features = [
    "park_area_per_hh_log","green_ratio","subway_dens","subway_per_10k",
    "bus_dens","bus_per_10k","pop_density","flow_pop",
    "anchor_fac_dens","land_price_log","sales_est_dens"
]

# 2) Z-score 표준화
X = StandardScaler().fit_transform(df_all[features])

# 3) 변수 간 상관관계 히트맵
plt.figure(figsize=(10,8))
corr = pd.DataFrame(X, columns=features).corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1)
plt.title("Feature Correlation Heatmap")
plt.show()

# (VIF 계산 후) VIF 데이터를 DataFrame으로 생성했다고 가정
vif_df = pd.DataFrame({
    "Feature": features,
    "VIF": [variance_inflation_factor(X, i) for i in range(len(features))]
})

# VIF Bar Chart 시각화
plt.figure(figsize=(8, 6))
vif_df_sorted = vif_df.sort_values('VIF', ascending=False)
sns.barplot(x='VIF', y='Feature', data=vif_df_sorted, palette='viridis')
plt.title('Variance Inflation Factor (VIF) by Feature')
plt.xlabel('VIF')
plt.ylabel('Feature')
plt.tight_layout()
plt.show()


# 5) PCA 로딩 막대차트 (PC1 기준)
pca = PCA(n_components=len(features)).fit(X)
loadings = pd.DataFrame(pca.components_.T,
                        index=features,
                        columns=[f"PC{i+1}" for i in range(len(features))])
plt.figure(figsize=(8,6))
loadings["PC1"].sort_values().plot(kind="barh")
plt.title("PC1 Loadings by Feature")
plt.xlabel("Loading")
plt.show()

# 6) 분산 임계치 필터링
selector = VarianceThreshold(threshold=0.5)
selector.fit(X)
var_df = pd.DataFrame({
    "Feature": features,
    "Variance_Pass": selector.get_support()
})
print("\nVariance Threshold Filter (threshold=0.5):")
print(var_df.to_string(index=False))

# --- 6-1) 원본 분산 대비 임계치 시각화 ---
# 1) 원본 변수 분산(스케일 전)
var_orig = df_all[features].var()

# 2) Bar chart
plt.figure(figsize=(10,6))
sns.barplot(
    x=var_orig.values,
    y=var_orig.index,
    palette="Blues_d"
)
plt.axvline(0.5, color='red', linestyle='--', label='Threshold = 0.5')
plt.title("Raw Feature Variances with Threshold")
plt.xlabel("Raw Variance")
plt.ylabel("Feature")
plt.legend()
plt.tight_layout()
plt.show()


# 7) 4가지 기준 중 3개 이상 만족하는 최종 변수 추출
criteria_corr = corr.abs().max() < 0.8
criteria_vif  = vif_df.set_index("Feature")["VIF"] < 10
criteria_pca  = loadings["PC1"].abs() > loadings["PC1"].abs().median()
criteria_var  = var_df.set_index("Feature")["Variance_Pass"]

final_feats = [
    f for f in features
    if sum([
        criteria_corr.loc[f],
        criteria_vif.loc[f],
        criteria_pca.loc[f],
        criteria_var.loc[f]
    ]) >= 3
]
print("\nFinal Selected Features (>=3 of 4 criteria):")
print(final_feats)
