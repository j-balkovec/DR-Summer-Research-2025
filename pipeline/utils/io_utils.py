# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: provides utility functions for reading and writing images, masks, and metadata files.

from pathlib import Path

import cv2

import numpy as np
import pandas as pd

def read_image(image_path: Path) -> np.ndarray:
    # pre: the path needs to be valid, and point to an image
    # post: np array representing the image
    # desc: reads in the image, returns a numpy array representing the image

    image = cv2.imread(str(image_path))
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def read_csv_image_paths(csv_path: Path) -> list:
    # pre: csv_path is a valid CSV with [filename, grade] columns; image_dir is where images are stored
    # post: returns a list of dicts with image_path, image_id, and grade
    # desc: parses the CSV and constructs full image paths and metadata
    # note: FMT = {"image_path": Path, "image_id": str, "grade": int}
    #             image_path is the full path to the image file (e.g just "0000_1.png")

    df = pd.read_csv(csv_path, header=None, names=["filename", "grade"])

    return [
        {
            "image_path": row["filename"],
            "image_id": Path(row["filename"]).stem,
            "grade": int(row["grade"])
        }
        for _, row in df.iterrows()
    ]

def save_image(image: np.ndarray, path: Path) -> None:
    # pre: the image is a numpy array and the path is valid
    # post: the image is saved to the path
    # desc: saves the image to the specified path in RGB format

    # note: can be used to save masks and patches as well [intermediate] (same format)
    #       patch saving is handled in the save_patches pipe

    bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(path), bgr_image)

def save_green_image(image: np.ndarray, path: Path) -> None:
    # pre: image is a 2D numpy array (green channel)
    # post: saves the image in grayscale format
    # desc: saves a single-channel image, e.g., the CLAHE-processed green channel

    cv2.imwrite(str(path), image)

def list_images(directory: Path, suffixes=(".png")):
    # pre: directory is a valid path
    # post: a list of image files in the directory with specified suffixes
    # desc: lists all image files in the directory with the specified suffixes

    return [p for p in directory.iterdir() if p.suffix.lower() in suffixes]

def ensure_dir(path: Path):
    # pre: path is a valid Path object
    # post: the directory at the path exists
    # desc: ensures that the directory at the specified path exists, creating it if necessary

    # note: this is useful for creating directories before saving files
    path.mkdir(parents=True, exist_ok=True)

def tqdm_if_verbose(iterable, desc=None, disable=False, **kwargs):
    # note: for multiprocessing
    # pre: iterable is an iterable object
    # post: returns a tqdm iterator if not disabled, otherwise returns the iterable
    # desc: adds a progress bar to the iterable if not disabled

    from tqdm import tqdm
    return tqdm(iterable, desc=desc, **kwargs) if not disable else iterable
