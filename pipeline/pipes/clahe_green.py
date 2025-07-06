# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: Applies CLAHE enhancement to the green channel of fundus images to improve lesion contrast

# == sys path ==
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

from pipeline.utils.image_utils import extract_green_channel, apply_clahe
from pipeline.utils.logger import get_logger
from pipeline.config.settings import LOG_ALL

logger = get_logger(__name__, file_logging=True)

class CLAHEGreenChannelPipe:
    # brief: applies CLAHE enhancement to the green channel of fundus images

    def process(self, data: dict) -> dict:
        # pre: data must contain the key "image" as a 3-channel RGB image
        # post: data will contain the key "enhanced_green" as a 2D numpy array
        # desc: extracts green channel and applies CLAHE for better lesion visibility

        logger.info("extracting green channel") if LOG_ALL else None
        green = extract_green_channel(data["image"])

        logger.info("applying CLAHE") if LOG_ALL else None
        enhanced = apply_clahe(green)

        data["enhanced_green"] = enhanced
        return data
