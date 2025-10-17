# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: loads pixel-level lesion masks (microaneurysms, hemorrhages, exudates, etc.) for annotation

# == sys path ==
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

from pipeline.utils.io_utils import read_image
from pipeline.utils.logger import get_logger
from pipeline.config.settings import MASK_ROOT, LESION_MASKS, LOG_ALL

logger = get_logger(__name__, file_logging=True)

class LesionMaskLoadingPipe:
    # brief: loads lesion masks for each predefined lesion type

    def process(self, data: dict) -> dict:
        # pre: data must contain the key "image_path" pointing to the RGB image file
        # post: data will contain the key "masks", a dict of lesion_type -> binary mask (or None if missing)
        # desc: attempts to load binary masks for all defined lesion types and stores them in a dictionary

        image_name = Path(data["image_path"]).stem
        masks = {}

        for lesion, folder in LESION_MASKS.items():
            mask_path = MASK_ROOT / folder / f"{image_name}.png"

            if mask_path.exists():
                logger.info(f"loading {lesion} mask for: {image_name}") if LOG_ALL else None

                # note: lesion masks are stored as RGB images with binary data in the red channel (channel 0);
                #       green and blue channels are unused (all zeros)
                masks[lesion] = read_image(mask_path)[:, :, 0]
            else:
                logger.info(f"{lesion} mask not found for: {image_name}") if LOG_ALL else None
                masks[lesion] = None

        data["masks"] = masks
        return data
