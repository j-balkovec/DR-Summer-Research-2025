# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: preps the data for the main pipeline

from pipeline.utils.io_utils import read_csv_image_paths
from pipeline.config.settings import IMAGE_DIR, CSV_PATH

def load_and_prepare_metadata(csv_path=CSV_PATH, image_dir=IMAGE_DIR):
    # pre: assumes CSV contains "image_path" column with filenames
    # post: returns a list of dicts with updated full image paths
    # brief: reads CSV metadata and attaches full image paths

    all_data = read_csv_image_paths(csv_path)
    for item in all_data:
        item["image_path"] = image_dir / item["image_path"]
    return all_data
