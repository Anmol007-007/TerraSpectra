# 06 — ML Specification
## Input
PCA-reduced patches: tensor `[N, 1, D=32, H=11, W=11]` (channel=1, depth=spectral PCs, spatial 11×11). Optional raw path: D=~180 valid bands.
## Architecture: HybridCNNViT
1. **3D-CNN stem**: Conv3d(1→16,k=(3,3,3)) → BN → GELU; ResBlock3D(16→32,stride=(1,1,1)); ResBlock3D(32→64,stride=(2,1,1)) with SE spectral attention. Output `[N,64,D',H',W']`.
2. **Feature adapter**: average over (H',W') (or keep centre) → `[N,64,D']` → group spectral slices into tokens of size g → `[N,T,64*g]` → Linear → `d_model=128`.
3. **SpectralViT**: CLS token + wavelength-aware positional embedding; 4 pre-norm blocks, 4 heads, MLP ratio 4, dropout 0.1, stochastic depth 0.1.
4. **Heads** (on CLS): state (3 classes), severity (sigmoid), forecast days-to-symptoms (softplus, + horizon logits for 7/14/21).
5. **Temporal extension (Day 14)**: sequence of K=4 acquisitions → per-date embeddings → temporal Transformer/GRU → forecast head.
Parameter budget ~1–3M. Must run on 8 GB GPU with batch 128 under AMP; CPU fallback supported.
## Losses
`L = L_state(focal γ=2, class weights) + 0.5·L_sev(SmoothL1) + 0.5·L_forecast(BCE horizons + Huber days)`; optional uncertainty weighting.
## Metrics
Per-class precision/recall/F1, macro-F1, mIoU, confusion matrix, ROC-AUC/PR-AUC (stressed vs healthy), forecast lead-time (days), zone-level precision/recall, false-alarm rate, ECE.
## Training defaults
AdamW lr 3e-4 wd 1e-2, cosine + 5% warmup, 60 epochs, batch 128, AMP (bf16/fp16), grad clip 1.0, EMA 0.999, early stop patience 10 on val macro-F1, seed 42. Two-stage: CNN pretrain → hybrid finetune with layer-wise LR decay.
## Ablations (Day 13)
cnn-only · vit-only · hybrid · PCA 16/32/64 · patch 7/11/15 · band-group size. Save table to `reports/ablation.md`.
## Explainability
Attention rollout → wavelength importance plot; 3D Grad-CAM on spectral axis.
## Calibration
Temperature scaling, reliability diagram, MC-dropout uncertainty map.
## Export
`state_dict` + `model_card.md` + `config.yaml` + `version.txt`; optional TorchScript/ONNX.
