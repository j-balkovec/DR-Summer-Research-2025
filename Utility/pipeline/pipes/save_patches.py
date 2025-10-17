# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: saves extracted patches to disk using structured naming

# == sys path ==
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

import pandas as pd

from pipeline.config.settings import LOG_ALL, PATCH_OUTPUT_DIR
from pipeline.utils.logger import get_logger
from pipeline.utils.io_utils import ensure_dir

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

    def process(self, data: dict) -> dict:
        # pre: data["patches"] must contain all patch metadata (file already saved)
        # post: Pickle DataFrame is written to disk
        # desc: constructs and saves patch metadata for downstream indexing/training

        patches = data["patches"]
        image_id = patches[0]["image_id"] if patches else "unknown"

        metadata = []

        for patch in patches:
            metadata.append({
                "image_id": patch["image_id"],
                "patch_id": patch["patch_id"],
                "file_path": patch["file_path"],
                "filter_tag": patch["filter_tag"],
                "coordinates": patch["coordinates"],
                "center": {"x": patch["x"], "y": patch["y"]},
                "label_vector": patch["label_vector"]
            })

        # -> save to /patches/{image_id}/frame/patch_frame.pkl
        frame_dir = Path(PATCH_OUTPUT_DIR) / image_id / "frame"
        ensure_dir(frame_dir)
        df_out_path = frame_dir / "patch_frame.pkl"

        df = pd.DataFrame(metadata)
        df.to_pickle(df_out_path)

        logger.info(f"saved metadata for {len(patches)} patches to {df_out_path}") if LOG_ALL else None
        return data
