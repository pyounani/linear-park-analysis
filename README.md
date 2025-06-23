# Data-Driven Selection of Optimal Sites for Linear Parks in Seoul

This project identifies the most suitable districts in Seoul for linear park development using spatial and statistical analysis.

You can access both the presentation slides and the full report below.

---

## 📂 Project Files

### 🎥 Presentation Materials

- 📄 [View the final presentation (PDF)](./presentation/빅데이터_발표자료.pdf)

### 📝 Full Report

- 📘 [Download the full data analysis report (PDF)](./report/Detailed_Big_Data_Report.pdf)

---

By **Youna Park**

## 📚 Table of Contents

- [📌 Overview](#-overview)
- [🎯 Objective](#-objective)
- [🛠️ Methodology](#-methodology)
  - [1. Data Collection & Preprocessing](#1-data-collection--preprocessing)
  - [2. Clustering Analysis](#2-clustering-analysis)
  - [3. AHP-based Scoring (Qx)](#3-ahp-based-scoring-qx)
  - [4. Spatial Optimization with INTER Index](#4-spatial-optimization-with-inter-index)
- [✅ Final Recommendations](#-final-recommendations)
- [🧠 Key Insights](#-key-insights)

---

## 📌 Overview

Seoul is facing intensifying heatwaves and a shortage of accessible green space in urban areas. Due to high land use saturation, traditional park development is no longer feasible in many regions.  
This project aims to scientifically identify the **optimal administrative districts for linear parks** by analyzing multiple spatial, demographic, and economic factors.

---

## 🎯 Objective

To recommend areas where linear parks would be most impactful, based on:

- Green space deficiency
- Accessibility (public transportation)
- Local demand (floating and residential population)
- Land availability and cost

---

## 🛠️ Methodology

### 1. Data Collection & Preprocessing

- Merged 10+ public datasets (land price, park size, subway/bus stops, population, facility density, etc.)
- Performed spatial joins and normalization (log, z-score)

### 2. Clustering Analysis

- Selected final features using correlation, PCA loading, VIF, and variance threshold
- Applied K-Means clustering (k=5) → Selected **10 candidate districts**

### 3. AHP-based Scoring (Q(x))

- Weights derived from Coefficient of Variation × Information Gain
- Aggregated standardized feature values into a single score per district

### 4. Spatial Optimization with INTER Index

- Measured interaction (traffic flows) between candidate and central areas
- Applied heuristic rules (distance ≤ 5km, minimum outer area, connected clusters)
- Selected **3 final optimal combinations**

---

## ✅ Final Recommendations

| District          | Key Characteristics                              |
| ----------------- | ------------------------------------------------ |
| **Seokgwan-dong** | High residential density, low green space ratio  |
| **Jongam-dong**   | High floating population, strong transport links |
| **Jegi-dong**     | Adjacent to river, low land cost                 |

---

## 🧠 Key Insights

- Integrated multiple perspectives: **urban, environmental, socioeconomic**
- Combined **quantitative scoring (Q(x))** with **spatial logic (INTER)** for final decision
- Proposed replicable, data-driven model for green infrastructure expansion

---
