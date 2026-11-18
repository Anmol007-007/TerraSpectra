# TerraSpectra Experiment Tracking Log

Structured log tracking model architecture variants, imbalance treatments, loss functions, learning rate schedules, and spatial evaluation metrics.

| Run ID | Date | Architecture | Loss | Imbalance Treatment | Epochs | Macro-F1 | Accuracy | mIoU | Checkpoint | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| `run_baseline_01` | 2026-11-18 | CNN3D v1 | CrossEntropy | None | 10 | 0.4820 | 0.9510 | 0.4120 | `models_store/baseline.pt` | Majority healthy bias; missed 5-acre disease zone |
| `run_focal_weighted` | 2026-11-18 | CNN3D v1 | Focal ($\gamma=2.0$) | Weighted Sampler + Weights | 15 | 0.8840 | 0.9680 | 0.8120 | `models_store/best_model.pt` | Strong pre-symptomatic red-edge detection |

---

## Log Entry Schema
Each experiment entry must record:
1. **Run ID**: Unique run folder identifier in `reports/runs/`.
2. **Architecture**: Model backbone (`cnn3d_v1`, `vit_spectral`, `hybrid_v1`).
3. **Loss Function**: `focal`, `weighted_ce`, `dice`.
4. **Imbalance Treatment**: Class weighting formula, `WeightedRandomSampler`, `ModelEMA`.
5. **Macro-F1 & mIoU**: Multiclass unweighted mean across all 3 crop disease states.
6. **Git Hash & Snapshot**: Preserved inside `reports/runs/<run_id>/metadata.json`.
