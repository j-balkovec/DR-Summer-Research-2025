# Jakob Balkovec
# DR-Pipeline (Visual Check Utility)
#   Updated: Jul 15, 2025

# brief: utility for visual checks of extracted patches with overlayed labels

# == sys path ==
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

import cv2
import numpy as np
import os

from pipeline.config.settings import (LESION_LABELS,
                                      VISUAL_CHECK_DIR,
                                      COLOR_MAP,
                                      LOG_ALL)

from pipeline.utils.logger import get_logger
from pipeline.utils.io_utils import ensure_dir

logger = get_logger(__name__, file_logging=True)

def visual_check(image, patches, image_id="unknown", show=False):
  # pre: provide RGB image and labeled patches with x/y/label_vector
  # post: saves annotated image to VISUAL_CHECK_DIR
  # desc: overlays label tags at patch centers with colored ticks + labels

    annotated = image.copy()

    for patch in patches:
        center = patch.get("center", {})
        x, y = center.get("x"), center.get("y")
        label_vector = patch["label_vector"]

        for idx, label in enumerate(label_vector):
            if label == 1:
                lesion = LESION_LABELS[idx]
                color = COLOR_MAP.get(lesion, (255, 255, 255))  # fallback = white

                coords = patch.get("coordinates", {})
                tl = coords.get("top-left")
                br = coords.get("bottom-right")

                if tl and br:               # rough estimate...rectangle
                    cv2.rectangle(annotated, tl, br, color, thickness=2)

                # tick
                cv2.drawMarker(annotated, (x, y), color, markerType=cv2.MARKER_TILTED_CROSS,
                               markerSize=15, thickness=2)

                # label
                cv2.putText(annotated, lesion, (x + 5, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)

    out_path = os.path.join(VISUAL_CHECK_DIR, f"{image_id}_vischeck.png")

    ensure_dir(VISUAL_CHECK_DIR)
    cv2.imwrite(out_path, cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))

    logger.info(f"saved visual check overlay to {out_path}") if LOG_ALL else None

    if show:
        cv2.imshow(f"Visual Check: {image_id}", cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
