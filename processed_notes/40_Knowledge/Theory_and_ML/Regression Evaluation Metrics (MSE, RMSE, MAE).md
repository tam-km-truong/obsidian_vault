---
category: knowledge
tags:
  - statistics
  - machine-learning
  - regression
  - metrics
source_raw: "[[Mean Squared Error (MSE) and Similar Techniques]]"
status: processed
---

# Regression Evaluation Metrics: MSE, RMSE, MAE, and Huber Loss

## Summary Table of Metrics
| Metric | Formula | Sensitivity to Outliers | Interpretation |
| :--- | :--- | :--- | :--- |
| **MSE** | $\frac{1}{n} \sum (y_i - \hat{y}_i)^2$ | High (quadratic penalty) | Penalizes large errors heavily |
| **RMSE** | $\sqrt{\text{MSE}}$ | High | In same units as target $y$ |
| **MAE** | $\frac{1}{n} \sum \|y_i - \hat{y}_i\|$ | Low (linear penalty) | Robust to extreme outliers |
| **Huber Loss** | Quadratic for $|e| \le \delta$, linear otherwise | Tunable via $\delta$ | Best of MSE and MAE |

## Related Notes
- [[Neural Inference for Evolutionary Genomics]]
- [[Feature Selection in High-Dimensional Genomics]]
