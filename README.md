# Flight Delay & Severity Prediction with Spark MLlib

A two-stage, distributed machine learning pipeline that predicts (1) whether a US domestic
flight will be delayed and (2) how severe that delay will be, using Apache Spark MLlib at
scale across three major US hub airports.

## Overview

Most flight delay prediction work treats delay as a single classification or regression
problem and evaluates on a single airport or a small dataset. This project instead:

- Splits the problem into **two hierarchical binary classification stages**:
  - **Layer 1 — Is the flight delayed?** (on-time vs. delayed by FAA definition, >15 min)
  - **Layer 2 — How severe is the delay?** (minor: 15–45 min vs. major: >45 min)
- Benchmarks **four classifiers** at each layer: Logistic Regression, Random Forest,
  Gradient Boosted Trees, and a Stacking ensemble (LR + RF base learners with an LR
  meta-model trained on out-of-fold predictions).
- Trains and evaluates on **3.4M+ flight records** (2018–2022) from the BTS On-Time
  Performance dataset, covering **ATL, ORD, and JFK**.
- Runs the full pipeline (ingestion, cleaning, feature engineering, training, tuning,
  evaluation) on a **distributed Apache Spark cluster (Dataproc)**, with explicit
  scalability benchmarking across incremental data partitions (25% → 100%).
- Addresses **class imbalance** (5.4:1 in Layer 1) via inverse-frequency class weighting
  (LR, RF) and downsampling (GBT), and compares weighted vs. unweighted variants.

## Key Results

| Model | Layer | Accuracy | Precision | F0.5 | AUC-ROC | Train Time |
|---|---|---|---|---|---|---|
| Logistic Regression (weighted) | 1 | 0.616 | 0.768 | 0.732 | 0.653 | 7.7s |
| Random Forest (weighted) | 1 | 0.635 | 0.778 | 0.744 | 0.678 | 231.7s |
| Gradient Boosted Trees | 1 | 0.595 | 0.786 | 0.716 | **0.703** | 83.0s |
| Stacking Ensemble | 1 | **0.820** | 0.770 | **0.780** | 0.679 | 657.3s |
| Random Forest | 2 | 0.595 | 0.599 | 0.598 | 0.625 | **17.7s** |
| Gradient Boosted Trees | 2 | 0.605 | 0.606 | 0.603 | **0.656** | 52.9s |
| Stacking Ensemble | 2 | 0.593 | 0.593 | 0.593 | 0.624 | 132.6s |

**Highlights:**
- GBT achieves the best Layer 1 discriminative power (AUC-ROC 0.703); Stacking achieves
  the best precision-weighted F0.5 (0.780), making them the strongest candidates for
  operational deployment where false-positive delay predictions are costly.
- At Layer 2, performance converges across tree-based models (AUC-ROC 0.624–0.656);
  Random Forest delivers comparable accuracy at a fraction of GBT/Stacking's training
  cost, making it the most practical Layer 2 choice.
- Unweighted LR/RF models achieve deceptively high accuracy (~0.82) by predicting the
  majority "on-time" class almost exclusively — a concrete illustration of why accuracy
  is a misleading metric under class imbalance.
- Random Forest shows near-constant prediction latency across dataset sizes (0.07s–0.13s
  from 174K to 696K rows), demonstrating strong distributed inference scalability.

## Methodology

1. **Data acquisition & cleaning** — Monthly BTS On-Time Performance CSVs (2018–2022)
   loaded into Spark, filtered to ATL/ORD/JFK, cancelled/diverted flights removed, nulls
   dropped, and consolidated into partitioned Parquet for fast downstream access.
2. **EDA** — Distribution analysis of delays, temporal patterns (hour/day/month),
   airport- and carrier-level delay rates, and distance effects, used to justify feature
   choices and the 45-minute severity threshold (median delay among late flights).
3. **Feature engineering** — `StringIndexer` + `OneHotEncoder` for low-cardinality
   categoricals (carrier, destination); `FeatureHasher` for high-cardinality origin
   airport (240+ values → 64-dim hashed vector); `VectorAssembler` producing an
   89-dimensional feature vector. Post-departure delay-cause indicators excluded to
   prevent data leakage.
4. **Train/test split** — Time-based split (2019–2021 train, 2022 test) to reflect
   realistic deployment and avoid leaking future scheduling patterns.
5. **Modeling** — Four classifiers per layer, with `CrossValidator`-based hyperparameter
   tuning for Random Forest (on a stratified sample for compute efficiency), and 5-fold
   out-of-fold meta-feature generation for the Stacking ensemble.
6. **Evaluation** — AUC-ROC, weighted precision, and F0.5 (precision-weighted) as primary
   metrics, reflecting the operational cost asymmetry of false delay predictions; scalability
   measured via training/prediction time across incremental data partitions.

## Tech Stack

- **Apache Spark / Spark MLlib** (distributed data processing & ML pipelines)
- **Google Cloud Dataproc** (2-worker-node cluster)
- **PySpark**, Parquet
- **Matplotlib / Seaborn** (EDA visualizations)

## Repository Structure

```
├── notebooks/
│   ├── 01_data_ingestion_cleaning.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_logistic_regression.ipynb
│   ├── 05_random_forest.ipynb
│   ├── 06_gradient_boosted_trees.ipynb
│   └── 07_stacking_ensemble.ipynb
├── report/
│   └── flight_delay_prediction_report.pdf
├── figures/
├── requirements.txt
└── README.md
```

## Report

The full write-up — including detailed EDA, feature importance analysis, confusion
matrices, threshold sensitivity analysis, and discussion of limitations — is available in
(report.pdf).

## Authors

Group project for **ST446: Distributed Computing for Big Data**, London School of
Economics.

## Data Source

Bureau of Transportation Statistics, [On-Time Performance dataset](https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr), 2018–2022.
