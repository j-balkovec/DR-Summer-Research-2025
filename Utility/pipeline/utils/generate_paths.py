# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 13th 2025

# brief: builds a CSV index of image patches

# == sys path ==
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

import os
import csv

from pipeline.config.settings import PATCH_OUTPUT_DIR, MASTER_PATHS_CSV_PATH

def generate_paths():
    # pre: PATCH_OUTPUT_DIR contains subdirectories with patch images
    # post: creates a CSV file with image names and their relative paths
    # desc: walks through the PATCH_OUTPUT_DIR, collects all .png files, and writes
    #       their names and relative paths to a CSV file for easy access

    image_data = []

    for root, _, files in os.walk(PATCH_OUTPUT_DIR):
        for file in files:
            if file.lower().endswith('.png'):
                full_path = os.path.join(root, file).replace("\\", "/")
                rel_path = full_path[full_path.index('patches/'):]
                image_data.append((file, rel_path))

    image_data.sort(key=lambda x: x[0])  # sort by image_name

    with open(MASTER_PATHS_CSV_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['image_name', 'relative_path'])
        writer.writerows(image_data)

    return len(image_data)

if __name__ == "__main__":
    print("[INFO] Generating paths CSV for image patches...")
    len=generate_paths()
    print("[DONE] Paths CSV generation complete.")
    print(f"CSV saved at: {MASTER_PATHS_CSV_PATH}")
    print(f"Total images indexed: {len}")
