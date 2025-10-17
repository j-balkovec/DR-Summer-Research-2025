# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: loads fundus images from disk and prepares them for processing

# == sys path ==
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

from pipeline.utils.io_utils import read_image
from pipeline.utils.logger import get_logger

from pipeline.config.settings import LOG_ALL

logger = get_logger(__name__, file_logging=True)

class LoadImagePipe:
    # brief: loads fundus images from disk and prepares them for processing

    def process(self, data: dict) -> dict:
        # pre: data must contain the key "image_path" with a valid image file path
        # post: data will contain the key "image" with the loaded image
        # desc: this method reads an image from the disk using the path provided in the data dictionary

        image_path = data.get("image_path")

        msg = 'assertion error in [LoadImagePipe | process(...)] >> image_path not found'
        assert image_path is not None and Path(image_path).exists(), msg

        logger.info(f"loading image: {image_path}") if LOG_ALL else None
        image = read_image(Path(image_path))

        data["image"] = image
        return data
