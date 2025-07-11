# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: extracts fixed-size patches centered around lesion polygons, with optional size enforcement

# == sys path ==
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

from pipeline.utils.geometry_utils import polygon_from_mask, patch_center_to_polygon
from pipeline.config.settings import (PATCH_HALF,
                                      EXTRACT_ALL_PATCHES,
                                      LOG_ALL)
from pipeline.utils.logger import get_logger

logger = get_logger(__name__, file_logging=True)

class PatchExtractionPipe:
    # brief: extracts lesion-centered patches from enhanced green image

    def process(self, data: dict) -> dict:
        # pre: data must contain "masks" and "enhanced_green" keys
        # post: data will contain the key "patches", a list of dicts with patch arrays and metadata
        # desc: iterates over lesion masks, extracts centered patches

        patches = []
        patch_counter = 1
        image = data["enhanced_green"]
        masks = data["masks"]
        height, width = image.shape

        for lesion_type, mask in masks.items():
            if mask is None:
                continue

            polygons = polygon_from_mask(mask)
            for poly in polygons:
                if not poly.is_valid:
                    continue

                minx, miny, maxx, maxy = poly.bounds
                cx, cy = int((minx + maxx) / 2), int((miny + maxy) / 2)

                x_start, x_end = cx - PATCH_HALF, cx + PATCH_HALF
                y_start, y_end = cy - PATCH_HALF, cy + PATCH_HALF

                x_start = max(0, x_start)
                y_start = max(0, y_start)
                x_end = min(width, x_end)
                y_end = min(height, y_end)

                patch = image[y_start:y_end, x_start:x_end]
                patch_poly = patch_center_to_polygon(cx, cy, PATCH_HALF)

                patches.append({
                    "patch": patch,
                    "patch_no": int(patch_counter),
                    "x": cx,
                    "y": cy,
                    "patch_polygon": patch_poly
                })
                patch_counter += 1

        # convert masks again to extract healthy patches against all lesion polygons
        lesion_polygons = {
            lesion_type: polygon_from_mask(mask)
            for lesion_type, mask in masks.items()
            if mask is not None
        }

        # optionally extract healthy patches (added into the patch stream)
        if EXTRACT_ALL_PATCHES:
            for y in range(PATCH_HALF, height - PATCH_HALF, 2 * PATCH_HALF):
                for x in range(PATCH_HALF, width - PATCH_HALF, 2 * PATCH_HALF):
                    patch_poly = patch_center_to_polygon(x, y, PATCH_HALF)
                    if not any(poly.intersects(patch_poly) for polys in lesion_polygons.values() for poly in polys):
                        patch = image[y - PATCH_HALF:y + PATCH_HALF, x - PATCH_HALF:x + PATCH_HALF]
                        patches.append({
                            "patch": patch,
                            "patch_no": int(patch_counter),
                            "x": x,
                            "y": y,
                            "patch_polygon": patch_poly
                        })
                        patch_counter += 1

            logger.info("added healthy patches during main loop") if LOG_ALL else None

        data["patches"] = patches
        logger.info(f"extracted {len(patches)} total patches") if LOG_ALL else None
        return data
