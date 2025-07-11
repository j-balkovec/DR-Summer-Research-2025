# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: saves extracted patches to disk using structured naming

# == sys path ==
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

import random
from collections import defaultdict

import pandas as pd # for csv
import numpy as np

from pipeline.config.settings import (PATCH_OUTPUT_DIR,
                                      LOG_ALL,
                                      PATCHES_CSV,
                                      HEALTHY_PATCHES_LIMIT,
                                      HEALTHY_PATCHES_LIMIT_MP,
                                      SHARD_DIR_LIMIT)

from pipeline.utils.logger import get_logger
from pipeline.utils.io_utils import save_image, ensure_dir
from pipeline.utils.image_utils import is_mostly_black

logger = get_logger(__name__, file_logging=True)

# !important! NOTE:
#       this part of the pipeline filters out the patches that are mostly black.
#       for example, if 95% of the patch is black, it will not be saved.
#       this is to avoid saving empty patches that do not contain any useful information
#       the THRESHOLD and BLACK_RATIO constants can and will be be adjusted in settings.py
# !another! note:
#       the logic is kinda weird (i know), but i know what i'm doing...(i think)

class SavePatchesPipe:
    # brief: saves patches to disk in directories organized by lesion type
    def __init__(self, multiprocessing=False, batch_idx=None):
        # pre: initializes the SavePatchesPipe
        # post: sets the multiprocessing flag, and optionally the batch index
        # desc: initializes the SavePatchesPipe with an optional multiprocessing flag and batch index
        self.multiprocessing = multiprocessing
        self.batch_idx = batch_idx

    def process(self, data: dict) -> dict:
        # pre: data must contain "patches", each with "label", "patch", and "file_name"
        # post: each patch is saved to PATCH_OUTPUT_DIR/<label>/<file_name>.png
        # desc: organizes saved patches into lesion-specific folders

        patches = data.get("patches", [])

        saved_counts = defaultdict(int)
        shard_counts = defaultdict(int)
        shard_dirs = defaultdict(lambda: 1)
        healthy_pool = []

        def get_shard_dir(label):
            # pre: label must be a valid (lesion) type
            # post: the directory path for saving patches of the given label
            # desc: gets the shard directory for the given label, creating it if necessary

            base_dir = PATCH_OUTPUT_DIR / label
            ensure_dir(base_dir)

            while True:
                shard_id = shard_dirs[label]
                dir_path = base_dir / f"{label}_{shard_id}"
                ensure_dir(dir_path)

                current_file_count = len(list(dir_path.glob("*.png")))
                if current_file_count < SHARD_DIR_LIMIT:
                    return dir_path

                shard_dirs[label] += 1

        def save_patch(patch_dict):
            # pre: patch_dict must contain "label", "patch", and "file_name"
            # post: saves the patch image to the appropriate shard directory
            # desc: saves the patch image to the correct directory based on its label

            # switched to dynamic labeling instead of dict lookups -> due to vector approach (multi-label)
            label = "_".join([lt for lt, val in patch["label_vector"].items() if val == 1]) or "healthy"
            patch_img = patch_dict["patch"]
            file_name = patch_dict["file_name"]

            shard_dir = get_shard_dir(label)
            save_path = shard_dir / file_name
            save_image(patch_img, save_path)

            saved_counts[label] += 1

            if LOG_ALL:
                logger.info(f"saved patch to {save_path}")

        final_patches = []
        black_pool = []

        for patch in patches:
            label = patch["label"]

            if label == "healthy":
                if not is_mostly_black(patch["patch"]):
                    healthy_pool.append(patch)
            elif label == "black":
                black_pool.append(patch)
            else:
                save_patch(patch)
                final_patches.append(patch)

        patches_limit = HEALTHY_PATCHES_LIMIT_MP if self.multiprocessing else HEALTHY_PATCHES_LIMIT

        random.shuffle(healthy_pool)
        for patch in healthy_pool[:patches_limit]:
            save_patch(patch)
            final_patches.append(patch)

        random.shuffle(black_pool)
        for patch in black_pool[:patches_limit]:
            save_patch(patch)
            final_patches.append(patch)

        # add option to filter out the ones where label = "black"
        csv_records = [
            {
                "image_id": patch["image_id"],
                "x": patch["x"],
                "y": patch["y"],
                "label": patch["label"],
                "file_name": patch["file_name"]
            }
            for patch in final_patches
        ]

        batch_csv_path = PATCHES_CSV.parent / f"patches_batch_{self.batch_idx}.csv" if self.batch_idx is not None else PATCHES_CSV
        ensure_dir(batch_csv_path.parent)
        pd.DataFrame(csv_records).to_csv(batch_csv_path, index=False)

        if LOG_ALL:
            logger.info(f"saved patch metadata CSV to {batch_csv_path}")

        return data
