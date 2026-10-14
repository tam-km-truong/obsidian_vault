---
category: knowledge
tags:
  - mlflow
  - python
  - experiment-tracking
source_raw: "[[MLflow]]"
status: processed
---

# MLflow: Experiment Tracking Cheatsheet

## Core Concepts
- **Run:** A single execution of machine learning or benchmark code.
- **Experiment:** A collection of runs comparing models or parameter sweeps.

```python
import mlflow

with mlflow.start_run(run_name="compression_benchmark_01"):
    mlflow.log_param("kmer_size", 31)
    mlflow.log_param("compressor", "agc")
    mlflow.log_metric("compression_ratio", 24.5)
    mlflow.log_artifact("results/tree.nwk")
```

## Related Notes
- [[Backpressure, Concurrency & Memory Management in Python]]
