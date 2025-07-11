# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: [Driver] runs the main pipeline

# [PARALLEL]

# == sys path ==
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

import json
import os
from multiprocessing import Pool

from filelock import FileLock

from pipeline.pipes.load_image import LoadImagePipe
from pipeline.pipes.clahe_green import CLAHEGreenChannelPipe
from pipeline.pipes.lesion_masks import LesionMaskLoadingPipe
from pipeline.pipes.extract_patches import PatchExtractionPipe
from pipeline.pipes.label_patches import LabelPatchesPipe
from pipeline.pipes.save_patches import SavePatchesPipe

from pipeline.core import DRPipeline

from pipeline.utils.data_utils import load_and_prepare_metadata

from pipeline.config.settings import (BATCH_LOG_PATH, BATCH_SIZE,
                                      toggle_disable_tqdm)

from pipeline.utils.logger import get_logger

from tqdm.contrib.concurrent import process_map # to track progress

logger = get_logger(__name__, file_logging=True)

def load_log():
    # pre: BATCH_LOG_PATH exists and is valid
    # post: returns a dictionary with batch indices as keys and their status as values
    # desc: loads the batch log from a JSON file, if it exists

    if BATCH_LOG_PATH.exists():
        try:
            with open(BATCH_LOG_PATH, "r") as f:
                content = f.read().strip()
                return json.loads(content) if content else {}
        except json.JSONDecodeError:
            print("[WARN] Corrupted batch log (or) starting fresh")
            return {}
    return {}

def save_log(log):
    # pre: log is a dictionary with batch indices as keys and their status as values
    # post: writes the log to BATCH_LOG_PATH in JSON format
    # desc: saves the batch log to a JSON file
    try:
        lock_path = str(BATCH_LOG_PATH) + ".lock"
        BATCH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with FileLock(lock_path):
            with open(BATCH_LOG_PATH, "w") as f:
                json.dump(log, f, indent=2)
            logger.debug(f"Updated batch log: {BATCH_LOG_PATH}")
    except Exception as e:
        logger.error(f"[ERROR] Could not save batch log: {e}")

def run_pipeline_batch(batch_idx, batch_size=BATCH_SIZE):
    # pre: batch_idx is an integer representing the batch index
    #      batch_size is an integer representing the number of samples per batch
    #
    # post: processes the batch of data and updates the log
    # desc: runs the pipeline for a specific batch of data, skipping if already done

    log = load_log()
    if str(batch_idx) in log and log[str(batch_idx)] == "done":
        print(f"[SKIP] Batch {batch_idx} already complete")
        return

    print(f"[RUN] Batch {batch_idx}")

    all_data = load_and_prepare_metadata()
    start = batch_idx * batch_size
    end = start + batch_size
    batch_data = all_data[start:end]

    pipeline = DRPipeline(
        pipes=[
            LoadImagePipe(),
            CLAHEGreenChannelPipe(),
            LesionMaskLoadingPipe(),
            PatchExtractionPipe(),
            LabelPatchesPipe(),
            SavePatchesPipe(multiprocessing=True, batch_idx=batch_idx),
        ],
        batch_idx=batch_idx)

    try:
        _ = pipeline.run(batch_data)
        log[str(batch_idx)] = "done"

        save_log(log)
        print(f"[DONE] Batch {batch_idx}")
    except Exception as e:
        print(f"[ERROR] Batch {batch_idx} failed: {e}")

def run_pipeline_in_parallel(batch_size=BATCH_SIZE):
    # pre: batch_size is an integer representing the number of samples per batch
    # post: runs the pipeline in parallel across multiple batches
    # desc: divides the dataset into batches and processes each batch in parallel
    #       using the cpu_count/2 number of workers

    num_workers = os.cpu_count() // 2 # floor div by 2...use only half the cores

    all_data = load_and_prepare_metadata()
    num_batches = (len(all_data) + batch_size - 1) // batch_size
    batch_indices = list(range(num_batches))

    process_map(run_pipeline_batch, batch_indices, max_workers=num_workers)

if __name__ == "__main__":
    toggle_disable_tqdm(True) # just to make sure it's on/off
    run_pipeline_in_parallel()
