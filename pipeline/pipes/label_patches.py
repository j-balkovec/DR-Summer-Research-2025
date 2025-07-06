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

from pipeline.config.settings import (PATCH_HALF,
                                      LOG_ALL)

from pipeline.utils.logger import get_logger

from pipeline.utils.geometry_utils import (polygon_from_mask,
                                           patch_center_to_polygon)

logger = get_logger(__name__, file_logging=True)

class LabelPatchesPipe:
    # brief: labels patches by dominant intersection area with lesion polygons

    def process(self, data: dict) -> dict:
        # pre: data must contain "patches" and "masks"
        # post: each patch will contain "label", "lesion_shape", and "overlap_flag"
        # desc: assigns lesion labels based on the largest area of intersection with each patch

        masks = data.get("masks", {})
        patches = data.get("patches", [])

        # binary masks to polygons
        lesion_polygons = {
            lesion_type: polygon_from_mask(mask)
            for lesion_type, mask in masks.items()
            if mask is not None
        }

        for patch in patches:
            if patch["lesion_type"] == "healthy":
                patch["label"] = "healthy"
                patch["lesion_shape"] = None
                patch["overlap_flag"] = False
            else:
                cx, cy = patch["x"], patch["y"]
                patch_poly = patch_center_to_polygon(cx, cy, PATCH_HALF)

                area_map = {}
                lesion_shapes = {}

                for lesion_type, polygons in lesion_polygons.items():
                    for poly in polygons:
                        if poly.is_valid and poly.intersects(patch_poly):
                            inter = patch_poly.intersection(poly)
                            area = inter.area
                            if area > 0:
                                area_map[lesion_type] = area_map.get(lesion_type, 0) + area
                                lesion_shapes.setdefault(lesion_type, []).append(inter)

                if area_map:
                    dominant_lesion = max(area_map.items(), key=lambda x: x[1])[0]
                    patch["label"] = dominant_lesion
                    patch["lesion_shape"] = lesion_shapes[dominant_lesion]
                    patch["overlap_flag"] = False
                else:
                    patch["label"] = "healthy"
                    patch["lesion_shape"] = None
                    patch["overlap_flag"] = False

            patch["image_id"] = Path(data["image_path"]).stem
            patch["file_name"] = f"{patch['image_id']}_{patch['label']}_{patch['x']}_{patch['y']}.png"

        logger.info(f"labeled {len(patches)} patches using area-based method") if LOG_ALL else None
        return data
