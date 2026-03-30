# Telecom Churn Sentiment Analysis (Reproducibility)

This repository contains a single, commented Python script used to reproduce the assignment analysis workflow.

## File

- `analysis.py`: end-to-end script that
  - loads `telecom_churn_sentiment.csv`
  - generates sentiment distribution tables/charts
  - generates negative-sentiment breakdowns by `Gender` and `TechSupport`
  - compares multiple text-driven churn models (5-fold CV where applicable)
  - writes output artifacts under `tables/` and `figures/`

## How to run

1. Place `telecom_churn_sentiment.csv` in the same folder as `analysis.py`.
2. Run:

```bash
python3 analysis.py
```

## Output artifacts

- `tables/sentiment_distribution.csv`
- `tables/negative_by_gender.csv`
- `tables/negative_by_techsupport.csv`
- `tables/model_test_score.csv`
- `tables/model_comparison.csv`
- `figures/sentiment_distribution.svg`
- `figures/negative_by_gender.svg`
- `figures/negative_by_techsupport.svg`
- `figures/confusion_matrix.svg`
- `figures/model_metric_comparison.svg`

## Notes

- The script uses only Python standard library modules for portability.
- The dataset file is not included in this repository.
