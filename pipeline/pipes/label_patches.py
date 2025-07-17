# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: labels the patches with lesion type and coordinates based on the binary mask and lesion location.
#        multiple labels are resolved using the area approach here

# == sys path ==
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

import numpy as np

from pipeline.config.settings import (PATCH_SIZE, LOG_ALL, LESION_LABELS)
from pipeline.utils.logger import get_logger

logger = get_logger(__name__, file_logging=True)

# !important! NOTE:
#       this part of the pipeline filters out the patches that are completely black
#       (e.g. if the patch is completely black, it will be labeled as "black"). This is so that
#       we do not save empty patches (meaningless data...)

class LabelPatchesPipe:
    # brief: labels patches by dominant intersection area with lesion polygons

    def process(self, data: dict) -> dict:
        # pre: data must contain "patches" and "masks"
        # post: each patch will contain "label_vector" with binary labels for each lesion type
        # desc: assigns label vector based on lesion mask presence in the patch crop

        masks = data.get("masks", {})
        patches = data.get("patches", [])
        image_id = Path(data["image_path"]).stem

        for patch in patches:
            cx, cy = patch["x"], patch["y"]
            label_vector = []

            for lesion_type in LESION_LABELS:
                mask = masks.get(lesion_type)

                if mask is None:
                    logger.warning(f"mask not found {image_id}, {lesion_type}")
                    label_vector.append(0)
                    continue

                y0, y1 = cy - PATCH_SIZE // 2, cy + PATCH_SIZE // 2
                x0, x1 = cx - PATCH_SIZE // 2, cx + PATCH_SIZE // 2
                lesion_crop = mask[y0:y1, x0:x1]
                label = int(np.any(lesion_crop > 0))
                label_vector.append(label)

            patch["label_vector"] = label_vector

            if patch["filter_tag"] != "black":
                patch["filter_tag"] = (
                    "healthy" if label_vector == [0, 0, 0, 0] else "lesion"
                )

            lesion_suffix = "_".join([
                lesion for lesion, present in zip(LESION_LABELS, label_vector) if present
            ]) or "healthy"

            patch["image_id"] = image_id
            patch["file_name"] = f"{image_id}_{lesion_suffix}_{cx}_{cy}.png"

        logger.info(f"labeled {len(patches)} patches for image {image_id}") if LOG_ALL else None
        return data


    # =============================================================
    # Deprecated: Area-Based Single-Label Patch Labeling (for legacy reference only)
    # Jakob Balkovec | DR-Pipeline
    # =============================================================

    def _deprecated_process(self, data: dict) -> dict:
        # -- DEPRECATED --
        # Previous approach that assigned a single label to each patch
        # based on the largest intersecting lesion area.
        #
        # Retained for historical reference. Use process() instead.

        # pre: data must contain "patches" and "masks"
        # post: each patch will contain "label", "lesion_shape", and "overlap_flag"
        # desc: assigns lesion labels based on the largest area of intersection with each patch

        raise DeprecationWarning("This method is deprecated and should not be used.")

        # Uncomment below if reactivation is needed:

        # masks = data.get("masks", {})
        # patches = data.get("patches", [])

        # # binary masks to polygons
        # lesion_polygons = {
        #     lesion_type: polygon_from_mask(mask)
        #     for lesion_type, mask in masks.items()
        #     if mask is not None
        # }

        # for patch in patches:
        #     if patch["lesion_type"] == "healthy":
        #         patch_img = patch.get("patch")
        #         if patch_img is None:
        #             raise ValueError(f"patch image is \'None\' for patch ({patch['x']}, {patch['y']}) with id: {[patch['patch_no']]}, image_id: {patch['image_id']}")

        #         black_pixels = count_black_pixels(patch_img)

        #         if black_pixels >= BLACK_PIXELS_THRESHOLD:
        #             patch["label"] = "black"
        #         else:
        #             patch["label"] = "healthy"

        #         patch["lesion_shape"] = None
        #         patch["overlap_flag"] = False
        #     else:
        #         cx, cy = patch["x"], patch["y"]
        #         patch_poly = patch_center_to_polygon(cx, cy, PATCH_HALF)

        #         area_map = {}
        #         lesion_shapes = {}

        #         for lesion_type, polygons in lesion_polygons.items():
        #             for poly in polygons:
        #                 if poly.is_valid and poly.intersects(patch_poly):
        #                     inter = patch_poly.intersection(poly)
        #                     area = inter.area
        #                     if area > 0:
        #                         area_map[lesion_type] = area_map.get(lesion_type, 0) + area
        #                         lesion_shapes.setdefault(lesion_type, []).append(inter)

        #         if area_map:
        #             dominant_lesion = max(area_map.items(), key=lambda x: x[1])[0]
        #             patch["label"] = dominant_lesion
        #             patch["lesion_shape"] = lesion_shapes[dominant_lesion]
        #             patch["overlap_flag"] = False
        #         else:
        #             patch["label"] = "healthy"
        #             patch["lesion_shape"] = None
        #             patch["overlap_flag"] = False

        #     patch["image_id"] = Path(data["image_path"]).stem
        #     patch["file_name"] = f"{patch['image_id']}_{patch['label']}_{patch['x']}_{patch['y']}.png"

        # logger.info(f"labeled {len(patches)} patches using area-based method") if LOG_ALL else None
        # return data
