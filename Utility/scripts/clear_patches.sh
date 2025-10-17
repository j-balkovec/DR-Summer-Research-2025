#!/bin/bash

PATCH_PATH="/Users/jbalkovec/Desktop/DR/data/patches"
BATCH_LOG="/Users/jbalkovec/Desktop/DR/pipeline/logs/batch_log.json"
PIPELINE_LOG="/Users/jbalkovec/Desktop/DR/pipeline/logs/pipeline.log"

echo "[INFO] Navigating to patches directory: $PATCH_PATH"
cd "$PATCH_PATH" || { echo "[ERROR] Failed to navigate to $PATCH_PATH"; exit 1; }

echo "[INFO] Deleting all contents in: $PATCH_PATH"
/bin/rm -rf *

echo "[DONE] All patch files and directories have been removed."

echo "[INFO] Clearing batch log: $BATCH_LOG"
> "$BATCH_LOG"
echo "[DONE] Batch log has been cleared."

echo "[INFO] Clearing pipeline log: $PIPELINE_LOG"
> "$PIPELINE_LOG"
echo "[DONE] Pipeline log has been cleared."
