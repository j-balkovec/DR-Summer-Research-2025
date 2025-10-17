# Jakob Balkovec
# DR-Pipeline
#   Updated: Mon Aug 25 2025
#
# brief: lesion-centered patch extraction + healthy sampling to hit ~60/40 ratio
#        writes to .../patches/<image_id>/all and returns patch dicts expected by SavePatchesPipe

# == sys path ==
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

import os
import cv2
import math
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from pipeline.config.settings import (
    PATCH_SIZE, LOG_ALL, PATCH_BLACK_THRESHOLD, BLACK_RATIO, BLACK_PIXELS_THRESHOLD,
    PATCH_OUTPUT_DIR, HEALTHY_TO_LESION_RATIO, LESION_DILATE_PX, SEED, LESION_LABELS
)

from pipeline.utils.geometry_utils import (get_patch_coordinates, _black_tag, _reflective_crop,
                                           _ensure_uint8, _connected_component_centroids, _dilate,
                                           _random_point_in_mask, _make_label_vector, crop_128_no_pad)
from pipeline.utils.logger import get_logger
from pipeline.utils.io_utils import ensure_dir
from pipeline.utils.image_utils import is_mostly_black

logger = get_logger(__name__, file_logging=True)

class PatchExtractionPipe:
    # brief: lesion-centered patch extraction + healthy sampling (~60/40).
    # inputs: data["image"] (RGB), data["image_id"], data["masks"] (dict[str]->mask or None)
    # outputs: data["patches"] list of dicts expected by SavePatchesPipe (includes label_vector)
    # writes: PNGs under PATCH_OUTPUT_DIR/<image_id>/all/

    def process(self, data: dict) -> dict:
        image: np.ndarray = data["image"]  # RGB
        image_id: str = data.get("image_id", Path(data["image_path"]).stem if "image_path" in data else "unknown")
        masks_in: Dict[str, Optional[np.ndarray]] = data.get("masks", {})

        masks: Dict[str, np.ndarray] = {}
        for cls, m in masks_in.items():
            m_bin = _ensure_uint8(m)
            if m_bin is not None and m_bin.any():
                masks[cls] = m_bin

        h, w, _ = image.shape
        np.random.seed(SEED)

        patch_dir = os.path.join(PATCH_OUTPUT_DIR, image_id, "all")
        ensure_dir(Path(patch_dir))

        patches: List[dict] = []
        patch_counter = 1

        lesion_kept = 0
        for cls_name, m in masks.items():
            comps = _connected_component_centroids(m)  # [(cx,cy,area)]
            for (cx, cy, area) in comps:
                success = False
                tries = 0

                while not success and tries < 10:
                    tries += 1
                    if tries == 1:
                        # first attempt = centroid
                        px, py = cx, cy
                    else:
                        # retry with random pixel inside this mask
                        ys, xs = np.where(m > 0)
                        idx = np.random.randint(0, len(xs))
                        px, py = xs[idx], ys[idx]

                    patch_rgb, bbox = crop_128_no_pad(image, px, py, PATCH_SIZE, max_shift=8)
                    if patch_rgb is None or is_mostly_black(patch_rgb):
                        continue  # try again

                    patch_coords = get_patch_coordinates(px, py, PATCH_SIZE)
                    patch_id = f"{image_id}_{str(px).zfill(4)}_{str(py).zfill(4)}"
                    file_name = f"{patch_id}.png"
                    file_path = os.path.join(patch_dir, file_name)
                    rel_path = os.path.relpath(file_path, PATCH_OUTPUT_DIR.parent)

                    cv2.imwrite(file_path, cv2.cvtColor(patch_rgb, cv2.COLOR_RGB2BGR))

                    patches.append({
                        "patch_no": int(patch_counter),
                        "image_id": image_id,
                        "patch_id": patch_id,
                        "file_name": file_name,
                        "file_path": rel_path,
                        "x": px,
                        "y": py,
                        "coordinates": patch_coords,
                        "filter_tag": "lesion",
                        "label_vector": _make_label_vector(cls_name),
                    })
                    patch_counter += 1
                    lesion_kept += 1
                    success = True

                if not success:
                    logger.warning(f"[skip] lesion component {cls_name} in {image_id} could not be patched after {tries} tries")

        n_healthy_target = int(math.ceil(HEALTHY_TO_LESION_RATIO * max(lesion_kept, 0)))

        union = np.zeros((h, w), dtype=np.uint8)
        for m in masks.values():
            union |= (m > 0).astype(np.uint8)
        keepout = _dilate(union, LESION_DILATE_PX)
        allowed = cv2.bitwise_not(keepout)

        healthy_kept = 0
        tries = 0
        max_tries = max(5000, 20 * max(1, n_healthy_target))

        while healthy_kept < n_healthy_target and tries < max_tries:
            tries += 1
            pt = _random_point_in_mask(allowed)
            if pt is None:
                break
            cx, cy = pt
            patch_rgb, bbox = _reflective_crop(image, cx, cy, PATCH_SIZE)
            if is_mostly_black(patch_rgb):
                continue  # skip and keep sampling

            center_x, center_y = cx, cy
            patch_coords = get_patch_coordinates(center_x, center_y, PATCH_SIZE)
            patch_id = f"{image_id}_{str(center_x).zfill(4)}_{str(center_y).zfill(4)}"
            file_name = f"{patch_id}.png"
            file_path = os.path.join(patch_dir, file_name)
            rel_path = os.path.relpath(file_path, PATCH_OUTPUT_DIR.parent)

            cv2.imwrite(file_path, cv2.cvtColor(patch_rgb, cv2.COLOR_RGB2BGR))

            patches.append({
                "patch_no": int(patch_counter),
                "image_id": image_id,
                "patch_id": patch_id,
                "file_name": file_name,
                "file_path": rel_path,
                "x": center_x,
                "y": center_y,
                "coordinates": patch_coords,
                "filter_tag": "healthy",
                "label_vector": _make_label_vector(None),
            })
            patch_counter += 1
            healthy_kept += 1

        data["patches"] = patches
        logger.info(f"[lesion-centered] {image_id}: lesion_kept={lesion_kept}  healthy_kept={healthy_kept}  total_saved={len(patches)}  tries={tries}")
        return data
