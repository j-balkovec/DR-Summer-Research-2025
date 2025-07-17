# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: extracts fixed-size patches centered around lesion polygons, with optional size enforcement

# == sys path ==
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

import numpy as np
import os
import cv2

from pipeline.config.settings import (PATCH_SIZE, LOG_ALL, PATCH_BLACK_THRESHOLD,
                                      BLACK_RATIO, BLACK_PIXELS_THRESHOLD, PATCH_OUTPUT_DIR)
from pipeline.utils.geometry_utils import get_patch_coordinates
from pipeline.utils.logger import get_logger

from pipeline.utils.io_utils import ensure_dir

logger = get_logger(__name__, file_logging=True)

class PatchExtractionPipe:
    # brief: extracts patches from the RGB image, skipping edge cases and filtering by black pixel ratio

    def process(self, data: dict) -> dict:
        # pre: data must contain "enhanced_green" key
        # post: data will contain "patches" key with list of patch dicts
        # desc: extracts patches from the enhanced green image, skipping edge cases and filtering by black pixel ratio

        image = data["image"]
        image_id = data.get("image_id", "unknown")
        height, width, _ = image.shape
        patches = []
        patch_counter = 1

        patch_dir = os.path.join(PATCH_OUTPUT_DIR, image_id, "all")
        ensure_dir(Path(patch_dir))

        for y in range(0, height, PATCH_SIZE):
            for x in range(0, width, PATCH_SIZE):
                patch = image[y:y+PATCH_SIZE, x:x+PATCH_SIZE]

                if patch.shape[0] != PATCH_SIZE or patch.shape[1] != PATCH_SIZE:
                    continue  # skip incomplete edge patches

                gray_patch = np.mean(patch, axis=2)
                black_pixels = np.sum(gray_patch < PATCH_BLACK_THRESHOLD)
                black_ratio = black_pixels / (PATCH_SIZE * PATCH_SIZE)
                filter_tag = "healthy"

                if black_pixels >= BLACK_PIXELS_THRESHOLD and black_ratio >= BLACK_RATIO:
                    filter_tag = "black"

                center_x, center_y = x + PATCH_SIZE // 2, y + PATCH_SIZE // 2
                patch_coords = get_patch_coordinates(x, y, PATCH_SIZE)
                patch_id = f"{image_id}_{str(center_x).zfill(3)}_{str(center_y).zfill(3)}"
                file_name = f"{patch_id}.png"
                file_path = os.path.join(patch_dir, file_name)

                rel_path = os.path.relpath(file_path, PATCH_OUTPUT_DIR.parent) # goes in the DF

                if os.path.exists(file_path):
                    logger.warning(f"[dup] patch already exists: {file_path}")

                bgr_patch = cv2.cvtColor(patch, cv2.COLOR_RGB2BGR)
                cv2.imwrite(file_path, bgr_patch)

                patches.append({
                    "patch_no": int(patch_counter),
                    "image_id": image_id,
                    "patch_id": patch_id,
                    "file_name": file_name,
                    "file_path": rel_path,
                    "x": center_x,
                    "y": center_y,
                    "coordinates": patch_coords,
                    "filter_tag": filter_tag
                })
                patch_counter += 1

        data["patches"] = patches
        logger.info(f"Extracted + saved {len(patches)} patches for image {image_id}") if LOG_ALL else None
        return data
