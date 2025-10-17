#!/bin/bash

CSV_DIR="/Users/jbalkovec/Desktop/DR/data/patches/csv"
PKL_DIR="/Users/jbalkovec/Desktop/DR/data/patches/frame"

MASTER_CSV="$CSV_DIR/master_patches.csv"
MASTER_PKL="$PKL_DIR/master_patches.pkl"

echo "[INFO] Merging CSV files into: $MASTER_CSV"
head -n 1 "$CSV_DIR/patches_batch_0.csv" > "$MASTER_CSV"  # Write header
tail -n +2 -q "$CSV_DIR"/patches_batch_*.csv >> "$MASTER_CSV"
echo "[DONE] CSV files merged."

PYTHON_BIN="/Users/jbalkovec/miniforge3/envs/dr-arm/bin/python"

echo "[INFO] Merging Pickle files into: $MASTER_PKL"
python - <<EOF
import pandas as pd
from pathlib import Path

pkl_dir = Path("$PKL_DIR")
out_path = pkl_dir / "master_patches.pkl"

frames = [pd.read_pickle(p) for p in sorted(pkl_dir.glob("patches_batch_*.pkl"))]
master_df = pd.concat(frames, ignore_index=True)
master_df.to_pickle(out_path)
print("[DONE] Pickle files merged.")
EOF
