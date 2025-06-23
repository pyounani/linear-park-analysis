import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 비교할 지표 값 입력
metrics = {
    'Algorithm': ['KMeans', 'HDBSCAN'],
    'Silhouette': [0.931, 0.999],
    'Calinski_Harabasz': [10160.1, 49304.1],
    'Davies_Bouldin': [0.357, 0.100]
}
df = pd.DataFrame(metrics)

# 1) Silhouette Score 비교
plt.figure(figsize=(6,4))
sns.barplot(x='Algorithm', y='Silhouette', data=df, palette='pastel')
plt.ylim(0, 1.1)
plt.title('Silhouette Score Comparison')
plt.ylabel('Silhouette Score')
plt.tight_layout()
plt.show()

# 2) Calinski-Harabasz Index 비교
plt.figure(figsize=(6,4))
sns.barplot(x='Algorithm', y='Calinski_Harabasz', data=df, palette='pastel')
plt.title('Calinski–Harabasz Index Comparison')
plt.ylabel('Calinski–Harabasz Index')
plt.tight_layout()
plt.show()

# 3) Davies–Bouldin Index 비교
plt.figure(figsize=(6,4))
sns.barplot(x='Algorithm', y='Davies_Bouldin', data=df, palette='pastel')
plt.title('Davies–Bouldin Index Comparison')
plt.ylabel('Davies–Bouldin Index')
plt.tight_layout()
plt.show()
