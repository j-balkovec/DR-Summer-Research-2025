# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: saves extracted patches to disk using structured naming

# == sys path ==
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

from pipeline.config.settings import PATCH_OUTPUT_DIR, LOG_ALL, PATCHES_CSV
from pipeline.utils.logger import get_logger
from pipeline.utils.io_utils import save_image, ensure_dir

import pandas as pd # for csv

logger = get_logger(__name__, file_logging=True)

class SavePatchesPipe:
    # brief: saves patches to disk in directories organized by lesion type

    def process(self, data: dict) -> dict:
        # pre: data must contain "patches", each with "label", "patch", and "file_name"
        # post: each patch is saved to PATCH_OUTPUT_DIR/<label>/<file_name>.png
        # desc: organizes saved patches into lesion-specific folders

        patches = data.get("patches", [])

        for patch in patches:
            label = patch["label"]
            filename = patch["file_name"]
            patch_img = patch["patch"]

            save_dir = PATCH_OUTPUT_DIR / str(label)
            ensure_dir(save_dir)

            save_path = save_dir / filename
            save_image(patch_img, save_path)

            if LOG_ALL:
                logger.info(f"saved patch to {save_path}")

        csv_records = [
            {
                "image_id": patch["image_id"],
                "x": patch["x"],
                "y": patch["y"],
                "label": patch["label"],
                "file_name": patch["file_name"]
            }
            for patch in patches
        ]

        df = pd.DataFrame(csv_records)

        ensure_dir(PATCHES_CSV.parent)
        df.to_csv(PATCHES_CSV, index=False)

        if LOG_ALL:
            logger.info(f"saved patch metadata CSV to {PATCHES_CSV}")
        return data
